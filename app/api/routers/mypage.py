from fastapi import APIRouter
from crud.mypage import mypage

router = APIRouter()

@router.get('/myPageOne/{user_id}', tags=['mypage'])
async def mypage_one(user_id: str):
    return mypage.myinfo(user_id)

@router.get('/myPageThree/{user_id}', tags=['mypage'])
async def mypage_three(user_id: str):
    return mypage.myboard(user_id)

