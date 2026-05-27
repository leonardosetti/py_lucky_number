"""Testes para o sistema de autenticação (Spec 003)."""

import pytest

from lucky_number.api.auth import (
    create_access_token,
    decode_jwt,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("Str0ng!Pass")
        assert isinstance(hashed, str)
        assert len(hashed) > 20
        assert hashed != "Str0ng!Pass"

    def test_verify_password_correct(self):
        hashed = hash_password("Str0ng!Pass")
        assert verify_password("Str0ng!Pass", hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("Str0ng!Pass")
        assert verify_password("WrongPass", hashed) is False


class TestJWT:
    def test_create_and_decode_token(self):
        data = {"sub": "user-id-123", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_jwt(token)
        assert decoded["sub"] == "user-id-123"
        assert decoded["role"] == "admin"

    def test_token_has_expiry(self):
        token = create_access_token({"sub": "1"})
        decoded = decode_jwt(token)
        assert "exp" in decoded

    def test_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_jwt("invalid.token.here")
