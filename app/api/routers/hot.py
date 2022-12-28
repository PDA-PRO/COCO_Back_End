from fastapi import APIRouter
from crud.hot import hot_crud

router = APIRouter()

@router.get("/hot")
async def hot_list():
    return hot_crud.hot_list()