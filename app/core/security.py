from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.crud.room import room_crud
from app.db.base import DBCursor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, exp_time:int=None):
    """
    필요한 data들을 통해 JWT 엑세스 토큰 생성

    params
    - data : jwt에 들어갈 데이터
    - exp_time : jwt의 유효 기간 **시간 기준**
    ---------------
    returns
    - jwt : data와 유효기간을 jwt로 만들어 반환
    """
    to_encode = data.copy()
    if exp_time is None:
        exp_time=int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS"))*24
    expire = datetime.utcnow() + timedelta(hours=exp_time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    해쉬화된 비밀번호 비교

    params
    - plain_password : 비교할 입력 비밀번호
    - hashed_password : 저장되어 있는 비밀번호
    ---------------
    returns
    - bool
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    비밀번호 해쉬화

    params
    - password : 비밀번호
    ---------------
    returns
    - 해쉬화된 비밀번호
    """
    return pwd_context.hash(password)

def decode_jwt(token: str) -> str:
    """
    jwt를 검증하고 jwt의 role과 sub, tutor를 디코딩

    params
    - token : jwt
    ---------------
    returns
    - (role, id, tutor)
        - role : 유효한 jwt라면 role 리턴
        - id : 유효한 jwt라면 id 리턴
        - tutor : 유요한 jwt라면 tutor 권한 리턴
    """
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        role: str = payload.get("role")#잘못된 토큰이면 에러발생
        id: str = payload.get("sub")#잘못된 토큰이면 에러발생
        tutor: str = payload.get("tutor")#잘못된 토큰이면 에러발생
        if role is None or id is None or tutor is None:
            return "","",""
    except JWTError:
        return "","",""
    return role,id,tutor

def check_token(token: str = Depends(oauth2_scheme)):
    """
    Validate the token
    when token is invalid, error raised
    raise error when token is invalid

    params
    - token : jwt
    ---------------
    returns
    - {"role", "id", "tutor" }
    ---------------
    Raises:
    - credentials_exception: If token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    role,id,tutor=decode_jwt(token)
    if role=="" or id=="" or tutor=="":
        raise credentials_exception
    return {"role":role,"id":id,"tutor":tutor}

def check_admin(token):
    if token['role']!=1:
        raise HTTPException(
            status_code=403,
            detail="권한이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def check_tutor(token):
    if token['tutor']!=1:
        raise HTTPException(
            status_code=403,
            detail="권한이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def check_leader(db_cursor: DBCursor, room_id:int,leader:str):
    if not room_crud.read(db_cursor,['id'],leader=leader,id=room_id):
        raise HTTPException(
            status_code=403,
            detail="권한이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def check_tutee(db_cursor: DBCursor, room_id:int,member:str):
    if not room_crud.read(db_cursor,table='room_ids',user_id=member,room_id=room_id):
        raise HTTPException(
            status_code=403,
            detail="권한이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )