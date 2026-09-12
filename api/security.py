from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 bytes)")
    return pwd_context.hash(password)