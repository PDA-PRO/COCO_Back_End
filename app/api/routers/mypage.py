from fastapi import APIRouter, Depends, HTTPException
from app.crud.submission import submission_crud
from app.core import security
from app.crud.user import user_crud
from app.crud.board import board_crud
from app.api.deps import get_cursor,DBCursor

router = APIRouter()


@router.get('/mypage/{user_id}', tags=['mypage'])
def mypage_one(user_id: str,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    사용자의 기본 정보 조회
    - user_id
    - token : jwt
    """
    user_info = user_crud.read(db_cursor,["id","name","role","email","exp"],id=user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="user not found")
    sub_result = submission_crud.read_mysub(db_cursor,user_id)
    level = user_crud.user_level(db_cursor, user_id)
    is_me=False
    if token['id']==user_id:
        is_me=True
    if is_me == 1:
        board = board_crud.read_myboard(db_cursor,user_id)
        solved = sub_result['solved_list']
        unsolved = sub_result['unsolved_list']
        before_task = user_crud.read_mytask(db_cursor,token['id'])
        # 내 문제집 풀이여부 수정
        for value in before_task:
            if value['id'] in solved:
                sql = "UPDATE coco.my_tasks SET solved = 1 WHERE user_id = %s and task_num = %s;"
                data = (user_id, value['id'])
                db_cursor.execute_sql(sql, data)
            elif value['id'] in unsolved:
                sql = "UPDATE coco.my_tasks SET solved = -1 WHERE user_id = %s and task_num = %s;"
                data = (user_id, value['id'])
                db_cursor.execute_sql(sql, data)
        after_task = user_crud.read_mytask(db_cursor,token['id'])
        return {
            "user_info": user_info[0],
            "sub_result": sub_result,
            'level': level,
            'board': board,
            'task': after_task
        }
    elif is_me == 2:
        return {
            "user_info": user_info[0],
            "sub_result": sub_result,
            'level': level,
        }

@router.post("/mytask", tags=['mypage'])
def add_mytask(task_id:int, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    내 문제집에 문제 추가

    - task_id
    - token : jwt
    """
    return user_crud.create_mytask(db_cursor,token['id'],task_id)

@router.delete("/mytask", tags=['mypage'])
def delete_mytask(task_id:int, token:dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    내 문제집에서 문제 삭제

    - task_id
    - token : jwt
    """
    return user_crud.delete_mytask(db_cursor,token['id'],task_id)
