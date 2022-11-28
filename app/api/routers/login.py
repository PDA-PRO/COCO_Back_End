from pydantic import BaseModel
from fastapi import APIRouter
from crud.user import CrudUser
# import pymysql

router = APIRouter()

#회원가입 정보
class SignUp(BaseModel):
    name: str
    id: str
    pw: str
    role: int #0이면 학생, 1이면 선생
    age: int

#아이디 중복 확인
class ID(BaseModel):
    id:str

#로그인
class Login(BaseModel):
    id: str
    pw: str


@router.post('/login/', tags=["login"])
async def login(user:Login):
    return {'code': CrudUser.check_db(user)}

@router.post("/signup/", tags=["login"])
async def create_user(user: SignUp):
    return {"code": CrudUser.insert_db(user)}

@router.post("/checkids/", tags=["login"])
async def check_ids(id: ID):
    user_id = id.id
    return {"code": CrudUser.find_id(user_id)} 