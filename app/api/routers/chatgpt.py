from fastapi import APIRouter, Depends, security
from app.crud.chatgpt import crud_chatGPT
from app.core import security
from app.api.deps import get_cursor,DBCursor
from app.schemas.chatGPT import AskQ, CreateTask

router = APIRouter(prefix='/chatgpt')

@router.post("/", tags=['chatgpt'])
def get_answer(info: AskQ,db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: question 생성에 필요한 입력 데이터
        - content: user가 작성한 질문
        - code: user가 작성한 코드
        - room_id: question이 등록된 study room의 id
        - q_id: 답변이 달린 question id
    
    '''
    return crud_chatGPT.get_answer(db_cursor, info)

@router.post("/create_task", tags=['chatgpt'])
def create_task(info: CreateTask, db_cursor:DBCursor=Depends(get_cursor)):
    return crud_chatGPT.create_task(db_cursor, info)
