from fastapi import APIRouter
from crud.status import CrudStatus

router = APIRouter()


@router.get("/status/", tags=["status"])
async def status(user_id: str|None = None, sub_id: int|None = None, task_id:int|None=None):
    status=CrudStatus()
    if user_id:
        return status.select_status_user(user_id)
    else:
        return status.select_status()