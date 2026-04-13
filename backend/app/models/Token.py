from sqlmodel import SQLModel


class TokenPayload(SQLModel):
    sub: str | None = None
