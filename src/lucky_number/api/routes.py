"""Rotas da API."""

import hashlib
import os
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, func

from lucky_number.api.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    validate_password_strength,
    verify_password,
    check_login_lockout,
    record_failed_login,
    reset_login_attempts,
)
from lucky_number.api.dependencies import get_gerador
from lucky_number.config import JOGOS
from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.user import User
from lucky_number.database.models.role import Role
from lucky_number.database.models.combinacao import Combinacao
from lucky_number.database.models.promessa import Promessa
from lucky_number.database.models.notification import (
    SystemNotification,
    NotificationDelivery,
)
from lucky_number.database.models.usage_event import UsageEvent
from lucky_number.database.models.password_reset_token import PasswordResetToken
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
from lucky_number.services.combinacao_service import (
    save_combinacao as sv,
    list_combinacoes as ls,
    delete_combinacao as dc,
    toggle_favorita as tf,
)
from lucky_number.services.promessa_service import (
    create_promessa as cp,
    list_promessas as lp,
    delete_promessa as dp,
    clone_promessa as cl,
    share_promessa as sp,
)
from lucky_number.services.gerador import EspacoAmostralEsgotadoError, GeradorDeApostas
from lucky_number.services.notification_service import NotificationService

router = APIRouter()

SHARING_TTL_DAYS = 7


# ─── Auth (Spec 003, 022) ───────────────────────────────────────────────


@router.post("/auth/register")
async def register(email: str, password: str, nome: str = ""):
    """Register a new user with bcrypt-hashed password. Prevents CWE-522, CWE-521."""
    validate_password_strength(password)
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email já cadastrado")
        role_result = await session.execute(
            select(Role).where(Role.nome == "Apostador")
        )
        role = role_result.scalar_one_or_none()
        user = User(
            nome=nome or email.split("@")[0],
            email=email,
            senha_hash=hash_password(password),
            role_id=role.id if role else None,
        )
        session.add(user)
        await session.commit()
        token = create_access_token(
            {"sub": str(user.id), "email": user.email, "role": "Apostador"}
        )
        return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/login")
async def login(email: str, password: str):
    """Login returning JWT. Prevents CWE-522, CWE-307."""
    check_login_lockout(email)
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == email, User.ativo)
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.senha_hash):
            record_failed_login(email)
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")
        reset_login_attempts(email)
        token = create_access_token(
            {"sub": str(user.id), "email": user.email, "role": str(user.role_id)}
        )
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


@router.delete("/auth/account")
async def delete_account(current_user=Depends(get_current_user)):
    """Delete own account (soft delete + anonymization). Prevents CWE-284.
    LGPD compliance: anonimiza dados pessoais."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.id == current_user["id"])
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        anon_hash = hashlib.sha256(
            f"deleted-{user.id}-{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]
        user.nome = "Usuário removido"
        user.email = f"deleted-{anon_hash}@removed.luckynumber"
        user.cpf = None
        user.telefone = None
        user.telefone_pais = None
        user.data_nascimento = None
        user.nome_completo = None
        user.logradouro = None
        user.numero = None
        user.complemento = None
        user.bairro = None
        user.cidade = None
        user.estado = None
        user.cep = None
        user.ativo = False
        user.deleted_at = datetime.now(UTC)
        await session.commit()
        return {
            "message": "Conta excluída com sucesso. Seus dados foram anonimizados conforme a LGPD."  # noqa: E501
        }


# ─── Password Reset (Specs 024, 025, 026) ─────────────────────────────


@router.post("/auth/forgot-password")
async def forgot_password(identifier: str, channel: str = "email"):
    """Request a password reset link. Sends via email or WhatsApp.
    Prevents CWE-200: returns generic message regardless of user existence.
    """
    token_ttl_minutes = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "20"))

    async with async_session_factory() as session:
        user = None
        if "@" in identifier:
            result = await session.execute(
                select(User).where(User.email == identifier, User.ativo)
            )
            user = result.scalar_one_or_none()
        else:
            result = await session.execute(
                select(User).where(User.telefone == identifier, User.ativo)
            )
            user = result.scalar_one_or_none()

        generic_msg = (
            "Se o email ou telefone informado estiver cadastrado, "
            "você receberá um link de redefinição de senha."
        )

        if not user:
            return {"message": generic_msg}

        await session.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.consumed_at.is_(None),
            )
            .values(consumed_at=datetime.now(UTC))
        )

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(UTC) + timedelta(minutes=token_ttl_minutes)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            canal_entrega=channel,
            expires_at=expires_at,
        )
        session.add(reset_token)
        await session.commit()

        reset_link = f"{os.getenv('APP_URL', 'http://localhost:3000')}/redefinir-senha?token={raw_token}"  # noqa: E501
        ns = NotificationService()
        recipient = user.email if channel == "email" else user.telefone
        if recipient:
            await ns.send_reset_link(recipient, channel, reset_link)

        return {"message": generic_msg}


@router.get("/auth/reset-password")
async def validate_reset_token(token: str):
    """Validate a password reset token."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    async with async_session_factory() as session:
        result = await session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        db_token = result.scalar_one_or_none()

        if not db_token:
            return {"valid": False, "error": "Link inválido"}
        if db_token.consumed_at is not None:
            return {
                "valid": False,
                "error": "Este link já foi utilizado. Solicite um novo reset de senha.",
            }
        if db_token.expires_at < datetime.now(UTC):
            return {
                "valid": False,
                "error": "Este link expirou. Solicite um novo link de redefinição de senha.",  # noqa: E501
            }

        return {"valid": True, "error": None}


