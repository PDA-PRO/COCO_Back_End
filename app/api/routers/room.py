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

@router.get('/', tags=['room'],response_model=list[RoomBase])
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

@router.get("/myroom/{user_id}", tags=['room'])
async def myroom(user_id: str):
    return room.myroom(user_id)
 
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

@router.get("/{room_id}/", tags=['room'])
async def get_room(room_id: int):
    return room.get_room(room_id)

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

@router.get("/room_apply/{room_id}/", tags=["room"])
async def room_apply(room_id: int):
    return room.room_apply(room_id)

@router.post("/reject_apply/", tags=["room"])
async def reject_apply(info: RoomMember):
    return room.reject_apply(info)