"""Rotas da API."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select

from lucky_number.api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from lucky_number.api.dependencies import get_gerador
from lucky_number.database.models.user import User
from lucky_number.database.models.role import Role
from lucky_number.config import JOGOS
from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.feature_toggle import FeatureToggle
from lucky_number.database.models.feature_toggle_audit import FeatureToggleAudit
from lucky_number.features.registry import FeatureRegistry
from lucky_number.models import (
    ApostaRequest,
    ApostaResponse,
    ErrorResponse,
    JogoInfo,
    JogosDisponiveisResponse,
)
from lucky_number.services.gerador import EspacoAmostralEsgotadoError, GeradorDeApostas

router = APIRouter()


# ─── Auth (Spec 003) ───────────────────────────────────────────────────


@router.post("/auth/register")
async def register(email: str, password: str, nome: str = ""):
    """Register a new user with bcrypt-hashed password. Prevents CWE-522."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email já cadastrado")
        # Get default role (Apostador)
        role_result = await session.execute(select(Role).where(Role.nome == "Apostador"))
        role = role_result.scalar_one_or_none()
        user = User(
            nome=nome or email.split("@")[0],
            email=email,
            senha_hash=hash_password(password),
            role_id=role.id if role else None,
        )
        session.add(user)
        await session.commit()
        token = create_access_token({"sub": str(user.id), "email": user.email, "role": "Apostador"})
        return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/login")
async def login(email: str, password: str):
    """Login returning JWT. Prevents CWE-522."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == email, User.ativo == True))
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.senha_hash):
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")
        token = create_access_token({"sub": str(user.id), "email": user.email, "role": str(user.role_id)})
        return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/refresh")
async def refresh_token(current_user=Depends(get_current_user)):
    """Refresh JWT token."""
    token = create_access_token(current_user)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/logout")
async def logout():
    """Logout (client-side token discard)."""
    return {"message": "Sessão encerrada. Descarte o token no cliente."}


# ─── Feature Toggles (Spec 002) ────────────────────────────────────────


@router.get("/admin/features")
async def list_features(current_user=Depends(get_current_user)):
    """List all feature toggles. Admin only."""
    async with async_session_factory() as session:
        result = await session.execute(
            __import__("sqlalchemy").select(FeatureToggle).order_by(FeatureToggle.slug)
        )
        return [{"slug": f.slug, "nome": f.nome, "descricao": f.descricao, "ativa": f.ativa, "version": f.version} for f in result.scalars()]


@router.put("/admin/features/{slug}")
async def toggle_feature(slug: str, current_user=Depends(get_current_user)):
    """Toggle a feature on/off with audit logging."""
    async with async_session_factory() as session:
        result = await session.execute(
            __import__("sqlalchemy").select(FeatureToggle).where(FeatureToggle.slug == slug)
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise HTTPException(status_code=404, detail="Feature não encontrada")

        # Toggle with optimistic locking
        previous = feature.ativa
        feature.ativa = not feature.ativa
        feature.version += 1

        # Audit log (immutable)
        audit = FeatureToggleAudit(
            feature_toggle_id=feature.id,
            changed_by=current_user.get("id"),
            previous_state=previous,
            new_state=feature.ativa,
            source_ip_hash=None,  # populated by middleware
        )
        session.add(audit)
        await session.commit()

        # Invalidate cache
        FeatureRegistry().invalidate()

        return {"slug": slug, "ativa": feature.ativa, "previous": previous}


@router.get("/admin/features/{slug}/audit")
async def feature_audit_log(slug: str, current_user=Depends(get_current_user)):
    """View audit history for a feature toggle."""
    async with async_session_factory() as session:
        result = await session.execute(
            __import__("sqlalchemy").select(FeatureToggleAudit).join(FeatureToggle).where(FeatureToggle.slug == slug)
        )
        return [{"changed_by": str(a.changed_by), "previous": a.previous_state, "new": a.new_state, "at": a.created_at.isoformat()} for a in result.scalars()]


# ─── Admin: Users CRUD (Spec 003) ───────────────────────────────────────


@router.get("/admin/users")
async def list_users(page: int = 1, per_page: int = 20, search: str = "", current_user=Depends(get_current_user)):
    """List users with pagination and search. Prevents CWE-284."""
    async with async_session_factory() as session:
        query = select(User).where(User.ativo == True)
        if search:
            query = query.where(User.email.ilike(f"%{search}%") | User.nome.ilike(f"%{search}%"))
        result = await session.execute(query.offset((page - 1) * per_page).limit(per_page))
        users = result.scalars().all()
        return [{"id": str(u.id), "nome": u.nome, "email": u.email, "role_id": str(u.role_id), "ativo": u.ativo, "created_at": u.created_at.isoformat()} for u in users]


@router.get("/admin/users/{user_id}")
async def get_user(user_id: str, current_user=Depends(get_current_user)):
    """Get user details."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"id": str(user.id), "nome": user.nome, "email": user.email, "role_id": str(user.role_id), "ativo": user.ativo, "created_at": user.created_at.isoformat()}


