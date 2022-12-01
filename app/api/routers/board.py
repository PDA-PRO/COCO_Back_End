from pydantic import BaseModel
from fastapi import APIRouter
from crud.board import CrudBoard

router = APIRouter()

class Board(BaseModel):
    id: int
    title: str
    user_id: str
    time: str
    category: int
    likes: int
    views: int
    comments: int

@router.get('/board/', tags = ['board'])
async def check_board():
    return CrudBoard.check_board()