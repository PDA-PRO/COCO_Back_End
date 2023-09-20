from app.schemas.user import *
from fastapi import APIRouter,Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core import security
from app.crud.user import user_crud
from app.api.deps import get_cursor,DBCursor

router = APIRouter()

@router.post("/signup/", tags=["login"])
def create_user(user: SignUp,db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 회원 생성
    pw해쉬값 저장
    
    - user
        - name : 실명
        - id : id
        - pw : 비밀번호는 영어, 숫자, 특수기호를 포함하고 8-15 길이
        - email : 이메일
    """
    return {"code": user_crud.create_user(db_cursor,user)}

@router.get("/checkids/", tags=["login"])
def check_id(id: str,db_cursor:DBCursor=Depends(get_cursor)):
    """
    회원가입시 아이디 중복 검사

    - id : user id
    """
    try:
        user_crud.exist_id(db_cursor,id)
        return {"code": 0}
    except:
        return {"code":1}

@router.get("/findid/", tags=["login"])
def get_id(info: FindId=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    id 찾기
    존재하지 않으면 0 리턴

    - info
        - name : 실명
        - email : 이메일
    """
    return {"code": user_crud.get_id(db_cursor,info)}

@router.patch("/pw/", tags=["login"])
def update_pw(pw:str,id:str,db_cursor:DBCursor=Depends(get_cursor)):
    """
    해당 user의 pw 업데이트
    id가 존재하지 않으면 오류

    - id : id
    - pw : 새로운 pw
    """
    try:
        user_crud.update_pw(db_cursor,Login(id=id,pw=pw))
        return {"code": 1}
    except ValueError:
        raise HTTPException(            
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": [
                    "pw"
                ],
                "msg": "비밀번호는 영어, 숫자, 특수기호를 포함하고 8-15 길이여야합니다.",
                "type": "value_error"
                }]
            )

@router.patch("/email/", tags=["login"])
def update_email(email:str,id:str,db_cursor:DBCursor=Depends(get_cursor)):
    """
    해당 user의 email 업데이트
 
    - id : id
    - email : email
    """
    try:
        user_crud.update_email(db_cursor,UpdateEmail(id=id,email=email))
        return {"code": 1}
    except ValueError :
        raise HTTPException(            
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": [
                    "email"
                ],
                "msg": "이메일 형식이 아닙니다.",
                "type": "value_error"
                }]
            )

#인증
#--------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login", response_model=Token,tags=["login"])
def login_for_access_token(autologin:bool=False,form_data: OAuth2PasswordRequestForm = Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    로그인
    자동로그인 체크시 토큰 일주일 유지 체크해제시 2시간 유지
 
    - autologin : 자동로그인 체크 
    - form_data
        - grant_type: the OAuth2 spec says it is required and MUST be the fixed string "password".
        Nevertheless, this dependency class is permissive and allows not passing it. If you want to enforce it,
        use instead the OAuth2PasswordRequestFormStrict dependency.
        - username: username string. The OAuth2 spec requires the exact field name "username".
        - password: password string. The OAuth2 spec requires the exact field name "password".
        - scope: Optional string. Several scopes (each one a string) separated by spaces. E.g.
        "items:read items:write users:read profile openid"
        - client_id: optional string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
        - client_secret: optional string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    """
    user_data = user_crud.get_user(db_cursor,form_data.username, form_data.password)
    user = user_data[0]
    alarm = user_data[1]
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if autologin:
        access_token = security.create_access_token( data={"sub": user["id"],"role":user["role"],"tutor":user["tutor"], "name": user["name"], "user_exp":user["exp"], "level":user["level"]})
    else:
        access_token = security.create_access_token( data={"sub": user["id"],"role":user["role"],"tutor":user["tutor"], "name": user["name"], "user_exp":user["exp"], "level":user["level"]},exp_time=2)
    return {"access_token": access_token, "token_type": "bearer", "alarm": alarm}