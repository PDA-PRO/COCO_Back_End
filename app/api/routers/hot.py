from fastapi import APIRouter, Depends
from crud.hot import hot_crud
from core import security
from api.deps import get_cursor,DBCursor

router = APIRouter()

@router.get("/hot", tags=['home'])
async def hot_list(db_cursor:DBCursor=Depends(get_cursor)):
    return hot_crud.hot_list(db_cursor)

@router.get('/my_status/{user_id}', tags=['home'])
async def my_status(user_id: str, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    return hot_crud.my_status(db_cursor,user_id)