from fastapi import APIRouter
from crud.mypage import mypage
from schemas.mypage import ChangeInfo

router = APIRouter()

@router.get('/myPageOne/{user_id}', tags=['mypage'])
async def mypage_one(user_id: str):
    return mypage.myinfo(user_id)

@router.get('/myPageThree/{user_id}', tags=['mypage'])
async def mypage_three(user_id: str):
    return mypage.myboard(user_id)

@router.post('/delete_myboard{board_id}', tags=['mypage'])
async def delete_myboard(board_id:int):
    return mypage.delete_myboard(board_id)

@router.post('/changePW/', tags=['mypage'])
async def change_pw(info: ChangeInfo):
    return mypage.change_pw(info)

@router.post('/changeEmail', tags=['mypage'])
async def change_email(info: ChangeInfo):
    return mypage.change_email(info)
