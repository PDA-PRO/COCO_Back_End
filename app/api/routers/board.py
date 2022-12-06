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

class BoardLikes(BaseModel):
    user_id: str
    board_id: int
    likes: int
    type: bool

class CommentLikes(BaseModel):
    user_id: str
    board_id: int
    comment_id: int
    likes: int
    type: bool

class CommentInfo(BaseModel):
    user_id: str
    context: str
    board_id: int





@router.get('/board/', tags = ['board'])
async def check_board():
    return crudBoard.check_board()

@router.get('/board/{board_id}', tags = ['board'] )
async def detail_board(board_id: int):
    return crudBoard.board_detail(board_id)

@router.post('/board_likes/', tags = ['board'])
async def board_likes(boardLikes: BoardLikes):
    return {'code': crudBoard.board_likes(boardLikes)}

@router.post('/comment/', tags = ['board'])
async def write_comment(commentInfo: CommentInfo):
    return {'code': crudBoard.write_comment(commentInfo)}

@router.post('/comment_likes/', tags = ['board'])
async def comment_likes(commentLikes: CommentLikes):
    return {'code': crudBoard.comment_likes(commentLikes)}

@router.post('/fastWrite/', tags = ['board'])
async def fast_write(fastWrite: FastWrite):
    return {'code': crudBoard.fast_write(fastWrite)}
