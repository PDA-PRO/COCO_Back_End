from schemas.login import Token
from schemas.notice import Notice
from fastapi import APIRouter,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from core import security
from core.admin import check

router = APIRouter(prefix="/manage")

#인증
#--------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=Token,tags=["admin"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if check.check_admin(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": form_data.username},is_admin=True,exp_time=1)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/notice",tags=["admin"])
async def get_notice():
    result=check.get_notice()
    if result==None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 로드 중 오류 발생"
        )
    return result

@router.post("/notice/",tags=["admin"])
async def update_notice(data:Notice,token:dict=Depends(security.check_token)):
    rsult=check.update_notice(data.content)
    if not rsult:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 업데이트 중 오류 발생"
        )