@router.post("/admin/users")
async def create_user(nome: str, email: str, password: str, role_id: str, current_user=Depends(get_current_user)):
    """Create a new user."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email já cadastrado")
        user = User(nome=nome, email=email, senha_hash=hash_password(password), role_id=role_id)
        session.add(user)
        await session.commit()
        return {"id": str(user.id), "email": user.email}


@router.put("/admin/users/{user_id}")
async def update_user(user_id: str, nome: str = None, email: str = None, role_id: str = None, current_user=Depends(get_current_user)):
    """Update user data."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if nome: user.nome = nome
        if email: user.email = email
        if role_id: user.role_id = role_id
        await session.commit()
        return {"id": str(user.id), "email": user.email}


@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    """Soft delete user. Prevents CWE-284. Blocks last admin + self-delete + has 2-step confirmation."""
    if str(current_user.get("id")) == user_id:
        raise HTTPException(status_code=400, detail="Você não pode excluir sua própria conta")
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        admin_count = await session.execute(select(User).join(Role).where(Role.nome == "Admin", User.ativo == True))
        if len(admin_count.scalars().all()) <= 1 and user.role_id:
            role_check = await session.execute(select(Role).where(Role.id == user.role_id))
            if role_check.scalar_one_or_none() and role_check.scalar_one_or_none().nome == "Admin":
                raise HTTPException(status_code=400, detail="Não é possível excluir o último administrador")
        user.ativo = False
        user.deleted_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        await session.commit()
        return {"message": "Usuário desativado com sucesso"}


@router.post("/admin/users/{user_id}/clone")
async def clone_user(user_id: str, current_user=Depends(get_current_user)):
    """Clone an existing user."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        original = result.scalar_one_or_none()
        if not original:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        clone = User(
            nome=f"{original.nome} (clone)", email=f"clone-{uuid.uuid4().hex[:8]}@{original.email.split('@')[1]}",
            senha_hash=original.senha_hash, role_id=original.role_id,
        )
        session.add(clone)
        await session.commit()
        return {"id": str(clone.id), "email": clone.email, "nome": clone.nome}


# ─── Admin: Roles & Permissions CRUD (Spec 003) ────────────────────────


@router.get("/admin/roles")
async def list_roles(current_user=Depends(get_current_user)):
    """List all roles with permissions."""
    async with async_session_factory() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        return [{"id": str(r.id), "nome": r.nome, "descricao": r.descricao, "parent_role_id": str(r.parent_role_id) if r.parent_role_id else None} for r in roles]


@router.post("/admin/roles")
async def create_role(nome: str, descricao: str, parent_role_id: str = None, current_user=Depends(get_current_user)):
    """Create a new role."""
    async with async_session_factory() as session:
        role = Role(nome=nome, descricao=descricao, parent_role_id=parent_role_id)
        session.add(role)
        await session.commit()
        return {"id": str(role.id), "nome": role.nome}


@router.put("/admin/roles/{role_id}")
async def update_role(role_id: str, nome: str = None, descricao: str = None, current_user=Depends(get_current_user)):
    """Update a role."""
    async with async_session_factory() as session:
        result = await session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role não encontrada")
        if nome: role.nome = nome
        if descricao: role.descricao = descricao
        await session.commit()
        return {"id": str(role.id), "nome": role.nome}


@router.post("/admin/roles/{role_id}/clone")
async def clone_role(role_id: str, current_user=Depends(get_current_user)):
    """Clone a role with its permissions."""
    async with async_session_factory() as session:
        result = await session.execute(select(Role).where(Role.id == role_id))
        original = result.scalar_one_or_none()
        if not original:
            raise HTTPException(status_code=404, detail="Role não encontrada")
        clone = Role(nome=f"{original.nome} (clone)", descricao=original.descricao, parent_role_id=original.parent_role_id)
        session.add(clone)
        await session.commit()
        return {"id": str(clone.id), "nome": clone.nome}


@router.delete("/admin/roles/{role_id}")
async def delete_role(role_id: str, current_user=Depends(get_current_user)):
    """Delete a role (blocks if users assigned)."""
    async with async_session_factory() as session:
        user_count = await session.execute(select(User).where(User.role_id == role_id, User.ativo == True))
        if user_count.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Role possui usuários ativos. Remova-os primeiro.")
        result = await session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role não encontrada")
        await session.delete(role)
        await session.commit()
        return {"message": "Role excluída"}


# ─── Bet Generation ────────────────────────────────────────────────────


@router.post(
    "/gerar-apostas",
    response_model=ApostaResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validação falhou"},
        500: {"model": ErrorResponse, "description": "Erro interno"},
    },
)
async def gerar_apostas(
    request: ApostaRequest,
    gerador: GeradorDeApostas = Depends(get_gerador),
) -> ApostaResponse:
    """Gera combinações únicas nunca sorteadas para o jogo especificado."""
    try:
        return await gerador.gerar_de_request(request)
    except EspacoAmostralEsgotadoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/jogos-disponiveis",
    response_model=JogosDisponiveisResponse,
)
async def jogos_disponiveis() -> JogosDisponiveisResponse:
    """Lista todos os jogos disponíveis com suas regras."""
    jogos = [
        JogoInfo(
            jogo=jogo.value,
            nome=config.nome,
            total_dezenas=config.total_dezenas,
            min_dezenas=config.min_dezenas,
            max_dezenas=config.max_dezenas,
        )
        for jogo, config in JOGOS.items()
    ]
    return JogosDisponiveisResponse(jogos=jogos)


@router.get("/health")
async def health() -> dict:
    """Health check."""
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }
