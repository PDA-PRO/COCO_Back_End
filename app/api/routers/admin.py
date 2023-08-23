from schemas.common import PaginationIn
from schemas.user import UpdateRole, UserList, UserListIn, UserListOut
from schemas.task import  TaskListWithCount
from schemas.board import  BoardListOut
from schemas.admin import Notice
from fastapi import APIRouter,Depends, HTTPException, status
from core.admin import check
from crud.task import task_crud
from crud.user import user_crud
from crud.board import board_crud
from api.deps import get_cursor,DBCursor

router = APIRouter(prefix="/manage")

@router.get("/tasklist", tags = ['admin'],response_model=TaskListWithCount)
async def read_task_with_count(info:PaginationIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    간단한 문제 목록 조회
    문제별 제출 회수 포함

    - info
        - size : 한 페이지의 크기
        - page : 페이지 번호
    """
    return task_crud.read_task_with_count(db_cursor,info)

@router.get("/notice",tags=["admin"])
async def get_notice():
    """
    공지사항 조회
    """
    result=check.get_notice()
    if result==None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 로드 중 오류 발생"
        )
    return result

@router.put('/notice', tags=["admin"])
async def update_notice(content: Notice):
    """
    공지사항 업데이트

    - content
        - html : html형식의 공지사항 내용
    """
    result=check.update_notice(content.html)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="공지사항 파일 업데이트 중 오류 발생"
        )
    
@router.get("/user/", tags=['admin'],response_model=UserListOut)
async def search_user(info : UserListIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    user의 id나 name으로 검색
    id, name, role 값 리턴

    - info
        - keyword : user의 id나 name | 값이 없을 시 모든 user 리스트 리턴
        - size : 한 페이지의 크기
        - page : 페이지
        - role : 0 -> 일반 유저 1-> 관리자
    """
    return user_crud.search_user(db_cursor,info)

@router.patch("/role", tags=["admin"])
async def update_role(info : UpdateRole,db_cursor:DBCursor=Depends(get_cursor)):
    """
    해당 user의 role 업데이트

    - info 
        - id : id
        - role : role | 0 -> 일반 유저 1 -> 관리자
    """
    return user_crud.update_role(db_cursor,info)

@router.get("/manager/", tags=["admin"],response_model=list[UserList])
async def read_manager(db_cursor:DBCursor=Depends(get_cursor)):
    """
    모든 관리자 조회

    """
    return user_crud.read_manager(db_cursor)
        
@router.get('/post', tags = ['admin'],response_model=BoardListOut)
async def read_board_with_pagination(info:PaginationIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    게시글 정보 조회
    
    - info 
        - size : 한 페이지의 크기
        - page : 현재 페이지의 번호
    '''
    return board_crud.read_board_with_pagination(db_cursor,info)