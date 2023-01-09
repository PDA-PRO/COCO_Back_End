from core import security
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter,Depends,HTTPException,status

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
@router.get("/auth/",tags=["authentication"])
async def read_users_me(token: dict = Depends(security.check_token)):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    # role=security.decode_jwt(token)
    # if role=="":
    #     raise credentials_exception

    return {"role":token.get("role")}