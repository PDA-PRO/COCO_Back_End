from schemas.login import Token
from schemas.admin import Notice, Info
from fastapi import APIRouter,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core import security
from core.admin import check
from crud.task import task_crud
from crud.user import user_crud
from crud.room import room
from pydantic import BaseModel

router = APIRouter(prefix="/manage")

#인증
#--------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=Token,tags=["admin"])
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not check.check_admin(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": form_data.username},is_admin=True,exp_time=1)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/modify_key", tags=["admin"])
async def modify_admin_key(new_pw:Info,token:dict=Depends(security.check_token)):
    if check.modify_admin_key(new_pw=new_pw.PW):
        return
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="admin PW 수정중 오류 발생"
        )

@router.get("/tasklist", tags = ['admin'])
async def get_tasklist():
    return task_crud.manage_tasklist()

@router.get("/notice",tags=["admin"])
async def get_notice():
    result=check.get_notice()
    if result==None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 로드 중 오류 발생"
        )
    return result

@router.post('/notice', tags=["admin"])
async def update_notice(content: Notice):
    result=check.update_notice(content.html)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 업데이트 중 오류 발생"
        )

@router.get("/user_list", tags=["admin"])
async def user_list():
    return user_crud.user_list()

@router.get("/manager_list/", tags=["admin"])
async def manager_list():
    return user_crud.manager_list()

class UserID(BaseModel):
    user_id: str

@router.post("/search_user/", tags=['admin'])
async def search_user(info: UserID):
    return room.search_user(info.user_id)

@router.post("/add_manager", tags=["admin"])
async def add_manager(info: UserID):
    return user_crud.add_manager(info.user_id)

@router.post("/delete_manager", tags=["admin"])
async def delete_manager(info: UserID):
    return user_crud.delete_manager(info.user_id)
        