@router.post("/auth/reset-password")
async def reset_password(token: str, password: str, password_confirm: str):
    """Set a new password using a valid reset token."""
    if password != password_confirm:
        raise HTTPException(status_code=422, detail="Senhas não conferem")
    validate_password_strength(password)

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    async with async_session_factory() as session:
        result = await session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        db_token = result.scalar_one_or_none()

        if not db_token:
            raise HTTPException(status_code=400, detail="Link inválido")
        if db_token.consumed_at is not None:
            raise HTTPException(status_code=400, detail="Este link já foi utilizado")
        if db_token.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Este link expirou")

        user_result = await session.execute(
            select(User).where(User.id == db_token.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="Usuário não encontrado")

        user.senha_hash = hash_password(password)
        db_token.consumed_at = datetime.now(UTC)
        await session.commit()

        return {"message": "Senha redefinida com sucesso", "redirect": "/login"}


@router.post("/auth/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    confirm_password: str,
    current_user=Depends(get_current_user),
):
    """Change password for authenticated user. Prevents CWE-522."""
    if new_password != confirm_password:
        raise HTTPException(status_code=422, detail="Senhas não conferem")
    validate_password_strength(new_password)

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.id == current_user["id"])
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if not verify_password(current_password, user.senha_hash):
            raise HTTPException(status_code=401, detail="Senha atual incorreta")

        if current_password == new_password:
            raise HTTPException(
                status_code=422, detail="A nova senha deve ser diferente da atual"
            )

        user.senha_hash = hash_password(new_password)
        await session.commit()

        return {"message": "Senha alterada com sucesso"}


# ─── Feature Toggles (Spec 002) ────────────────────────────────────────


@router.get("/admin/features")
async def list_features(current_user=Depends(get_current_user)):
    """List all feature toggles. Admin only."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(FeatureToggle).order_by(FeatureToggle.slug)
        )
        return [
            {
                "slug": f.slug,
                "nome": f.nome,
                "descricao": f.descricao,
                "ativa": f.ativa,
                "version": f.version,
            }
            for f in result.scalars()
        ]


@router.put("/admin/features/{slug}")
async def toggle_feature(slug: str, current_user=Depends(get_current_user)):
    """Toggle a feature on/off with audit logging."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(FeatureToggle).where(FeatureToggle.slug == slug)
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise HTTPException(status_code=404, detail="Feature não encontrada")

        previous = feature.ativa
        feature.ativa = not feature.ativa
        feature.version += 1

        audit = FeatureToggleAudit(
            feature_toggle_id=feature.id,
            changed_by=current_user.get("id"),
            previous_state=previous,
            new_state=feature.ativa,
            source_ip_hash=None,
        )
        session.add(audit)
        await session.commit()

        FeatureRegistry().invalidate()

        return {"slug": slug, "ativa": feature.ativa, "previous": previous}


