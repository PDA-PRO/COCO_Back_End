from fastapi import APIRouter
from crud.status import status_crud
from pydantic import BaseModel


class TaskStatus(BaseModel):
    user_id: str
    option: tuple
    task_info: str

router = APIRouter()

@router.get("/status/", tags=["status"])
async def status(user_id: str|None = None, lang: int|None = None, result: bool|None = None):
    if user_id:
        return status_crud.select_status_user(user_id, lang, result)
    else:
        return status_crud.select_status(lang, result)

@router.post("/task_status/", tags=['status'])
async def task_status(info: TaskStatus):
    return status_crud.status_per_task(info)