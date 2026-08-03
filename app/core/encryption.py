import json
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from app.config import get_settings


@lru_cache
def get_fernet() -> Fernet:
    settings = get_settings()
    return Fernet(settings.field_encryption_key)


class EncryptedString(TypeDecorator):
    """Transparently encrypts/decrypts a text column at rest (Fernet/AES-128-CBC+HMAC)."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            return None


class EncryptedJSON(TypeDecorator):
    """Encrypts a JSON-serializable value (e.g. list of IoCs) at rest."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        payload = json.dumps(value)
        return get_fernet().encrypt(payload.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            decrypted = get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            return None
        return json.loads(decrypted)
