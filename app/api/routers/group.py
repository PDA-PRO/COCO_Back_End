from fastapi import APIRouter, Depends
from core import security
from crud.group import group

router = APIRouter(prefix='/group')

# 전체 그룹 리스트(그룹명, 설명)
@router.get('/all_groups', tags=['group'])
async def all_groups():
    return group.all_groups()

@router.get("/mygroup/{user_id}", tags=['group'])
async def mygroup(user_id: str):
    return group.mygroup(user_id)