from fastapi import APIRouter, Depends
from crud.mypage import mypage
from schemas.mypage import ChangeInfo
from core import security

router = APIRouter()

@router.get('/myPageOne/{user_id}', tags=['mypage'])
async def mypage_one(user_id: str,token: dict = Depends(security.check_token)):
    return mypage.myinfo(user_id)

@router.get('/myPageTwo/{user_id}', tags = ['mypage'])
# async def mypage_two(user_id: str, token: dict = Depends(security.check_token)):
async def mypage_two(user_id: str):
    return mypage.myproblems(user_id)

@router.get('/myPageThree/{user_id}', tags=['mypage'])
async def mypage_three(user_id: str, token: dict = Depends(security.check_token)):
    return mypage.myboard(user_id)

@router.post('/delete_myboard{board_id}', tags=['mypage'])
async def delete_myboard(board_id:int, token: dict = Depends(security.check_token)):
    return mypage.delete_myboard(board_id)

@router.post('/changePW/', tags=['mypage'])
async def change_pw(info: ChangeInfo,token: dict = Depends(security.check_token)):
    return mypage.change_pw(info)

@router.post('/changeEmail', tags=['mypage'])
async def change_email(info: ChangeInfo,token: dict = Depends(security.check_token)):
    return mypage.change_email(info)