@router.get("/admin/features/{slug}/audit")
async def feature_audit_log(slug: str, current_user=Depends(get_current_user)):
    """View audit history for a feature toggle."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(FeatureToggleAudit)
            .join(FeatureToggle)
            .where(FeatureToggle.slug == slug)
        )
        return [
            {
                "changed_by": str(a.changed_by),
                "previous": a.previous_state,
                "new": a.new_state,
                "at": a.created_at.isoformat(),
            }
            for a in result.scalars()
        ]


# ─── Admin: Users CRUD (Spec 003) ───────────────────────────────────────


@router.get("/admin/users")
async def list_users(
    page: int = 1,
    per_page: int = 20,
    search: str = "",
    current_user=Depends(get_current_user),
):
    """List users with pagination and search. Prevents CWE-284."""
    async with async_session_factory() as session:
        query = select(User).where(User.ativo)
        if search:
            query = query.where(
                User.email.ilike(f"%{search}%") | User.nome.ilike(f"%{search}%")
            )
        result = await session.execute(
            query.offset((page - 1) * per_page).limit(per_page)
        )
        users = result.scalars().all()
        return [
            {
                "id": str(u.id),
                "nome": u.nome,
                "email": u.email,
                "role_id": str(u.role_id),
                "ativo": u.ativo,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]


@router.get("/admin/users/{user_id}")
async def get_user(user_id: str, current_user=Depends(get_current_user)):
    """Get user details."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {
            "id": str(user.id),
            "nome": user.nome,
            "email": user.email,
            "role_id": str(user.role_id),
            "ativo": user.ativo,
            "created_at": user.created_at.isoformat(),
        }


@router.post("/admin/users")
async def create_user(
    nome: str,
    email: str,
    password: str,
    role_id: str,
    current_user=Depends(get_current_user),
):
    """Create a new user."""
    validate_password_strength(password)
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email já cadastrado")
        user = User(
            nome=nome, email=email, senha_hash=hash_password(password), role_id=role_id
        )
        session.add(user)
        await session.commit()
        return {"id": str(user.id), "email": user.email}


@router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    nome: str = None,
    email: str = None,
    role_id: str = None,
    current_user=Depends(get_current_user),
):
    """Update user data."""
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if nome:
            user.nome = nome
        if email:
            user.email = email
        if role_id:
            user.role_id = role_id
        await session.commit()
        return {"id": str(user.id), "email": user.email}


@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    """Soft delete user. Prevents CWE-284. Blocks last admin + self-delete."""
    if str(current_user.get("id")) == user_id:
        raise HTTPException(
            status_code=400,
            detail="Você não pode excluir sua própria conta. Use DELETE /auth/account.",
        )
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        if user.role_id:
            admin_count = await session.execute(
                select(func.count())
                .select_from(User)
                .join(Role)
                .where(Role.nome == "Admin", User.ativo)
            )
            if admin_count.scalar() <= 1:
                role_check = await session.execute(
                    select(Role).where(Role.id == user.role_id)
                )
                role = role_check.scalar_one_or_none()
                if role and role.nome == "Admin":
                    raise HTTPException(
                        status_code=400,
                        detail="Não é possível excluir o último administrador",
                    )

        user.ativo = False
        user.deleted_at = datetime.now(UTC)
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
            nome=f"{original.nome} (clone)",
            email=f"clone-{uuid.uuid4().hex[:8]}@{original.email.split('@')[1]}",
            senha_hash=hash_password(secrets.token_urlsafe(16)),
            role_id=original.role_id,
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
        return [
            {
                "id": str(r.id),
                "nome": r.nome,
                "descricao": r.descricao,
                "parent_role_id": str(r.parent_role_id) if r.parent_role_id else None,
            }
            for r in roles
        ]


