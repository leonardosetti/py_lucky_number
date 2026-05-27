"""Testes para o sistema de Feature Toggles (Spec 002)."""

from lucky_number.database.models.feature_toggle import FeatureToggle
from lucky_number.database.models.feature_toggle_audit import FeatureToggleAudit


class TestFeatureToggleModel:
    def test_model_attributes(self):
        """Verify SQLAlchemy model has expected columns."""
        mapper = FeatureToggle.__mapper__
        columns = {c.name for c in mapper.columns}
        assert "slug" in columns
        assert "nome" in columns
        assert "ativa" in columns
        assert "version" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_version_default(self):
        """version defaults to 1 (optimistic locking)."""
        assert FeatureToggle.__table__.columns["version"].default.arg == 1


class TestFeatureToggleAuditModel:
    def test_model_attributes(self):
        mapper = FeatureToggleAudit.__mapper__
        columns = {c.name for c in mapper.columns}
        assert "feature_toggle_id" in columns
        assert "changed_by" in columns
        assert "previous_state" in columns
        assert "new_state" in columns
        assert "created_at" in columns
