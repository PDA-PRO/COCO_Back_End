from schemas.login import Token
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
