from fastapi import APIRouter, Depends
from core import security
from crud.group import group
from schemas.group import *
from pydantic import BaseModel

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

class Info(BaseModel):
    info: str

@router.post("/search_user/", tags=["group"])
async def search_user(info: Info):
    return group.search_user(info.info)

@router.post("/leave_group/", tags=["group"])
async def leave_group(info: ModifyGroup):
    return group.leave_group(info)

@router.post("/delete_group/{group_id}/", tags=["group"])
async def delete_group(info: int):
    return group.delete_group(info)

@router.post("/invite_member/", tags=["group"])
async def invite_member(info: ModifyGroup):
    return group.invite_member(info)

@router.get("/{group_id}/", tags=['group'])
async def get_group(info: int):
    return group.get_group(info)