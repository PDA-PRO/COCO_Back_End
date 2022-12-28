from pydantic import BaseModel

#회원가입 정보
class SignUp(BaseModel):
    name: str
    id: str
    pw: str
    email: str
    role: int #0이면 학생, 1이면 선생
    age: int

#아이디 중복 확인
class ID(BaseModel):
    id:str

#로그인
class Login(BaseModel):
    id: str
    pw: str

class FindId(BaseModel):
    name: str
    email: str

class FindPw(BaseModel):
    name: str
    id: str
    email:str