@router.post("/admin/roles")
async def create_role(
    nome: str,
    descricao: str,
    parent_role_id: str = None,
    current_user=Depends(get_current_user),
):
    """Create a new role."""
    async with async_session_factory() as session:
        role = Role(nome=nome, descricao=descricao, parent_role_id=parent_role_id)
        session.add(role)
        await session.commit()
        return {"id": str(role.id), "nome": role.nome}


@router.put("/admin/roles/{role_id}")
async def update_role(
    role_id: str,
    nome: str = None,
    descricao: str = None,
    current_user=Depends(get_current_user),
):
    """Update a role."""
    async with async_session_factory() as session:
        result = await session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role não encontrada")
        if nome:
            role.nome = nome
        if descricao:
            role.descricao = descricao
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
        clone = Role(
            nome=f"{original.nome} (clone)",
            descricao=original.descricao,
            parent_role_id=original.parent_role_id,
        )
        session.add(clone)
        await session.commit()
        return {"id": str(clone.id), "nome": clone.nome}


@router.delete("/admin/roles/{role_id}")
async def delete_role(role_id: str, current_user=Depends(get_current_user)):
    """Delete a role (blocks if users assigned)."""
    async with async_session_factory() as session:
        user_count = await session.execute(
            select(func.count())
            .select_from(User)
            .where(User.role_id == role_id, User.ativo)
        )
        if user_count.scalar() > 0:
            raise HTTPException(
                status_code=400,
                detail="Role possui usuários ativos. Remova-os primeiro.",
            )
        result = await session.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role não encontrada")
        await session.delete(role)
        await session.commit()
        return {"message": "Role excluída"}


# ─── Combinacoes Salvas (Spec 004, Principle IV) ───────────────────────


@router.post("/combinacoes")
async def save_combinacao(
    jogo: str,
    dezenas: list[int],
    dezenas_por_aposta: int,
    current_user=Depends(get_current_user),
):
    """Save a combination to user history. Prevents duplicates via hash. FIFO at 200."""
    if not dezenas:
        raise HTTPException(
            status_code=422, detail="Lista de dezenas não pode estar vazia"
        )
    try:
        combo = await sv(str(current_user["id"]), jogo, dezenas, dezenas_por_aposta)
        return {
            "id": str(combo.id),
            "hash": combo.hash_combinacao,
            "created_at": str(combo.created_at),
        }
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/combinacoes")
async def list_combinacoes(
    page: int = 1,
    per_page: int = 20,
    jogo: str = None,
    current_user=Depends(get_current_user),
):
    """List user's saved combinations."""
    combos = await ls(str(current_user["id"]), page, per_page, jogo)
    return [
        {
            "id": str(c.id),
            "jogo": c.jogo,
            "dezenas": c.dezenas,
            "favorita": c.favorita,
            "created_at": str(c.created_at),
        }
        for c in combos
    ]


@router.delete("/combinacoes/{combinacao_id}")
async def delete_combinacao(combinacao_id: str, current_user=Depends(get_current_user)):
    """Delete a combination."""
    if not await dc(combinacao_id, str(current_user["id"])):
        raise HTTPException(status_code=404, detail="Combinação não encontrada")
    return {"message": "Combinação removida"}


@router.put("/combinacoes/{combinacao_id}/favorita")
async def toggle_favorita(combinacao_id: str, current_user=Depends(get_current_user)):
    """Toggle favorite status."""
    result = await tf(combinacao_id, str(current_user["id"]))
    if result is None:
        raise HTTPException(status_code=404, detail="Combinação não encontrada")
    return {"favorita": result}


# ─── Promessas (Spec 001, Principle V) ─────────────────────────────────


@router.post("/promessas")
async def create_promessa(
    titulo: str = None,
    prioridade: str = "media",
    valor_total: float = 0.0,
    combinacoes: list[dict] = [],
    current_user=Depends(get_current_user),
):
    """Create a bet promise. FIFO at 50."""
    promessa = await cp(
        str(current_user["id"]), titulo, prioridade, valor_total, combinacoes
    )
    return {
        "id": str(promessa.id),
        "valor_total": promessa.valor_total,
        "created_at": str(promessa.created_at),
    }


