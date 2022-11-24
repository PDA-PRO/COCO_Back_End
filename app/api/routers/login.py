from pydantic import BaseModel
from fastapi import APIRouter
from crud.user import CrudUser
# import pymysql

router = APIRouter()

user_model = CrudUser()

#회원가입 정보
class SignUp(BaseModel):
    name: str
    id: str
    pw: str
    type: int #1이면 학생, 2이면 선생

#아이디 중복 확인
class ID(BaseModel):
    id:str

#로그인
class Login(BaseModel):
    id: str
    pw: str


@router.post('/login/', tags=["login"])
async def login(user:Login):
    return {'code': user_model.check_db(user)}

@router.post("/signup/", tags=["login"])
async def create_user(user: SignUp):
    return {"code": user_model.insert_db(user)}

@router.post("/checkids/", tags=["login"])
async def check_ids(id: ID):
    return {"code": user_model.find_ids(id.id)} 