from fastapi import APIRouter,Depends
from crud.board import board_crud
from schemas.board import *
from core import security
router = APIRouter()

@router.get('/board/', tags = ['board'])
async def check_board():
    return board_crud.check_board()

@router.get('/board/{board_id}', tags = ['board'] )
async def detail_board(board_id: int):
    return board_crud.board_detail(board_id)

@router.post('/board_likes/', tags = ['board'])
async def board_likes(boardLikes: BoardLikes,token: dict = Depends(security.check_token)):
    return {'code': board_crud.board_likes(boardLikes)}

@router.post('/comment/', tags = ['board'])
async def write_comment(commentInfo: CommentInfo,token: dict = Depends(security.check_token)):
    return {'code': board_crud.write_comment(commentInfo)}

@router.post('/comment_likes/', tags = ['board'])
async def comment_likes(commentLikes: CommentLikes,token: dict = Depends(security.check_token)):
    return {'code': board_crud.comment_likes(commentLikes)}

@router.post('/write_board/', tags=['board'])
async def write_board(writeBoard: WriteBoard, token: dict = Depends(security.check_token)):
    return {'code': board_crud.write_board(writeBoard)}

@router.post('/delete_content/', tags=['board'])
async def delete_content(board_id: DeleteBoard,token: dict = Depends(security.check_token)):
    return {'code': board_crud.delete_content(board_id)}

@router.post('/delete_comment/', tags=['board'])
async def delete_comment(comment_id: DeleteComment,token: dict = Depends(security.check_token)):
    return {'code': board_crud.delete_comment(comment_id)}

@router.get('/boardlist', tags=['manage'])
async def boardlist():
    return board_crud.check_board()

@router.get('/deleteBoard/{board_id}', tags=['manage'])
async def deletetask(board_id):
    return board_crud.delete_content(board_id)

@router.post('/update_board/', tags=['board'])
async def update_board(updateBoard: UpdateBoard, token: dict = Depends(security.check_token)):
    return {'code': board_crud.update_board(updateBoard)} 

