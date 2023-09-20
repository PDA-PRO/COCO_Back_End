from pydantic import (
    BaseModel,
    validator,
    conint,
    EmailStr
)
import re
from .common import *

#로그인
class Login(BaseModel):
    id: str
    pw: str

    @validator('pw')
    @classmethod
    def password_validator(cls, v: str) -> str:
        if re.fullmatch("^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{8,15}$",v):
            return v
        else:
            raise ValueError('비밀번호는 영어, 숫자, 특수기호를 포함하고 8-15 길이여야합니다.')

#회원가입 정보
class SignUp(Login):
    name: str
    email: EmailStr

class UpdateEmail(BaseModel):
    id: str
    email :EmailStr

class UpdateRole(BaseModel):
    id: str
    role: conint(le=1,ge=0)
    
class FindId(BaseModel):
    name: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    alarm: list

class UserListIn(PaginationIn):
    keyword: str | None
    role:conint(le=1,ge=0)|None

class UserList(BaseModel):
    id: str
    name: str
    role: conint(le=1,ge=0)
class UserListOut(PaginationOut):
    userlist:list[UserList]