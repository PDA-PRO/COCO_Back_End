from fastapi import APIRouter, Depends,HTTPException,status
from app.crud.hot import hot_crud
from app.core import security
from app.api.deps import get_cursor,DBCursor
from app.core.notice import get_notice,update_notice

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
    result=get_notice()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 로드 중 오류 발생"
        )
    return result

@router.put('/notice', tags=["mics.","admin"])
def update_notice(content: str):
    """
    공지사항 업데이트

    - content : html형식의 공지사항 내용
    """
    result=update_notice(content)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 업데이트 중 오류 발생"
        )