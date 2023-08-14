from fastapi import APIRouter, Depends
from crud.submission import submission_crud
from core import security
from crud.user import user_crud
from crud.board import board_crud

router = APIRouter()

@router.get('/myPageOne/{user_id}', tags=['mypage'])
async def mypage_one(user_id: str,token: dict = Depends(security.check_token)):
    return user_crud.read(user_id)

@router.get('/myPageTwo/{user_id}', tags = ['mypage'])
async def mypage_two(user_id: str, token: dict = Depends(security.check_token)):
    return submission_crud.read_mysub(user_id)

@router.get('/myPageThree/{user_id}', tags=['mypage'])
async def mypage_three(user_id: str, token: dict = Depends(security.check_token)):
    return board_crud.read_myboard(user_id)

@router.post("/mytask/", tags=['mypage'])
async def post_mytask(user_id,task_id, token: dict = Depends(security.check_token)):
    return user_crud.create_mytask(user_id,task_id)

@router.get("/mytask/{user_id}", tags = ['mypage'])
async def read_mytask(user_id: str, token: dict = Depends(security.check_token)):
    return user_crud.read_mytask(user_id)

@router.delete("/mytask/", tags=['mypage'])
async def delete_mytask(user_id,task_id, token:dict = Depends(security.check_token)):
    return user_crud.delete_mytask(user_id,task_id)