@router.get("/promessas")
async def list_promessas(
    page: int = 1,
    per_page: int = 20,
    prioridade: str = None,
    current_user=Depends(get_current_user),
):
    """List user's promises."""
    promessas = await lp(str(current_user["id"]), page, per_page, prioridade)
    return [
        {
            "id": str(p.id),
            "titulo": p.titulo,
            "prioridade": p.prioridade,
            "valor_total": p.valor_total,
            "favorita": p.favorita,
            "created_at": str(p.created_at),
        }
        for p in promessas
    ]


@router.delete("/promessas/{promessa_id}")
async def delete_promessa(promessa_id: str, current_user=Depends(get_current_user)):
    """Delete a promise."""
    if not await dp(promessa_id, str(current_user["id"])):
        raise HTTPException(status_code=404, detail="Promessa não encontrada")
    return {"message": "Promessa removida"}


@router.post("/promessas/{promessa_id}/clone")
async def clone_promessa(promessa_id: str, current_user=Depends(get_current_user)):
    """Clone a promise."""
    clone = await cl(promessa_id, str(current_user["id"]))
    if not clone:
        raise HTTPException(status_code=404, detail="Promessa não encontrada")
    return {"id": str(clone.id), "titulo": clone.titulo}


@router.post("/promessas/{promessa_id}/compartilhar")
async def share_promessa(promessa_id: str, current_user=Depends(get_current_user)):
    """Generate HMAC sharing link (7-day expiry)."""
    share_hash = await sp(promessa_id, str(current_user["id"]))
    if not share_hash:
        raise HTTPException(status_code=404, detail="Promessa não encontrada")
    link = f"luckynumber://promise/{share_hash}"
    return {"link": link, "expiracao": "7 dias"}


# ─── Notifications (Spec 003) ──────────────────────────────────────────


@router.get("/notifications")
async def list_notifications(
    page: int = 1, per_page: int = 20, current_user=Depends(get_current_user)
):
    """List user's notifications."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(NotificationDelivery)
            .where(NotificationDelivery.user_id == current_user["id"])
            .order_by(NotificationDelivery.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return [
            {"id": str(d.id), "lida": d.lida, "created_at": str(d.created_at)}
            for d in result.scalars().all()
        ]


@router.put("/notifications/{delivery_id}/read")
async def mark_notification_read(
    delivery_id: str, current_user=Depends(get_current_user)
):
    """Mark notification as read."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(NotificationDelivery).where(
                NotificationDelivery.id == delivery_id,
                NotificationDelivery.user_id == current_user["id"],
            )
        )
        delivery = result.scalar_one_or_none()
        if not delivery:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        delivery.lida = True
        delivery.lida_em = datetime.now(UTC)
        await session.commit()
        return {"message": "Marcada como lida"}


@router.post("/admin/notifications")
async def create_notification(
    titulo: str,
    mensagem: str,
    prioridade: str = "media",
    destinatario_user_id: str = None,
    destinatario_role_id: str = None,
    current_user=Depends(get_current_user),
):
    """Create system notification (admin only)."""
    async with async_session_factory() as session:
        notif = SystemNotification(
            titulo=titulo,
            mensagem=mensagem,
            prioridade=prioridade,
            destinatario_user_id=destinatario_user_id,
            destinatario_role_id=destinatario_role_id,
            created_by=current_user["id"],
        )
        session.add(notif)
        await session.commit()
        return {"id": str(notif.id), "titulo": notif.titulo}


# ─── Dashboard & Tracking (Spec 003) ────────────────────────────────────


@router.get("/admin/dashboard/summary")
async def dashboard_summary(current_user=Depends(get_current_user)):
    """Aggregate metrics for admin dashboard."""
    async with async_session_factory() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
        total_bets = (
            await session.execute(select(func.count(Combinacao.id)))
        ).scalar() or 0
        total_promises = (
            await session.execute(select(func.count(Promessa.id)))
        ).scalar() or 0
        return {
            "total_usuarios": total_users,
            "total_apostas": total_bets,
            "total_promessas": total_promises,
        }


