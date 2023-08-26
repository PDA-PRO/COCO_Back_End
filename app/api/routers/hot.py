from fastapi import APIRouter, Depends
from crud.hot import hot_crud
from core import security

router = APIRouter()

@router.get("/hot", tags=['home'])
async def hot_list():
    return hot_crud.hot_list()

@router.get('/my_status/{user_id}', tags=['home'])
async def my_status(user_id: str, token: dict = Depends(security.check_token)):
    return hot_crud.my_status(user_id)