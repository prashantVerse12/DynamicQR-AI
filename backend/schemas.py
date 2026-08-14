from pydantic import BaseModel


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