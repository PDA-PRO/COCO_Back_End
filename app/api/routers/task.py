import json
from core import security
from crud.task import task_crud
from fastapi import APIRouter, Depends, Form
from schemas.task import Task
from pydantic import BaseModel


router = APIRouter()

class Info(BaseModel):
    info: str

@router.post('/manage/', tags=['manage'])
async def upload_task(description :str=Form(...),task: Task = Depends(), token: dict = Depends(security.check_token)):
    """ 
    새로운 문제를 업로드
    
    - description : 텍스트 에디터의 raw format 즉 json형식의 str
    - task : 문제의 다른 요소들
    """
    return {
        "result":  task_crud.insert_task(task,description)
    }

@router.get('/problems', tags=['manage'])
async def read_task(keyword:str=None,sort:str="id"):
    return task_crud.read_problems(keyword)

@router.get('/problems/{task_id}', tags=['manage'])
async def task_detail(task_id: int):
    return task_crud.search_task(task_id)

@router.get('/tasklist', tags=['manage'])
async def tasklist():
    return task_crud.select_simplelist()

@router.post("/order_task", tags=['manage'])
async def order_task(order: dict):
    return task_crud.order_task(order['order'])

@router.get('/deletetask/{task_id}', tags=['manage'])
async def deletetask(task_id, token: dict = Depends(security.check_token)):
    return task_crud.delete_task(task_id)

@router.post("/find_task/", tags=['manage'])
async def find_task(info: Info):
    return task_crud.find_task(info.info)
