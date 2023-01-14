from core import security
from crud.task import task_crud
from fastapi import APIRouter, Depends
from schemas.task import Task

router = APIRouter()



#일단은 입출력 예제 두개씩 넣기
@router.post('/manage/', tags=['manage'])
async def upload_task(task: Task = Depends()):
    task_crud.insert_task(task)
    return {
        "result": 1,
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

@router.get('/deletetask/{task_id}', tags=['manage'])
async def deletetask(task_id,token: dict = Depends(security.check_token)):
    return task_crud.delete_task(task_id)