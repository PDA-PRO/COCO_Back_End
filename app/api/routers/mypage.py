from fastapi import APIRouter, Depends
from app.crud.submission import submission_crud
from app.core import security
from app.crud.user import user_crud
from app.crud.board import board_crud
from app.api.deps import get_cursor,DBCursor

router = APIRouter()

@router.get('/myPageOne/{user_id}', tags=['mypage'])
def mypage_one(user_id: str,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return user_crud.read(db_cursor,["id","name","role","email","exp"],id=user_id)

@router.get('/myPageTwo/{user_id}', tags = ['mypage'])
def mypage_two(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return submission_crud.read_mysub(db_cursor,user_id)

@router.get('/myPageThree/{user_id}', tags=['mypage'])
def mypage_three(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return board_crud.read_myboard(db_cursor,user_id)

@router.post("/mytask/", tags=['mypage'])
def post_mytask(user_id,task_id, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return user_crud.create_mytask(db_cursor,user_id,task_id)

@router.get("/mytask/{user_id}", tags = ['mypage'])
def read_mytask(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return user_crud.read_mytask(db_cursor,user_id)

@router.delete("/mytask/", tags=['mypage'])
def delete_mytask(user_id,task_id, token:dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return user_crud.delete_mytask(db_cursor,user_id,task_id)