from fastapi import APIRouter, Depends
from core import security
from crud.room import room
from schemas.room import *
from models.room import *

router = APIRouter(prefix='/room')
# 전체 그룹 리스트(그룹명, 설명)

@router.post("/", tags=["room"])
async def create_room(info: CreateRoom):
    '''
    study room 생성

    - info : study room 생성에 필요한 입력 데이터
        - name : 이름
        - desc : 간략한 설명
        - leader : 만든 user id
        - members : user들의 id
    '''
    return room.create_room(info)

@router.get('/', tags=['room'], response_model=list[RoomBase])
async def read_rooms():
    '''
    모든 study room의 기본 정보 조회
    '''
    return room.read_all_rooms()

@router.delete("/", tags=["room"])
async def delete_room(room_id: int):
    '''
    해당 id의 study room 삭제 

    - room_id : 삭제할 room의 id
    '''
    return room.delete_room(room_id)

@router.put("/member/", tags=["room"])
async def insert_members(members: RoomMember):
    '''
    해당 id의 study room에 member를 추가

    - members : 추가할 room의 id
        - room_id : room id
        - user_id : user id
    '''
    return room.insert_members(members)

@router.delete("/member/", tags=["room"])
async def delete_members(members: RoomMember):
    '''
    해당 id의 study room에 member를 삭제

    - members : 삭제할 room의 id
        - room_id : room id
        - user_id : user id
    '''
    return room.delete_members(members)

@router.get("/{room_id}/", tags=['room'], )
async def get_room(room_id: int):
    '''
    해당 id의 study room의 정보를 리턴
        - 'room_id': 스터디룸 아이디
        - 'name': 스터디룸 이름
        - 'desc': 스터디룸 설명
        - 'leader': 튜터
        - 'members': 튜티 리스트
        - 'exp': 전체 멤버 exp 총합
    '''
    return room.get_room(room_id)


@router.get("/myroom/{user_id}", tags=['room'], response_model=list[RoomBase])
async def myroom(user_id: str):
    '''
    해당 user가 속한 study room의 정보를 리턴
    '''
    return room.myroom(user_id)

@router.post("/write_question/", tags=['room'])
async def write_question(info: RoomQuestion):
    '''
    Study room의 질문 생성
    
    - info: question 생성에 필요한 입력 데이터
        - room_id: question이 등록될 study room의 id
        - question: user가 작성한 질문
        - code: user가 작성한 코드
        - writer: 질문 작성 user
    '''
    return room.write_question(info)

@router.get('/questions/{room_id}', tags=['room'])
async def room_questions(room_id: int):
    '''
    해당 study room에 등록된 질문 리스트 리턴
    '''
    return room.room_questions(room_id)


 
@router.get("/userlist/", tags=["room"])
async def userlist():
    return room.userlist()



@router.post("/search_user/", tags=["room"])
async def search_user(info: UserID):
    return room.search_user(info.user_id)

@router.post("/leave_room/", tags=["room"])
async def leave_room(info: RoomMember):
    return room.leave_room(info)



@router.post("/invite_member/", tags=["room"])
async def invite_member(info: RoomMember):
    return room.invite_member(info)



@router.get("/board/{room_id}", tags=["room"])
async def room_boardlist(room_id: int):
    return room.room_boardlist(room_id)

@router.get("/room_workbooks/{room_id}", tags=["room"])
async def room_workbooks(room_id: int):
    return room.room_workbooks(room_id)

@router.post("/add_problem", tags=["room"])
async def add_problem(info: RoomProblem):
    return room.add_problem(info)

@router.post("/delete_problem", tags=["room"])
async def delete_problem(info: RoomProblem):
    return room.delete_problem(info)

@router.post("/check_member/", tags=["room"])
async def is_my_room(info: RoomMember):
    return room.is_my_room(info)

@router.post("/join_room/", tags=["room"])
async def join_room(info: JoinRoom):
    return room.join_room(info)

# @router.get("/room_leader/{room_id}/", tags=["room"])
# async def room_leader(room_id: int):
#     return room.room_leader(room_id)
