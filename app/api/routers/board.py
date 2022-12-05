from pydantic import BaseModel
from fastapi import APIRouter
from crud.board import CrudBoard

router = APIRouter()
crudBoard = CrudBoard()

class Board(BaseModel):
    id: int
    title: str
    user_id: str
    time: str
    category: int
    likes: int
    views: int
    comments: int

class FastWrite(BaseModel):
    user_id: str
    title: str
    context: str


@router.get('/board/', tags = ['board'])
async def check_board():
    return crudBoard.check_board()

@router.get('/board/{board_id}', tags = ['board'] )
async def detail_board(board_id: int):
    return crudBoard.board_detail(board_id)

@router.post('/fastWrite/', tags = ['board'])
async def fast_write(fastWrite: FastWrite):
    return {'code': crudBoard.fast_write(fastWrite)}
