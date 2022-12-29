from schemas.login import Login,SignUp,ID,FindId,FindPw,Token
from fastapi import APIRouter,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core import security
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

#인증
#--------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/token", response_model=Token,tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_crud.check_db_v2(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token( data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/",tags=["authentication"])
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    userid=security.decode_jwt(token)
    if userid=="":
        print("gma")
        raise credentials_exception
    user = user_crud.get_user(userid)
    if len(user) == 0:
        raise credentials_exception
    return user[0]
