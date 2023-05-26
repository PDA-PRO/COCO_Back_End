from fastapi import APIRouter, Depends
from core import security
from crud.group import group
from schemas.group import *
from pydantic import BaseModel

router = APIRouter(prefix='/group')

class UserID(BaseModel):
    user_id: str

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

@router.post("/search_user/", tags=["group"])
async def search_user(info: UserID):
    return group.search_user(info.user_id)

@router.post("/leave_group/", tags=["group"])
async def leave_group(info: GroupMember):
    return group.leave_group(info)

@router.post("/delete_group/{group_id}/", tags=["group"])
async def delete_group(group_id: int):
    return group.delete_group(group_id)

@router.post("/invite_member/", tags=["group"])
async def invite_member(info: GroupMember):
    return group.invite_member(info)

@router.get("/{group_id}/", tags=['group'])
async def get_group(group_id: int):
    return group.get_group(group_id)

@router.get("/board/{group_id}", tags=["group"])
async def group_boardlist(group_id: int):
    return group.group_boardlist(group_id)

@router.get("/group_workbooks/{group_id}", tags=["group"])
async def group_workbooks(group_id: int):
    return group.group_workbooks(group_id)

@router.post("/add_problem", tags=["group"])
async def add_problem(info: GroupProblem):
    return { "code": group.add_problem(info) }

@router.post("/delete_problem", tags=["group"])
async def delete_problem(info: GroupProblem):
    return group.delete_problem(info)

@router.post("/check_member/", tags=["group"])
async def is_my_group(info: GroupMember):
    return group.is_my_group(info)

@router.post("/join_group/", tags=["group"])
async def join_group(info: JoinGroup):
    return group.join_group(info)

@router.get("/group_leader/{group_id}/", tags=["group"])
async def group_leader(group_id: int):
    return group.group_leader(group_id)

@router.get("/group_apply/{group_id}/", tags=["group"])
async def group_apply(group_id: int):
    return group.group_apply(group_id)