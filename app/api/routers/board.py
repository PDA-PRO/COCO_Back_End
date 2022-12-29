from fastapi import APIRouter
from crud.board import board_crud
from schemas.board import *
router = APIRouter()

@router.get('/board/', tags = ['board'])
async def check_board():
    return board_crud.check_board()

@router.get('/board/{board_id}', tags = ['board'] )
async def detail_board(board_id: int):
    return board_crud.board_detail(board_id)

@router.post('/board_likes/', tags = ['board'])
async def board_likes(boardLikes: BoardLikes):
    return {'code': board_crud.board_likes(boardLikes)}

@router.post('/comment/', tags = ['board'])
async def write_comment(commentInfo: CommentInfo):
    return {'code': board_crud.write_comment(commentInfo)}

@router.post('/comment_likes/', tags = ['board'])
async def comment_likes(commentLikes: CommentLikes):
    return {'code': board_crud.comment_likes(commentLikes)}

@router.post('/fastWrite/', tags = ['board'])
async def fast_write(fastWrite: FastWrite):
    return {'code': board_crud.fast_write(fastWrite)}

@router.post('/delete_content/', tags=['board'])
async def delete_content(board_id: DeleteBoard):
    return {'code': board_crud.delete_content(board_id)}

@router.post('/delete_comment/', tags=['board'])
async def delete_comment(comment_id: DeleteComment):
    return {'code': board_crud.delete_comment(comment_id)}
