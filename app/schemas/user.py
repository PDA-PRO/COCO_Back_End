from pydantic import (
    BaseModel,
    conint,
    EmailStr
)
from pydantic_core import core_schema
import re
from .common import *

class PasswordStr(str):
    @classmethod
    def __get_pydantic_core_schema__(cls,_source,_handler,):
        return core_schema.no_info_after_validator_function(cls.password_validator, core_schema.str_schema())

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        field_schema = handler(core_schema)
        field_schema.update(type='string', format='password',example='qwer1234!')
        return field_schema
    
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
    pw:PasswordStr|None=None
    name:str|None=None
    email:EmailStr|None=None
    cur_pw:PasswordStr|None=None
class UpdateEmail(BaseModel):
    id: str
    email :EmailStr

class UpdatePermission(BaseModel):
    id: str
    role: conint(le=1,ge=0)|None=None
    tutor:conint(le=1,ge=0)|None=None
    
class FindId(BaseModel):
    name: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    alarm: int

class UserListIn(PaginationIn):
    keyword: str | None=None
    role: conint(le=1,ge=0)|None=None
    tutor:conint(le=1,ge=0)|None=None

class UserList(BaseModel):
    id: str
    name: str
    role: conint(le=1,ge=0)
    exp: int
    level: int

class UserListOut(PaginationOut):
    userlist:list[UserList]

