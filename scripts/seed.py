#!/usr/bin/env python3
"""Seed script to populate initial data: features, roles, permissions, admin user.

Usage:
    python scripts/seed.py
"""
import asyncio

import bcrypt as _bcrypt
from sqlalchemy import select

from lucky_number.database.engine import async_session_factory
from lucky_number.database.models.feature_toggle import FeatureToggle
from lucky_number.database.models.role import Role
from lucky_number.database.models.permission import Permission
from lucky_number.database.models.user import User


def _hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt(rounds=12)).decode("utf-8")

SEED_FEATURES = [
    {"slug": "geracao-apostas", "nome": "Geração de Apostas", "descricao": "Permite gerar combinações aleatórias", "ativa": True},
    {"slug": "promessas", "nome": "Promessas de Aposta", "descricao": "Permite criar e gerenciar promessas", "ativa": True},
    {"slug": "export", "nome": "Exportação", "descricao": "Permite exportar combinações em CSV/JSON/PDF", "ativa": True},
    {"slug": "admin", "nome": "Painel Administrativo", "descricao": "Acesso ao painel de administração", "ativa": True},
]

SEED_ROLES = [
    {"nome": "Admin", "descricao": "Acesso total ao sistema", "parent_role_id": None},
    {"nome": "Auditor", "descricao": "Acesso somente leitura", "parent_role_id": None},
    {"nome": "TestDemo", "descricao": "Acesso editável efêmero (transaction rollback)", "parent_role_id": None},
    {"nome": "Apostador", "descricao": "Usuário comum — geração de apostas e promessas", "parent_role_id": None},
]

SEED_PERMISSIONS = [
    {"slug": "users.create", "nome": "Criar Usuário", "recurso": "users"},
    {"slug": "users.read", "nome": "Ler Usuário", "recurso": "users"},
    {"slug": "users.update", "nome": "Atualizar Usuário", "recurso": "users"},
    {"slug": "users.delete", "nome": "Excluir Usuário", "recurso": "users"},
    {"slug": "features.toggle", "nome": "Alternar Feature", "recurso": "features"},
    {"slug": "features.read", "nome": "Ler Features", "recurso": "features"},
    {"slug": "notifications.create", "nome": "Criar Notificação", "recurso": "notifications"},
    {"slug": "notifications.read", "nome": "Ler Notificações", "recurso": "notifications"},
    {"slug": "dashboard.read", "nome": "Ler Dashboard", "recurso": "dashboard"},
]


async def seed_features(session):
    for feat in SEED_FEATURES:
        result = await session.execute(select(FeatureToggle).where(FeatureToggle.slug == feat["slug"]))
        if not result.scalar_one_or_none():
            session.add(FeatureToggle(**feat))
    print(f"✅ Features: {len(SEED_FEATURES)}")


async def seed_roles(session):
    roles = {}
    for r in SEED_ROLES:
        result = await session.execute(select(Role).where(Role.nome == r["nome"]))
        existing = result.scalar_one_or_none()
        if not existing:
            role = Role(**r)
            session.add(role)
            await session.flush()
            roles[r["nome"]] = role
        else:
            roles[r["nome"]] = existing
    print(f"✅ Roles: {len(SEED_ROLES)}")
    return roles


async def seed_permissions(session):
    perms = {}
    for p in SEED_PERMISSIONS:
        result = await session.execute(select(Permission).where(Permission.slug == p["slug"]))
        existing = result.scalar_one_or_none()
        if not existing:
            perm = Permission(**p)
            session.add(perm)
            await session.flush()
            perms[p["slug"]] = perm
        else:
            perms[p["slug"]] = existing
    print(f"✅ Permissions: {len(SEED_PERMISSIONS)}")
    return perms


async def seed_admin(session, admin_role):
    result = await session.execute(select(User).where(User.email == "admin@luckynumber.app"))
    if not result.scalar_one_or_none():
        user = User(
            nome="Admin", email="admin@luckynumber.app",
            senha_hash=_hash_password("admin123"),
            role_id=admin_role.id,
        )
        session.add(user)
        print("✅ Admin user: admin@luckynumber.app / admin123")


async def main():
    print("🌱 Seeding database...")
    async with async_session_factory() as session:
        await seed_features(session)
        roles = await seed_roles(session)
        perms = await seed_permissions(session)
        await seed_admin(session, roles.get("Admin"))
        await session.commit()
    print("✅ Seed complete")


if __name__ == "__main__":
    asyncio.run(main())

