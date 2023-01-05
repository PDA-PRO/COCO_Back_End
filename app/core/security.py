from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

#환경변수에서 민감한 정보 가져오기
load_dotenv(verbose=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict,is_admin=False,exp_time:int=7):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=exp_time)
    print('to_encode: ', expire)
    to_encode.update({"exp": expire})
    if is_admin:
        to_encode.update({"role": 100})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def decode_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        role: str = payload.get("role")#잘못된 토큰이면 에러발생
        if role is None:
            return ""
    except JWTError:
        return ""
    return role