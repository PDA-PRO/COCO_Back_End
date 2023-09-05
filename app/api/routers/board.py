from fastapi import APIRouter,Depends
from crud.board import board_crud
from schemas.board import *
from core import security


# import os
# import pymysql.cursors
# from pymysql import converters
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# converions = converters.conversions
# converions[pymysql.FIELD_TYPE.BIT] = lambda x: False if x == b'\x00' else True

router = APIRouter(prefix="/board")



# @router.get("/tmp", tags=['board'])
# def tmp():
#     user = query_get("""
#         SELECT * FROM coco.user;
#         """, ())
#     return JSONResponse(status_code=200, content=jsonable_encoder(user))

# def init_connection():
#     connection = pymysql.connect(host=os.getenv("DATABASE_HOST"),
#                                  port=3306,
#                                  user=os.environ.get("DATABASE_USERNAME"),
#                                  password=os.environ.get("DATABASE_PASSWORD"),
#                                  database=os.environ.get("DATABASE"),
#                                  cursorclass=pymysql.cursors.DictCursor,
#                                  conv=converions)
#     return connection

# def query_get(sql, param):
#     connection = init_connection()
#     with connection:
#         with connection.cursor() as cursor:
#             cursor.execute(sql, param)
#             return cursor.fetchall()

@router.post('/', tags=['board'])
async def create_board(writeBoard: CreateBoard, token: dict = Depends(security.check_token)):
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
    return {'code': board_crud.create_board(writeBoard)}

@router.get('/', tags = ['board'],response_model=list[BoardBase])
async def read_board():
    '''
    게시글 정보 조회
    '''
    return board_crud.read_board()

@router.get('/{board_id}', tags = ['board'],response_model=BoardDetail)
async def detail_board(board_id: int,user_id:str=None):
    '''
    특정 게시글 상세 정보 조회

    - board_id : 게시글 id
    - user_id : 조회를 요청한 유저의 id
    '''
    return board_crud.board_detail(board_id,user_id)

@router.delete('/', tags=['board'])
async def delete_board(board_id: int,token: dict = Depends(security.check_token)):
    """
    게시글 삭제

    - board_id : board id
    - token : 사용자 인증
    """
    return {'code': board_crud.delete_board(board_id)}

@router.patch('/likes/', tags = ['board'])
async def update_board_likes(boardLikes: LikesBase,token: dict = Depends(security.check_token)):
    """
    게시글의 좋아요 업데이트

    - boardLikes : 게시글의 요소들
        - user_id : user id
        - board_id : board id
        - type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_board_likes(boardLikes)}

@router.post('/comment/', tags = ['board'])
async def create_comment(commentInfo: CreateComment,token: dict = Depends(security.check_token)):
    """
    새로운 댓글을 생성

    - commentInfo : 댓글의 요소들
        - user_id : user id
        - context : 댓글 내용
        - board_id : board id
    - token : 사용자 인증
    """
    return {'code': board_crud.create_comment(commentInfo)}

@router.delete('/comment/', tags=['board'])
async def delete_comment(board_id: int,comment_id: int,token: dict = Depends(security.check_token)):
    """
    댓글 삭제

    - board_id : board id
    - comment_id : comment id
    - token : 사용자 인증
    """
    return {'code': board_crud.delete_comment(board_id,comment_id)}

@router.patch('/comment/likes/', tags = ['board'])
async def update_comment_likes(commentLikes: CommentLikes,token: dict = Depends(security.check_token)):
    """
    댓글의 좋아요 업데이트

    - commentLikes : 댓글의 요소들
        - user_id : user id
        - board_id : board id
        - comment_id : comment id
        - type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_comment_likes(commentLikes)}



