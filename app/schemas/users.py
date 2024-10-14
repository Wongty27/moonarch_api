from pydantic import BaseModel, Field, SecretStr

class UserMaster(BaseModel):
    id: int
    username: str = Field(max_length=20)
    password: SecretStr = Field(max_length=30)