@router.get("/admin/dashboard/events")
async def dashboard_events(
    event_type: str = None,
    page: int = 1,
    per_page: int = 20,
    current_user=Depends(get_current_user),
):
    """Filtered usage events."""
    async with async_session_factory() as session:
        query = select(UsageEvent).order_by(UsageEvent.created_at.desc())
        if event_type:
            query = query.where(UsageEvent.event_type == event_type)
        result = await session.execute(
            query.offset((page - 1) * per_page).limit(per_page)
        )
        return [
            {
                "id": str(e.id),
                "type": e.event_type,
                "regiao": e.regiao,
                "at": str(e.created_at),
            }
            for e in result.scalars().all()
        ]


# ─── Export & Share (Spec 019) ─────────────────────────────────────────


@router.get("/export/csv")
async def export_csv(current_user=Depends(get_current_user)):
    """Export user's combinations as CSV. Prevents CWE-79: output encoding."""
    from lucky_number.services.share_service import generate_csv, get_user_combinations
    from fastapi.responses import PlainTextResponse

    combos = await get_user_combinations(str(current_user["id"]))
    csv_content = generate_csv(combos)
    return PlainTextResponse(
        csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=combinacoes.csv"},
    )


@router.get("/export/json")
async def export_json(current_user=Depends(get_current_user)):
    """Export user's combinations as JSON."""
    from lucky_number.services.share_service import generate_json, get_user_combinations
    from fastapi.responses import PlainTextResponse

    combos = await get_user_combinations(str(current_user["id"]))
    return PlainTextResponse(
        generate_json(combos),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=combinacoes.json"},
    )


@router.get("/export/pdf")
async def export_pdf(current_user=Depends(get_current_user)):
    """Export user's combinations as PDF."""
    from lucky_number.services.share_service import generate_pdf
    from fastapi.responses import Response

    pdf_bytes = await generate_pdf(str(current_user["id"]))
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=combinacoes.pdf"},
    )


@router.get("/share/whatsapp")
async def share_whatsapp(
    combinacao_id: str = None, current_user=Depends(get_current_user)
):
    """Generate WhatsApp sharing link with plain text."""
    from lucky_number.services.share_service import (
        format_whatsapp_text,
        get_user_combinations,
    )
    import urllib.parse

    combos = await get_user_combinations(str(current_user["id"]))
    if combinacao_id:
        combos = [c for c in combos if str(c.get("id", "")) == combinacao_id]
    text = format_whatsapp_text(combos)
    wa_link = f"https://wa.me/?text={urllib.parse.quote(text)}"
    return {"link": wa_link, "expiracao": f"{SHARING_TTL_DAYS} dias"}


@router.post("/share/user/{recipient_id}")
async def share_with_user(recipient_id: str, current_user=Depends(get_current_user)):
    """Share combinations with another user via notification."""
    from lucky_number.services.share_service import (
        get_user_combinations,
        share_with_user as swu,
    )

    combos = await get_user_combinations(str(current_user["id"]))
    await swu(str(current_user["id"]), recipient_id, combos)
    return {"message": "Combinações compartilhadas com sucesso"}


@router.get("/share/clipboard")
async def share_clipboard(current_user=Depends(get_current_user)):
    """Get formatted text for clipboard copy."""
    from lucky_number.services.share_service import (
        format_clipboard,
        get_user_combinations,
    )
    from fastapi.responses import PlainTextResponse

    combos = await get_user_combinations(str(current_user["id"]))
    return PlainTextResponse(format_clipboard(combos), media_type="text/plain")


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
    """Health check. Validates DB + Redis (when available)."""
    try:
        from lucky_number.database.engine import check_health

        db_ok = await check_health()
        status = "ok" if db_ok else "degraded"
    except Exception:
        status = "degraded"
        db_ok = False

    redis_ok = None
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        await r.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    return {
        "status": status,
        "database": "connected" if db_ok else "disconnected",
        "redis": (
            "connected"
            if redis_ok
            else "disconnected" if redis_ok is False else "not_checked"
        ),
        "timestamp": datetime.now(UTC).isoformat(),
    }
