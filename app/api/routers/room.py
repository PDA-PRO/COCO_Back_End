from fastapi import APIRouter, Depends, HTTPException
from app.crud.room import room_crud
from app.crud.submission import submission_crud
from app.schemas.room import *
from app.models.room import *
from app.core import security
from app.api.deps import get_cursor,DBCursor
from app.core.image import image
from app.crud.alarm import alarm_crud
import os

router = APIRouter(prefix='/rooms')

@router.get("/myroom", tags=['room'], response_model=list[MyRoom])
def myroom(token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 user가 속한 study room의 정보를 리턴

    - token : jwt
    '''
    return room_crud.myroom(db_cursor,token['id'])

@router.post("", tags=["room"],response_model=BaseResponse)
def create_room(info: CreateRoom,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    study room 생성

    params
    - info : study room 생성에 필요한 입력 데이터
        - name : 이름
        - desc : 간략한 설명
        - members : user들의 id
    - token : jwt
    -----------------------
    returns
    - code : 생성된 스터디룸 id
    '''
    security.check_tutor(token)
    return {"code":room_crud.create_room(db_cursor,info,token['id'])}

@router.get('', tags=['room'], response_model=RoomBaseOut)
def read_rooms(params:RoomBaseIn=Depends(), db_cursor:DBCursor=Depends(get_cursor)):
    '''
    모든 study room의 기본 정보 조회

    - params
        - query : 검색어
        - page 
        - size
    '''
    return room_crud.read_all_rooms(params,db_cursor)

@router.get("/{room_id}", tags=['room'],response_model=RoomDetail,response_model_exclude=['ranking'])
def get_room(room_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room의 정보를 리턴

    - room_id: 스터디룸 아이디
    - token : jwt
    '''
    security.check_tutee(db_cursor,room_id,token['id'])
    return room_crud.get_room(db_cursor,room_id)

@router.delete("/{room_id}", tags=["room"],response_model=BaseResponse)
def delete_room(room_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room 삭제 

    - room_id : 삭제할 room의 id
    - token : jwt
    '''
    security.check_leader(db_cursor,room_id,token['id'])

    return {"code":room_crud.delete_room(db_cursor,room_id)}

@router.put("/{room_id}/member", tags=["room"],response_model=BaseResponse)
def insert_members(room_id:int, user_id: str=Body(embed=True),token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room에 member를 추가

    - room_id : room id
    - user_id : user id
    - token : jwt
    '''
    security.check_leader(db_cursor,room_id,token['id'])
    try:
        room_crud.create(db_cursor,{'room_id':room_id,'user_id':user_id},table='room_ids')
        return {"code":1}
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{room_id}/member", tags=["room"],response_model=BaseResponse)
def delete_members(room_id:int, user_id: str=Body(embed=True),token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room에 member를 삭제

    - room_id : room id
    - user_id : user id
    - token : jwt
    '''
    security.check_leader(db_cursor,room_id,token['id'])
    try:
        room_crud.delete(db_cursor,table='room_ids',room_id=room_id,user_id=user_id)
        return {"code":1}
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/{room_id}/questions", tags=['room'],response_model=BaseResponse)
def create_question(room_id:int,info: CreateQuestion,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    Study room의 질문 생성
    
    - room_id: question이 등록될 study room의 id
    - info: question 생성에 필요한 입력 데이터
        - title : 질문 제목
        - question: user가 작성한 질문
        - code: user가 작성한 코드
    - token : jwt
    '''
    security.check_tutee(db_cursor,room_id,token['id'])
    return {"code":room_crud.write_question(db_cursor,room_id,info,token['id'])}

@router.get('/{room_id}/questions', tags=['room'],response_model=QuestionListOut)
def read_questions(room_id: int,pagination:PaginationIn=Depends(),token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 질문 리스트 조회

    - room_id
    - pagination
        - size
        - page
    - token :jwt
    '''
    security.check_tutee(db_cursor,room_id,token['id'])
    return room_crud.room_questions(db_cursor,room_id,pagination)

@router.post("/{room_id}/answer", tags=['room'],response_model=BaseResponse)
def create_answer(room_id: int,info: CreateAnswer,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    study room에 등록된 질문에 답변을 생성

    - room_id: 질문이 등록된 room id
    - info: answer 생성에 필요한 입력 데이터
        - q_id: 답변이 달릴 질문 id
        - answer: 답변
        - code: 코드
    - token: jwt
    '''
    security.check_tutee(db_cursor,room_id,token['id'])
    return {"code":room_crud.write_answer(db_cursor,room_id,info,token['id'])}

@router.post("/{room_id}/roadmaps", tags=['room'],response_model=BaseResponse)
def create_roadmap(room_id: int,info: RoadmapBody,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    Study room의 roadmap 생성
    
    - room_id: room id
    - info: roadmap 생성에 필요한 입력 데이터
        - name: roadmap 제목
        - desc: roadmap 메인 설명
        - tasks: 관련 문제 목록
    - token : jwt
    '''
    security.check_leader(db_cursor,room_id,token['id'])
    return {"code":room_crud.create_roadmap(db_cursor,room_id,info,token["id"])}

@router.get('/{room_id}/roadmaps', tags=['room'], response_model=RoadMapList)
def read_roadmap(room_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 모든 roadmap 정보 조회

    - room_id: room id
    - token : jwt
    '''
    security.check_tutee(db_cursor,room_id,token['id'])
    room_info=room_crud.read_roadmap(db_cursor,room_id)
    solved_task=submission_crud.get_solved(db_cursor,token['id'])
    return {
        "room_info" :room_info,
        "solved_task" : solved_task
    }

@router.put('/{room_id}/roadmaps/{roadmap_id}', tags=['room'],response_model=BaseResponse)
def update_roadmap(room_id:int,roadmap_id:int,info: RoadmapBody, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 roadmap 수정
    
    - room_id : 수정할 room id
    - roadmap_id: roadmap id
    - info: roadmap 수정에 필요한 입력 데이터
        - name: roadmap 제목
        - desc: roadmap 메인 설명
        - tasks: 관련 문제 목록
        - last_modify: 마지막 수정 시간 미입력 권장
    - token : jwt
    '''
    security.check_leader(db_cursor,room_id,token['id'])

    roadmap_table=f"`{str(room_id)}_roadmap`"
    roadmap_ids_table=f"`{str(room_id)}_roadmap_ids`"
    new_desc=image.save_update_image(os.path.join(os.getenv("ROADMAP_PATH"),"temp",token["id"]),os.path.join(os.getenv("ROADMAP_PATH"),f"{str(room_id)}_{str(roadmap_id)}"),info.desc,f"{str(room_id)}_{str(roadmap_id)}","su")
    room_crud.update(db_cursor,{"name":info.name,"`desc`":new_desc},"room",roadmap_table,id=roadmap_id)
    room_crud.delete(db_cursor,"room",roadmap_ids_table,roadmap_id=roadmap_id)
    for i in info.tasks:
        room_crud.create(db_cursor,{"roadmap_id":roadmap_id,"task_id":i},"room",roadmap_ids_table)

    # 스터디룸 로드맵 수정 시 알람
    room_name_sql = 'SELECT name FROM coco.room where id = %s;'
    room_name_data = (room_id)
    room_result = db_cursor.select_sql(room_name_sql, room_name_data)

    users_sql = 'SELECT user_id FROM coco.room_ids where room_id = %s;'
    users_data = (room_id)
    users_result = db_cursor.select_sql(users_sql, users_data)
    for result in users_result:
        user = result['user_id']    
        alarm_crud.create_alarm(
            db_cursor,
            {
                'sender': None,
                'receiver': user,
                'context': {
                    'room_id': room_id,
                    'room_name': room_result[0]['name'],
                    'roadmap_name': info.name,
                    'roadmap_id': roadmap_id
                    },
                'category': 10
            }
        )    
    return {"code":1}

@router.delete('/{room_id}/roadmaps/{roadmap_id}', tags=['room'],response_model=BaseResponse)
def delete_roadmap(room_id: int,roadmap_id:int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 study room에 등록된 roadmap 삭제

    - room_id: room id
    - roadmap_id: roadmap id
    - token : jwt
    '''
    security.check_leader(db_cursor,room_id,token['id'])
    return {"code":room_crud.delete_roadmap(db_cursor,room_id,roadmap_id)}

@router.get('/{room_id}/roadmaps/{roadmap_id}', tags=['room'])
def get_roadmap(room_id: int, roadmap_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 id의 study room의 특정 roadmap 정보 조회

    - room_id: room id
    - roadmap_id: roadmap id
    - token : jwt
    '''
    security.check_tutee(db_cursor,room_id,token['id'])
    return room_crud.get_roadmap(db_cursor,room_id, roadmap_id)

@router.put('/{room_id}/select-answer', tags=['room'],response_model=BaseResponse)
def select_answer(room_id: int,info: SelectAnswer, token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    '''
    해당 질문에 대한 답변을 채택함

    - room_id: int
    - info
        - a_id: int
        - select: int
    - token : jwt
    '''

    room_crud.select_answer(db_cursor, room_id,info,token['id'])
    # try: 
    #     room_crud.select_answer(db_cursor, info,token['id'])
    # except:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="권한이 없습니다.",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    return {"code":1}