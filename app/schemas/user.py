from pydantic import (
    BaseModel,
    conint,
    EmailStr
)
import re
from .common import *

class PasswordStr(str):
    @classmethod
    def __modify_schema__(cls, field_schema: dict[str]) -> None:
        field_schema.update(type='string', format='password')

    @classmethod
    def __get_validators__(cls):
        yield cls.password_validator
    
    @classmethod
    def password_validator(cls, v: str) -> str:
        if re.fullmatch("^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{8,15}$",v):
            return v
        else:
            raise ValueError('비밀번호는 영어, 숫자, 특수기호를 포함하고 8-15 길이여야합니다.')

#로그인
class Login(BaseModel):
    id: str
    pw: PasswordStr

#회원가입 정보
class SignUp(Login):
    name: str
    email: EmailStr

class UpdateUser(BaseModel):
    pw:PasswordStr|None
    name:str|None
    email:EmailStr|None
    cur_pw:PasswordStr|None
class UpdateEmail(BaseModel):
    id: str
    email :EmailStr

class UpdatePermission(BaseModel):
    id: str
    role: conint(le=1,ge=0)|None
    tutor:conint(le=1,ge=0)|None
    
class FindId(BaseModel):
    name: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    alarm: int

class UserListIn(PaginationIn):
    keyword: str | None
    role: conint(le=1,ge=0)|None
    tutor:conint(le=1,ge=0)|None

class UserList(BaseModel):
    id: str
    name: str
    role: conint(le=1,ge=0)
class UserListOut(PaginationOut):
    userlist:list[UserList]

