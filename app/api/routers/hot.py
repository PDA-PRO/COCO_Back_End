from fastapi import APIRouter
from crud.hot import hot_crud
from crud.base import Crudbase

router = APIRouter()


@router.get("/hot")
async def hot_list():
    return hot_crud.hot_list()


@router.post("/aitest")
async def aitest(num: int):
    return Crudbase.is_auto_increase(Crudbase, num)
