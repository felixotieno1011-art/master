from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Username must be 3-20 characters")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
