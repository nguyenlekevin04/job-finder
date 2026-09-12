
from pydantic import BaseModel


class UserResponse(BaseModel):
    """
    A response model for user data.
    """
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """
    A response model for authentication tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"