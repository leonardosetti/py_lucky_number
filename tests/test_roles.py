"""Testes para roles e permissões (Spec 003)."""

from lucky_number.database.models.role import Role
from lucky_number.database.models.permission import Permission
from lucky_number.database.models.role_permission import RolePermission


class TestRoleModel:
    def test_model_attributes(self):
        mapper = Role.__mapper__
        cols = {c.name for c in mapper.columns}
        assert "nome" in cols
        assert "parent_role_id" in cols
        assert "descricao" in cols

    def test_role_repr(self):
        role = Role(nome="Admin", descricao="Full access")
        assert "Admin" in repr(role)


class TestPermissionModel:
    def test_model_attributes(self):
        mapper = Permission.__mapper__
        cols = {c.name for c in mapper.columns}
        assert "slug" in cols
        assert "recurso" in cols

    def test_unique_slug(self):
        slug_col = Permission.__table__.columns["slug"]
        assert slug_col.unique is True


class TestRolePermissionModel:
    def test_composite_pk(self):
        """Verify composite primary key."""
        pk = RolePermission.__table__.primary_key
        assert len(pk.columns) == 2
        assert "role_id" in pk.columns
        assert "permission_id" in pk.columns
