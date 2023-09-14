from fastapi import APIRouter,Depends
from app.crud.board import board_crud
from app.schemas.board import *
from app.core import security
from app.api.deps import get_cursor,DBCursor

router = APIRouter(prefix="/board")

@router.post('/', tags=['board'])
def create_board(writeBoard: CreateBoard, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 게시글을 생성

    - writeBoard : 게시글의 요소들
        - user_id : user id
        - title : 제목
        - context : 내용
        - category : 카테고리
        - code : 코드
    - token : 사용자 인증
    """
    return {'code': board_crud.create_board(db_cursor,writeBoard)}

@router.get('/', tags = ['board'],response_model=list[BoardBase])
def read_board(db_cursor:DBCursor=Depends(get_cursor)):
    '''
    게시글 정보 조회
    '''
    return board_crud.read_board(db_cursor)

@router.get('/{board_id}', tags = ['board'],response_model=BoardDetail)
def detail_board(board_id: int,user_id:str=None,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    특정 게시글 상세 정보 조회

    - board_id : 게시글 id
    - user_id : 조회를 요청한 유저의 id
    '''
    return board_crud.board_detail(db_cursor,board_id,user_id)

@router.delete('/', tags=['board'])
def delete_board(board_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    게시글 삭제

    - board_id : board id
    - token : 사용자 인증
    """
    return {'code': board_crud.delete_board(db_cursor,board_id)}

@router.patch('/likes/', tags = ['board'])
def update_board_likes(boardLikes: LikesBase,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    게시글의 좋아요 업데이트

    - boardLikes : 게시글의 요소들
        - user_id : user id
        - board_id : board id
        - type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_board_likes(db_cursor,boardLikes)}

@router.post('/comment/', tags = ['board'])
def create_comment(commentInfo: CreateComment,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 댓글을 생성

    - commentInfo : 댓글의 요소들
        - user_id : user id
        - context : 댓글 내용
        - board_id : board id
    - token : 사용자 인증
    """
    return {'code': board_crud.create_comment(db_cursor,commentInfo)}

@router.delete('/comment/', tags=['board'])
def delete_comment(board_id: int,comment_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    댓글 삭제

    - board_id : board id
    - comment_id : comment id
    - token : 사용자 인증
    """
    return {'code': board_crud.delete_comment(db_cursor,board_id,comment_id)}

@router.patch('/comment/likes/', tags = ['board'])
def update_comment_likes(commentLikes: CommentLikes,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    댓글의 좋아요 업데이트

    - commentLikes : 댓글의 요소들
        - user_id : user id
        - board_id : board id
        - comment_id : comment id
        - type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_comment_likes(db_cursor,commentLikes)}



