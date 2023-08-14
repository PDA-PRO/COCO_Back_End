from fastapi import APIRouter, Depends
from schemas.user import UserListIn, UserListOut
from core import security
from crud.room import room
from crud.user import user_crud
from crud.submission import submission_crud
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

@router.get("/{room_id}", tags=['room'], )
async def get_room(room_id: int):
    '''
    해당 id의 study room의 정보를 리턴

    - room_id: 스터디룸 아이디
    '''
    return room.get_room(room_id)


@router.get("/myroom/{user_id}", tags=['room'], response_model=list[MyRoom])
async def myroom(user_id: str):
    '''
    해당 user가 속한 study room의 정보를 리턴
    '''
    return room.myroom(user_id)

@router.post("/question/", tags=['room'])
async def create_question(info: RoomQuestion):
    '''
    Study room의 질문 생성
    
    - info: question 생성에 필요한 입력 데이터
        - room_id: question이 등록될 study room의 id
        - question: user가 작성한 질문
        - code: user가 작성한 코드
        - writer: 질문 작성 user
    '''
    return room.write_question(info)

@router.get('/question/{room_id}', tags=['room'])
async def read_questions(room_id: int):
    '''
    해당 study room에 등록된 질문 리스트 조회
    '''
    return room.room_questions(room_id)

@router.post("/answer", tags=['room'])
async def create_answer(info: RoomAnswer):
    '''
    study room에 등록된 질문에 답변을 생성

    - info: answer 생성에 필요한 입력 데이터
        - room_id: 질문이 등록된 room id
        - q_id: 답변이 달릴 질문 id
        - answer: 답변
        - code: 코드
        - writer: 답변 작성자
    '''
    return room.write_answer(info)

@router.post("/roadmap", tags=['room'])
async def create_roadmap(info: RoomRoadMap):
    '''
    Study room의 roadmap 생성
    
    - info: roadmap 생성에 필요한 입력 데이터
        - room_id: room id
        - name: roadmap 제목
        - desc: roadmap 메인 설명
        - task_id: 관련 문제 목록
    '''
    return room.create_roadmap(info)

@router.get('/roadmap/{room_id}', tags=['room'], response_model=RoomRoadMapList)
async def read_roadmap(room_id: int,user_id:str):
    '''
    해당 study room에 등록된 모든 roadmap 정보 조회

    

    - room_id: room id
    - user_id: user id
    '''
    room_info=room.read_roadmap(room_id)
    solved_task=submission_crud.get_solved(user_id)
    return {
        "room_info" :room_info,
        "solved_task" : solved_task
    }

@router.delete('/roadmap/{room_id}', tags=['room'])
async def delete_roadmap(room_id: int,roadmap_id:int):
    '''
    해당 study room에 등록된 roadmap 삭제

    - room_id: room id
    - roadmap_id: roadmap id
    '''
    return room.delete_roadmap(room_id,roadmap_id)

@router.put('/roadmap/{room_id}/task', tags=['room'])
async def insert_roadmap_task(room_id: int,roadmap_id:int,task_id:int):
    '''
    해당 id의 study room의 roadmap에 task를 추가
        
    - room_id : room id
    - roadmap_id : roadmap id
    - task_id : task id
    '''
    return room.insert_roadmap_task(room_id,roadmap_id,task_id)

@router.delete('/roadmap/{room_id}/task', tags=['room'])
async def delete_roadmap_task(room_id: int,roadmap_id:int,task_id:int):
    '''
    해당 id의 study room의 roadmap에 task를 삭제

    - room_id : room id
    - roadmap_id : roadmap id
    - task_id : task id
    '''
    return room.delete_roadmap_task(room_id,roadmap_id,task_id)

@router.get('/search_user/', tags=['room'],response_model=UserListOut)
async def search_user(info: UserListIn=Depends()):
    """
    user의 id나 name으로 검색
    id, name, role 값 리턴

    - info
        - keyword : user의 id나 name | 값이 없을 시 모든 user 리스트 리턴
        - size : 한 페이지의 크기
        - page : 페이지
        - role : 0 -> 일반 유저 1-> 관리자
    """
    return user_crud.search_user(info)

@router.get('/roadmap/{room_id}/{roadmap_id}', tags=['room'])
async def get_roadmap(room_id: int, roadmap_id: int):
    '''
        해당 id의 study room의 특정 roadmap 정보를 가져옴

        - room_id: room id
        - roadmap_id: roadmap id
    '''
    return room.get_roadmap(room_id, roadmap_id)
