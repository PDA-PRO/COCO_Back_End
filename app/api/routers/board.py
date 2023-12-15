from fastapi import APIRouter,Depends
from app.crud.board import board_crud
from app.schemas.board import *
from app.core import security
from app.api.deps import get_cursor,DBCursor

router = APIRouter(prefix="/boards")

@router.post('', tags=['board'],response_model=BoardBase)
def create_board(info: BoardBody, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 게시글을 생성

    - info : 게시글의 요소들
        - title : 제목
        - context : 내용
        - category : 카테고리
        - code : 코드
    - token : 사용자 인증
    ------------------------
    returns
    - 성공시 생성된 게시글 반환
    """

    board_id=board_crud.create_board(db_cursor,info,token["id"])
    result=board_crud.read(db_cursor,id=board_id)[0]
    result['user_id'] = token["id"]
    return result

@router.get('', tags = ['board'],response_model=BoardListOut)
def read_boards(info:PaginationIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    게시글 정보 조회
    size와 page 존재할 시 pagination 적용
    
    - info 
        - size : 한 페이지의 크기
        - page : 현재 페이지의 번호
    '''
    if info.size and info.page:
        total,result=board_crud.read_with_pagination(db_cursor,size=info.size,page=info.page,sort=True)
        # 게시글 데이터에 작성자 추가
        for board in result:
            id = board['id']
            sql = "SELECT * FROM coco.boards_ids where board_id = %s;"
            data = (id)
            writer = db_cursor.select_sql(sql, data)
            board['user_id'] = writer[0]['user_id']
        return {"total":total,"size":info.size,"boardlist":result}
    else:
        result=board_crud.read(db_cursor,sort=True)
        # 게시글 데이터에 작성자 추가
        for board in result:
            id = board['id']
            sql = "SELECT * FROM coco.boards_ids where board_id = %s;"
            data = (id)
            writer = db_cursor.select_sql(sql, data)
            board['user_id'] = writer[0]['user_id']
        return {"boardlist":result}


@router.put("/{board_id}", tags=['board'])
def update_board(board_id:int,info: BoardBody,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    사용자가 작성한 게시글을 수정

    - board_id: 게시글 id
    - info: 게시글 수정에 필요한 정보
      - title: 게시글 타이틀
      - context: 게시글 본문
      - category: 게시글 카테고리
      - code: 코드
    '''
    return board_crud.update_board(db_cursor, board_id, info)

@router.get('/{board_id}', tags = ['board'],response_model=BoardDetail)
def detail_board(board_id: int,user_id:str=None,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    특정 게시글 상세 정보 조회

    - board_id : 게시글 id
    - user_id : 조회를 요청한 유저의 id
    '''
    return board_crud.board_detail(db_cursor,board_id,user_id)

@router.delete('/{board_id}', tags=['board'],response_model=BaseResponse)
def delete_board(board_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    게시글 삭제

    - board_id : board id
    - token : 사용자 인증
    """
    if not board_crud.read(db_cursor,['user_id'],table="boards_ids",board_id=board_id,user_id=token["id"]):
        security.check_admin(token)

    return {'code': board_crud.delete_board(db_cursor,board_id)}

@router.patch('/{board_id}/likes', tags = ['board'],response_model=BaseResponse)
def update_board_likes(board_id:int,like_type:bool,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    게시글의 좋아요 업데이트

    - board_id : board id
    - like_type: True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_board_likes(db_cursor,board_id,like_type,token['id'])}

@router.post('/{board_id}/comments', tags = ['board'],response_model=CommentBase)
def create_comment(board_id: int,commentInfo: CreateComment,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    새로운 댓글을 생성
    댓글 생성에 성공하면 성공한 댓글 리턴

    - board_id : board id
    - commentInfo : 댓글의 요소
        - context : 댓글 내용
    - token : 사용자 인증
    ----------------------
    returns
    - 새로 생성된 댓글
    """
    board_crud.create_comment(db_cursor,board_id,commentInfo,token['id'])
    res=board_crud.read_comment(db_cursor,board_id,token['id'])[0]
    return res

@router.get('/{board_id}/comments', tags = ['board'],response_model=list[CommentBase])
def read_comments(board_id: int,user_id:str=None,db_cursor:DBCursor=Depends(get_cursor)):
    """
    특정 게시글의 댓글 조회

    - board_id : 게시글 id
    - user_id : 조회를 요청한 유저의 id
    """
    return board_crud.read_comment(db_cursor,board_id,user_id)

@router.delete('/{board_id}/comments/{comment_id}', tags=['board'],response_model=BaseResponse)
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

@router.patch('/{board_id}/comments/{comment_id}/likes', tags = ['board'],response_model=BaseResponse)
def update_comment_likes(board_id: int,comment_id: int,like_type:bool,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    댓글의 좋아요 업데이트

    - board_id : board id
    - comment_id : comment id
    - like_type : True = 감소 , False = 증가
    - token : 사용자 인증
    """
    return {'code': board_crud.update_comment_likes(db_cursor,board_id,comment_id,like_type,token['id'])}



