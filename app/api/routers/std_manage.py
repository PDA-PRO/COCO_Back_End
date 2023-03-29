from fastapi import APIRouter, Depends
from core import security
from crud.std_manage import std_manage
from schemas.std_manage import *

router = APIRouter(prefix='/std_manage')

# 관리할 학생 검색
@router.get('/search_student', tags=['std_manage'])
async def search_student():
    return std_manage.search_student()

# 관리할 학생 등록
@router.post('/add_student', tags=['std_manage'])
async def add_student(info: MyStudents):
    return std_manage.add_student(info)

# 등록한 학생 리스트
@router.get('/mystudents/{tea_id}', tags=["std_manage"])
async def my_students(tea_id: str):
    return std_manage.my_students(tea_id)

# 등록한 학생 제거
@router.post('/delete_mystudent', tags=["std_manage"])
async def delete_mystudents(info: MyStudents):
    return std_manage.delete_mystudents(info)