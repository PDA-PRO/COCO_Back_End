from fastapi import APIRouter
from crud.status import status_crud

router = APIRouter()

@router.get("/status/", tags=["status"])
async def status(user_id: str|None = None, sub_id: int|None = None, task_id:int|None=None):
    if user_id:
        return status_crud.select_status_user(user_id)
    else:
        return status_crud.select_status()