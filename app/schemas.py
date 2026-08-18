from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None
    role: str = "viewer"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class ConversationCreate(BaseModel):
    title: str | None = None