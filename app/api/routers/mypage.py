from fastapi import APIRouter
from crud.mypage import mypage

router = APIRouter()

@router.get('/myPageThree/{user_id}', tags=['mypage'])
async def mypage_three(user_id: str):
    return mypage.myboard(user_id)

