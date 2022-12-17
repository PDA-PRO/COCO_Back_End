from pydantic import BaseModel
from fastapi import APIRouter

from crud.hot import CrudHot
router = APIRouter()

crudHot = CrudHot()


@router.get("/hot")
async def hot_list():
    return crudHot.hot_list()