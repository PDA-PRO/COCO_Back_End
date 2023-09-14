from fastapi import APIRouter, Depends
from app.schemas.submission import StatusListIn,StatusListOut
from app.crud.submission import submission_crud
from app.api.deps import get_cursor,DBCursor

router = APIRouter()

@router.get("/status/", tags=["status"],response_model=StatusListOut)
def read_status(info:StatusListIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    제출 조회

    - info
        - size: 한 페이지의 크기
        - page: 현재 페이지 번호
        - task_id: 문제 id 
        - lang: 제출 코드 언어 0 -> 파이썬 1-> c언어
        - user_id: 
        - answer: status가 3("정답") 인지 여부
    """
    
    return submission_crud.read_status(db_cursor,info)
