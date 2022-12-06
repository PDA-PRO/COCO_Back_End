import shutil
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, Depends
from crud.task import CrudTask
from typing import List
import zipfile
import os

router = APIRouter()

class Task(BaseModel):
    title: str
    description: str
    desPic: List[UploadFile]
    diff: int
    timeLimit: int
    memLimit: int
    inputDescription: str
    inputEx1: str
    inputEx2: str
    outputDescription: str
    outputEx1: str
    outputEx2: str
    python: bool
    C_Lan: bool
    testCase: UploadFile

#일단은 입출력 예제 두개씩 넣기
@router.post('/manage/', tags=['manage'])
async def upload_task(task: Task = Depends()):
    CrudTask.insert_task(task)
    return {
        "result": 1,
    }

@router.get('/problems', tags=['manage'])
async def read_task():
    return CrudTask.read_problems()

@router.get('/problems/{task_id}', tags=['manage'])
async def task_detail(task_id: int):
    return CrudTask.search_task(task_id)

@router.get('/tasklist', tags=['manage'])
async def tasklist():
    return CrudTask.select_simplelist()

@router.get('/deletetask/{task_id}', tags=['manage'])
async def deletetask(task_id):
    return CrudTask.delete_task(task_id)