"""
Security Utilities
Encryption, hashing, and security functions
"""

import os
import base64
from typing import Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_encryption_key() -> bytes:
    """
    Get or generate encryption key

    Returns:
        Encryption key bytes
    """
    key = os.getenv("ENCRYPTION_KEY")

    if not key:
        # Generate new key if not set
        key = Fernet.generate_key()
        print(f"Generated new encryption key: {key.decode()}")
        print("Please set ENCRYPTION_KEY in your .env file")
        return key

    return key.encode() if isinstance(key, str) else key


def encrypt_data(data: Union[str, bytes]) -> str:
    """
    Encrypt sensitive data

    Args:
        data: Data to encrypt

    Returns:
        Encrypted data as base64 string
    """
    if isinstance(data, str):
        data = data.encode()

    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(data)

    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt encrypted data

    Args:
        encrypted_data: Encrypted data as base64 string

    Returns:
        Decrypted data as string
    """
    key = get_encryption_key()
    f = Fernet(key)

    encrypted_bytes = base64.b64decode(encrypted_data.encode())
    decrypted = f.decrypt(encrypted_bytes)

    return decrypted.decode()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key(length: int = 32) -> str:
    """
    Generate a random API key

    Args:
        length: Length of the key in bytes

    Returns:
        Random API key
    """
    random_bytes = os.urandom(length)
    return base64.urlsafe_b64encode(random_bytes).decode().rstrip("=")


def mask_sensitive_data(data: str, reveal_chars: int = 4) -> str:
    """
    Mask sensitive data, revealing only first/last chars

    Args:
        data: Sensitive data to mask
        reveal_chars: Number of characters to reveal at start/end

    Returns:
        Masked data
    """
    if len(data) <= reveal_chars * 2:
        return "*" * len(data)

    return f"{data[:reveal_chars]}{'*' * (len(data) - reveal_chars * 2)}{data[-reveal_chars:]}"
