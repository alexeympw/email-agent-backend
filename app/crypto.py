from cryptography.fernet import Fernet

from .config import settings


def _get_fernet() -> Fernet:
    # ENCRYPTION_KEY must be a base64 urlsafe key of length 32 bytes
    return Fernet(settings.encryption_key.encode())


def encrypt_str(value: str) -> str:
    f = _get_fernet()
    token = f.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_str(token: str) -> str:
    f = _get_fernet()
    value = f.decrypt(token.encode("utf-8"))
    return value.decode("utf-8")
