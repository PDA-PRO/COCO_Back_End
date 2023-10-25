from fastapi import APIRouter, Depends, HTTPException
from app.crud.submission import submission_crud
from app.core import security
from app.crud.user import user_crud
from app.crud.board import board_crud
from app.api.deps import get_cursor,DBCursor
from app.schemas.board import UpdateBoard

router = APIRouter()


@router.get('/mypage/{type}/{user_id}', tags=['mypage'])
def mypage_one(type: int, user_id: str,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    사용자의 기본 정보 조회
    - type: 1=사용자의 기본 정보 조회, 2=타 사용자의 기본 정보 조회
    - user_id
    - token : jwt
    """
    user_info = user_crud.read(db_cursor,["id","name","role","email","exp"],id=user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="user not found")
    sub_result = submission_crud.read_mysub(db_cursor,user_id)
    level = user_crud.user_level(db_cursor, user_id)

    if type == 1:
        board = board_crud.read_myboard(db_cursor,user_id)
        task = user_crud.read_mytask(db_cursor,token['id'])
        return {
            "user_info": user_info[0],
            "sub_result": sub_result,
            'level': level,
            'board': board,
            'task': task
        }
    elif type == 2:
        return {
            "user_info": user_info[0],
            "sub_result": sub_result,
            'level': level,
        }

@router.post("/mytask/", tags=['mypage'])
def add_mytask(task_id:int, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    내 문제집에 문제 추가

    - task_id
    - token : jwt
    """
    return user_crud.create_mytask(db_cursor,token['id'],task_id)

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
    '''
    사용자가 작성한 게시글을 수정
    - info: 게시글 수정에 필요한 정보
      - board_id: 게시글 id
      - title: 게시글 타이틀
      - context: 게시글 본문
      - category: 게시글 카테고리
      - code: 코드
    '''
    return user_crud.update_board(db_cursor, info, token['id'])