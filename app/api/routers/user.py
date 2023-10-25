from app.core import security
from app.schemas.user import *
from fastapi import APIRouter,Depends, HTTPException
from app.crud.user import user_crud
from app.api.deps import get_cursor,DBCursor
from app.crud.alarm import alarm_crud

router = APIRouter(prefix="/user")
    
@router.get("/", tags=['user'],response_model=UserListOut)
def read_userlist(info : UserListIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    user의 id나 name, role, tutor로 검색
    id, name, role, tutor 값 리턴

    params
    - info
        - keyword : user의 id나 name | 값이 없을 시 모든 user 리스트 리턴
        - size : 한 페이지의 크기
        - page : 페이지
        - role : 0 -> 일반 유저 1-> 관리자
        - tutor : 0 -> 일반 유저 1-> 튜터
    -----------------------------------------------
    returns
    - userlist : 쿼리 결과
    - size와 page가 있을 경우 
        - total : 전체 결과
        - size : 페이지 크기
    """
    return user_crud.search_user(db_cursor,info)

@router.patch("/", tags=["user"])
def update_user(info:UpdateUser,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    해당 user의 정보 업데이트

    params
    - info
        - pw : 새로운 pw
        - name : 새로운 이름
        - email : 새로운 이메일
        - prev_pw : pw 변경시 현재 pw
    - token : jwt
    --------------------------
    raises
    - 새로운 pw 요청시 현재 pw가 없다면 에러 발생
    - 현재 pw가 맞지 않을 시 에러 발생
    """
    if info.pw is not None:
        if info.cur_pw is None:
            raise HTTPException(
            status_code=400,
            detail="If a new PW is requested, the current PW must also be provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if not security.verify_password(info.cur_pw,user_crud.read(db_cursor,["pw"],id=token["id"])[0]["pw"]):
            raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        else:
            info.pw=security.get_password_hash(info.pw)
    update_info=info.dict(exclude=set(["cur_pw"]),exclude_none=True)
    user_crud.update(db_cursor,update_info,id=token["id"])

    return {"code":1}
    
@router.patch("/permission", tags=["user"])
def update_permission(info : UpdatePermission,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    해당 user의 권한 업데이트
    관리자만 수정 가능

    - info 
        - id : 업데이트할 유저 target id
        - role : role | 0 -> 일반 유저 1 -> 관리자
        - turor : 0 -> 일반 유저, 1 -> 튜터
    - token : jwt
    """
    if token["role"]!=1:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Admin privileges are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if info.role is not None:
        user_crud.update(db_cursor,{"role":info.role},id=info.id)
        if info.role == 1:
            alarm_crud.create_alarm(db_cursor, {
                'sender': None,
                'receiver': info.id,
                'category': 13
            })
    if info.tutor is not None:
        user_crud.update(db_cursor,{"tutor":info.tutor},id=info.id)
        user_crud.delete(db_cursor,table="user_tutor",user_id=info.id)
        if info.tutor == 1:
            alarm_crud.create_alarm(db_cursor, {
                'sender': None,
                'receiver': info.id,
                'category': 4
            })
    
    return {"code":1}

@router.get("/checkid", tags=["user"])
def check_id(id: str,db_cursor:DBCursor=Depends(get_cursor)):
    """
    회원가입시 아이디 중복 검사
    존재하면 1 존재하지 않으면 0

    - user_id : user id
    """
    if user_crud.read(db_cursor,["id"],id=id):
        return {"code": 0}
    else:
        return {"code":1}
    
@router.get("/findid", tags=["user"])
def get_id(name:str,email:EmailStr,db_cursor:DBCursor=Depends(get_cursor)):
    """
    id 찾기
    존재하지 않으면 0 리턴

    - info
        - name : 실명
        - email : 이메일
    """
    result=user_crud.read(db_cursor,["id"],name=name,email=email)
    if len(result) == 0:
        return {"code": 0}
    else:
        return {"code": result[0]["id"]}
    
@router.patch("/pw", tags=["user"])
def update_pw_temp(info:SignUp,db_cursor:DBCursor=Depends(get_cursor)):
    """
    pw 재설정

    - info
        - name : 실명
        - email : 이메일
        - id : id
        - pw : 새로운 비밀번호
    --------------------------
    returns
    존재하지 않는 계정에 접근시 0리턴
    비밀번호 재설정에 설공하면 1리턴
    """
    result=user_crud.read(db_cursor,["id"],name=info.name,email=info.email,id=info.id)
    if len(result) == 0:
        raise HTTPException(
            status_code=404,
            detail="일치하는 계정이 존재하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        user_crud.update(db_cursor,{'pw':security.get_password_hash(info.pw)},id=info.id)
        return {"code": 1}
    
@router.get("/alarm", tags=['user'])
def get_alarm(token: dict = Depends(security.check_token), db_cursor:DBCursor=Depends(get_cursor)):
    return alarm_crud.get_alarm(db_cursor, token['id'])

@router.patch("/alarm/{user_id}", tags=['user'])
def check_alarm(user_id: str, db_cursor:DBCursor=Depends(get_cursor)):
    return alarm_crud.check_alarm(db_cursor, user_id)

@router.get("/level", tags=['user'])
def user_level(user_id: str, db_cursor:DBCursor=Depends(get_cursor)):
    return user_crud.user_level(db_cursor, user_id)