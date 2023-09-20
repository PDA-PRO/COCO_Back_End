from typing import Annotated
from fastapi import APIRouter, Body, Depends,HTTPException,status
from app.crud.hot import hot_crud
from app.crud.user import user_crud
from app.core import security
from app.api.deps import get_cursor,DBCursor
from app.core import notice

router = APIRouter()

@router.get("/hot", tags=['mics.'])
def hot_list(db_cursor:DBCursor=Depends(get_cursor)):
    return hot_crud.hot_list(db_cursor)

@router.get('/my_status/{user_id}', tags=['mics.'])
def my_status(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return hot_crud.my_status(db_cursor,user_id)

@router.get("/notice",tags=["mics."])
def read_notice():
    """
    공지사항 조회
    """
    result=notice.get_notice()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 로드 중 오류 발생"
        )
    return result

@router.put('/notice', tags=["mics."])
def update_notice(content: Annotated[str, Body(embed=True)], token: dict = Depends(security.check_token)):
    """
    공지사항 업데이트

    - content : html형식의 공지사항 내용
    """
    result=notice.update_notice(content)
    if token["role"]!=1:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Admin privileges are required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 업데이트 중 오류 발생"
        )
    
@router.get('/request-tutor', tags = ['mics.'])
def read_tutor_request(db_cursor:DBCursor=Depends(get_cursor)):
    '''
    모든 튜터 신청 정보 조회
    '''
    return user_crud.read(db_cursor,table="user_tutor")