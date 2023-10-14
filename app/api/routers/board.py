from fastapi import APIRouter,Depends, HTTPException
from app.crud.board import board_crud
from app.schemas.board import *
from app.core import security
from app.api.deps import get_cursor,DBCursor

router = APIRouter(prefix="/board")

@router.post('/', tags=['board'],response_model=BoardBase)
def create_board(writeBoard: CreateBoard, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 게시글을 생성

    - writeBoard : 게시글의 요소들
        - title : 제목
        - context : 내용
        - category : 카테고리
        - code : 코드
    - token : 사용자 인증
    ------------------------
    returns
    - 성공시 게시글 id 반환
    """

    board_id=board_crud.create_board(db_cursor,writeBoard,token["id"])
    result=board_crud.read(db_cursor,id=board_id)[0]
    return result

@router.get('/', tags = ['board'],response_model=BoardListOut)
def read_board(info:PaginationIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    게시글 정보 조회
    size와 page 존재할 시 pagination 적용
    
    - info 
        - size : 한 페이지의 크기
        - page : 현재 페이지의 번호
    '''
    if info.size and info.page:
        total,result=board_crud.read_with_pagination(db_cursor,size=info.size,page=info.page,sort=True)
        for board in result:
            id = board['id']
            sql = "SELECT * FROM coco.boards_ids where board_id = %s;"
            data = (id)
            writer = db_cursor.select_sql(sql, data)
            board['user_id'] = writer[0]['user_id']
        print(result)
        return {"total":total,"size":info.size,"boardlist":result}
    else:
        result=board_crud.read(db_cursor,sort=True)
        for board in result:
            id = board['id']
            sql = "SELECT * FROM coco.boards_ids where board_id = %s;"
            data = (id)
            writer = db_cursor.select_sql(sql, data)
            board['user_id'] = writer[0]['user_id']
        print(result)
        return {"boardlist":result}

@router.get('/{board_id}', tags = ['board'],response_model=BoardDetail)
def detail_board(board_id: int,user_id:str=None,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    특정 게시글 상세 정보 조회

    - board_id : 게시글 id
    - user_id : 조회를 요청한 유저의 id
    '''
    return board_crud.board_detail(db_cursor,board_id,user_id)

@router.delete('/', tags=['board'],response_model=BaseResponse)
def delete_board(board_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    게시글 삭제

    - board_id : board id
    - token : 사용자 인증
    """
    if not board_crud.read(db_cursor,['user_id'],table="boards_ids",board_id=board_id,user_id=token["id"]):
        security.check_admin(token)

    return {'code': board_crud.delete_board(db_cursor,board_id)}

@router.patch('/likes/', tags = ['board'],response_model=BaseResponse)
def update_board_likes(boardLikes: LikesBase,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    게시글의 좋아요 업데이트

    - boardLikes : 게시글의 요소들
        - board_id : board id
        - type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_board_likes(db_cursor,boardLikes,token['id'])}

@router.post('/comment/', tags = ['board'],response_model=CommentBase)
def create_comment(commentInfo: CreateComment,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 댓글을 생성
    댓글 생성에 성공하면 성공한 댓글 리턴

    - commentInfo : 댓글의 요소
        - context : 댓글 내용
        - board_id : board id
    - token : 사용자 인증
    ----------------------
    returns
    - 새로 생성된 댓글
    """
    board_crud.create_comment(db_cursor,commentInfo,token['id'])
    res=board_crud.read_comment(db_cursor,commentInfo.board_id,token['id'])[0]
    return res

@router.get('/comment/', tags = ['board'],response_model=list[CommentBase])
def read_comment(board_id: int,user_id:str=None,db_cursor:DBCursor=Depends(get_cursor)):
    """
    특정 게시글의 댓글 조회

    - board_id : 게시글 id
    - user_id : 조회를 요청한 유저의 id
    """
    return board_crud.read_comment(db_cursor,board_id,user_id)

@router.delete('/comment/', tags=['board'],response_model=BaseResponse)
def delete_comment(board_id: int,comment_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    댓글 삭제

    - board_id : board id
    - comment_id : comment id
    - token : 사용자 인증
    """
    if not board_crud.read(db_cursor,['user_id'],table="comments_ids",board_id=board_id,user_id=token["id"],comment_id=comment_id):
        security.check_admin(token)
        
    return {'code': board_crud.delete_comment(db_cursor,board_id,comment_id)}

@router.patch('/comment/likes/', tags = ['board'],response_model=BaseResponse)
def update_comment_likes(commentLikes: CommentLikes,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    댓글의 좋아요 업데이트

    - commentLikes : 댓글의 요소들
        - board_id : board id
        - comment_id : comment id
        - type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_comment_likes(db_cursor,commentLikes,token['id'])}



