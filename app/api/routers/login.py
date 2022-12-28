from schemas.login import Login,SignUp,ID,FindId,FindPw
from fastapi import APIRouter
from crud.user import user_crud
# import pymysql

router = APIRouter()

@router.post('/login/', tags=["login"])
async def login(user:Login):
    return {'code': user_crud.check_db(user)}

@router.post("/signup/", tags=["login"])
async def create_user(user: SignUp):
    return {"code": user_crud.insert_db(user)}

@router.post("/checkids/", tags=["login"])
async def check_ids(id: ID):
    user_id = id.id
    return {"code": user_crud.check_id(user_id)} 

@router.post("/findid/", tags=["login"])
async def find_id(info: FindId):
    return {"code": user_crud.find_id(info)}

@router.post("/findpw/", tags=["login"])
async def find_pw(info: FindPw):
    return {"code": user_crud.find_pw(info)}