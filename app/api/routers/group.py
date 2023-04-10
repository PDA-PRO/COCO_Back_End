from fastapi import APIRouter, Depends
from core import security
from crud.group import group
from schemas.group import *

router = APIRouter(prefix='/group')

# 전체 그룹 리스트(그룹명, 설명)
@router.get('/all_groups', tags=['group'])
async def all_groups():
    return group.all_groups()

@router.get("/mygroup/{user_id}", tags=['group'])
async def mygroup(user_id: str):
    return group.mygroup(user_id)

@router.get("/userlist/", tags=["group"])
async def userlist():
    return group.userlist()

@router.post("/makegroup/", tags=["group"])
async def make_group(info: MakeGroup):
    return group.make_group(info)