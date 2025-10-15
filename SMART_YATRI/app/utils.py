# app/utils.py
# Helper functions for Smart Yatri backend
# Author: Humanized

from passlib.context import CryptContext

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain text password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against the hashed version
    """
    return pwd_context.verify(plain_password, hashed_password)
