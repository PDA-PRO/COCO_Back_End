from fastapi import APIRouter, Depends
from app.crud.submission import submission_crud
from app.core import security
from app.crud.user import user_crud
from app.crud.board import board_crud
from app.api.deps import get_cursor,DBCursor
from app.schemas.board import UpdateBoard

router = APIRouter()

@router.get('/myPageOne/{user_id}', tags=['mypage'])
def mypage_one(user_id: str,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    사용자의 기본 정보 조회

    - user_id
    - token : jwt
    """
        
    return user_crud.read(db_cursor,["id","name","role","email","exp"],id=user_id)

@router.get('/myPageTwo/{user_id}', tags = ['mypage'])
def mypage_two(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    사용자의 역량 정보 조회

    - user_id
    - token : jwt
    """
    return submission_crud.read_mysub(db_cursor,user_id)

@router.get('/myPageThree/{user_id}', tags=['mypage'])
def mypage_three(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    사용자의 게시글 정보 조회

    - user_id
    - token : jwt
    """
    return board_crud.read_myboard(db_cursor,user_id)

@router.post("/mytask/", tags=['mypage'])
def add_mytask(task_id:int, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    내 문제집에 문제 추가

    - task_id
    - token : jwt
    """
    return user_crud.create_mytask(db_cursor,token['id'],task_id)

@router.get("/mytask/", tags = ['mypage'])
def read_mytask(token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    내 문제집 조회

    - task_id
    - token : jwt
    """
    return user_crud.read_mytask(db_cursor,token['id'])

@router.delete("/mytask/", tags=['mypage'])
def delete_mytask(task_id:int, token:dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    내 문제집에서 문제 삭제

    - task_id
    - token : jwt
    """
    return user_crud.delete_mytask(db_cursor,token['id'],task_id)

@router.put("/board/update-board", tags=['mypage'])
def update_board(info: UpdateBoard, token:dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return user_crud.update_board(db_cursor, info, token['id'])