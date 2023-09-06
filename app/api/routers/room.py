from fastapi import APIRouter, Depends, HTTPException
from schemas.user import UserListIn, UserListOut
from crud.room import room
from crud.user import user_crud
from crud.submission import submission_crud
from schemas.room import *
from models.room import *
from core import security
from api.deps import get_cursor,DBCursor
from core.image import image
import os

router = APIRouter(prefix='/room')
# 전체 그룹 리스트(그룹명, 설명)

@router.post("/", tags=["room"])
async def create_room(info: CreateRoom,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    study room 생성

    - info : study room 생성에 필요한 입력 데이터
        - name : 이름
        - desc : 간략한 설명
        - leader : 만든 user id
        - members : user들의 id
    '''
    return room.create_room(db_cursor,info)

@router.get('/', tags=['room'], response_model=RoomBaseOut)
async def read_rooms(params:RoomBaseIn=Depends(), db_cursor:DBCursor=Depends(get_cursor)):
    '''
    모든 study room의 기본 정보 조회
    '''
    return room.read_all_rooms(params,db_cursor)

@router.delete("/", tags=["room"])
async def delete_room(room_id: int,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room 삭제 

    - room_id : 삭제할 room의 id
    '''
    return room.delete_room(db_cursor,room_id)

@router.put("/member/", tags=["room"])
async def insert_members(members: RoomMember,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room에 member를 추가

    - members : 추가할 room의 id
        - room_id : room id
        - user_id : user id
    '''
    try:
        room.insert_members(db_cursor,members)
        return True
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/member/", tags=["room"])
async def delete_members(members: RoomMember,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room에 member를 삭제

    - members : 삭제할 room의 id
        - room_id : room id
        - user_id : user id
    '''
    return room.delete_members(db_cursor,members)

@router.get("/{room_id}", tags=['room'], )
async def get_room(room_id: int,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room의 정보를 리턴

    - room_id: 스터디룸 아이디
    '''
    return room.get_room(db_cursor,room_id)


@router.get("/myroom/{user_id}", tags=['room'], response_model=list[MyRoom])
async def myroom(user_id: str,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 user가 속한 study room의 정보를 리턴
    '''
    return room.myroom(db_cursor,user_id)

@router.post("/question/", tags=['room'])
async def create_question(info: RoomQuestion,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    Study room의 질문 생성
    
    - info: question 생성에 필요한 입력 데이터
        - room_id: question이 등록될 study room의 id
        - question: user가 작성한 질문
        - code: user가 작성한 코드
        - writer: 질문 작성 user
    '''
    return room.write_question(db_cursor,info)

@router.get('/question/{room_id}', tags=['room'],response_model=QuestionListOut)
async def read_questions(room_id: int,pagination:PaginationIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 질문 리스트 조회
    '''
    return room.room_questions(db_cursor,room_id,pagination)

@router.post("/answer", tags=['room'])
async def create_answer(info: RoomAnswer,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    study room에 등록된 질문에 답변을 생성

    - info: answer 생성에 필요한 입력 데이터
        - room_id: 질문이 등록된 room id
        - q_id: 답변이 달릴 질문 id
        - answer: 답변
        - code: 코드
        - writer: 답변 작성자
    '''
    return room.write_answer(db_cursor,info)

@router.post("/roadmap", tags=['room'])
async def create_roadmap(info: RoomRoadMap,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    Study room의 roadmap 생성
    
    - info: roadmap 생성에 필요한 입력 데이터
        - id: room id
        - name: roadmap 제목
        - desc: roadmap 메인 설명
        - tasks: 관련 문제 목록
    '''
    return room.create_roadmap(db_cursor,info,token["id"])

@router.get('/roadmap/{room_id}', tags=['room'], response_model=RoomRoadMapList)
async def read_roadmap(room_id: int,user_id:str,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 모든 roadmap 정보 조회

    - room_id: room id
    - user_id: user id
    '''
    room_info=room.read_roadmap(db_cursor,room_id)
    solved_task=submission_crud.get_solved(db_cursor,user_id)
    return {
        "room_info" :room_info,
        "solved_task" : solved_task
    }

@router.put('/roadmap/', tags=['room'])
async def update_roadmap(info: RoomRoadMap,roadmap_id:int, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 모든 roadmap 수정
    
    - info: roadmap 수정에 필요한 입력 데이터
        - id: room id
        - name: roadmap 제목
        - desc: roadmap 메인 설명
        - tasks: 관련 문제 목록
    - roadmap_id : 수정할 roadmap id
    '''
    roadmap_table=f"`{str(info.id)}_roadmap`"
    roadmap_ids_table=f"`{str(info.id)}_roadmap_ids`"
    new_desc=image.save_update_image(os.path.join(os.getenv("ROADMAP_PATH"),"temp",token["id"]),os.path.join(os.getenv("ROADMAP_PATH"),f"{str(info.id)}_{str(roadmap_id)}"),info.desc,f"{str(info.id)}_{str(roadmap_id)}","su")
    room.update(db_cursor,{"name":info.name,"`desc`":new_desc},"room",roadmap_table,id=roadmap_id)
    room.delete(db_cursor,"room",roadmap_ids_table,roadmap_id=roadmap_id)
    for i in info.tasks:
        room.create(db_cursor,{"roadmap_id":roadmap_id,"task_id":i},"room",roadmap_ids_table)

    return 1

@router.delete('/roadmap/{room_id}', tags=['room'])
async def delete_roadmap(room_id: int,roadmap_id:int,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 roadmap 삭제

    - room_id: room id
    - roadmap_id: roadmap id
    '''
    return room.delete_roadmap(db_cursor,room_id,roadmap_id)

@router.get('/search_user/', tags=['room'],response_model=UserListOut)
async def search_user(info: UserListIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
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

@router.get('/roadmap/{room_id}/{roadmap_id}', tags=['room'])
async def get_roadmap(room_id: int, roadmap_id: int,db_cursor:DBCursor=Depends(get_cursor)):
    '''
        해당 id의 study room의 특정 roadmap 정보를 가져옴

        - room_id: room id
        - roadmap_id: roadmap id
    '''
    return room.get_roadmap(db_cursor,room_id, roadmap_id)

@router.post('/tutor-request', tags=['room'])
def create_tutor_request(user_id:str,reason:str="",db_cursor:DBCursor=Depends(get_cursor)):
    '''
        해당 id의 study room의 특정 roadmap 정보를 가져옴

        - room_id: room id
        - roadmap_id: roadmap id
    '''
    room.create(db_cursor,{"reason":reason,"user_id":user_id},table="user_tutor")
    return 1