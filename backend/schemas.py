from typing import Any, Literal

from pydantic import BaseModel, HttpUrl, field_validator


# data coming from frontend
class UserCreate(BaseModel):

    email: str

    password: str



# login request

class UserLogin(BaseModel):

    email: str

    password: str



# token response

class Token(BaseModel):

    access_token: str

    token_type: str


ContentType = Literal["URL", "TEXT", "FORM"]


class QRContentRequest(BaseModel):
    content_type: ContentType
    content: str | dict[str, Any]


class UpdateQRRequest(BaseModel):
    destination_url: HttpUrl | None = None
    content_type: ContentType | None = None
    content: str | dict[str, Any] | None = None

    @field_validator("content")
    @classmethod
    def reject_empty_content(cls, value):
        if value == "" or value is None:
            raise ValueError("content must not be empty")
        return value