from schemas.login import SignUp,ID,FindId,FindPw,Token
from fastapi import APIRouter,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core import security
from crud.user import user_crud

router = APIRouter()

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=Token,tags=["login"])
async def login_for_access_token(autologin:bool=False,form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_crud.check_db(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if autologin:
        access_token = security.create_access_token( data={"sub": user["id"],"role":user["role"], "name": user["name"], "user_exp":user["exp"], "level":user["level"]})
    else:
        access_token = security.create_access_token( data={"sub": user["id"],"role":user["role"], "name": user["name"], "user_exp":user["exp"], "level":user["level"]},exp_time=2)
    return {"access_token": access_token, "token_type": "bearer"}