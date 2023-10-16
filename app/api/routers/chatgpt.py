from fastapi import APIRouter, Depends, security, Form
from app.crud.chatgpt import crud_chatGPT
from app.core import security
from app.api.deps import get_cursor,DBCursor
from app.schemas.chatGPT import *

router = APIRouter(prefix='/ai')

@router.post("/ai-answer", tags=['ai'])
def ai_answer(info: AskQ, token: dict = Depends(security.check_token), db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: question 생성에 필요한 입력 데이터
        - content: user가 작성한 질문
        - code: user가 작성한 코드
        - room_id: question이 등록된 study room의 id
        - q_id: 답변이 달린 question id
    
    '''
    return crud_chatGPT.ai_answer(db_cursor, info)

@router.post("/create-task", tags=['ai'])
def create_task( info: CreateTask, db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: 처음 문제 생성 질문
        - content: 문제 생성 질문
    '''
    return crud_chatGPT.create_task(db_cursor, info)


@router.post("/upload-task", tags=['ai'])
def upload_task(description:str=Form(...),info: UploadAITask=Depends(), db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: 문제 생성 데이터
        - title: 문제 제목
        - inputDescription: 입력 예제 설명
        - inputEx1: 입력 예제 1
        - inputEx2: 입력 예제 2
        - outputDescription: 출력 예제 설명
        - outputEx1: 출력 예제 1
        - outputEx2: 출력 예제 2
        - diff: 난이도
        - timeLimit: 시간 제한
        - memLimit: 메모리 제한
        - category: 문제 카테고리, ','로 구문된 문자열
    - description: 문제 메인 설명
    '''
    return crud_chatGPT.upload_task(db_cursor, info, description)

@router.post("/ai-code", tags=["ai"], response_model=CodeImprovement)
def ai_code(info: AiCode, token: dict = Depends(security.check_token), db_cursor: DBCursor=Depends(get_cursor)):
    '''
    - info: AI의 코드 개선 추천
        - code: 사용자의 코드
        - task_id: 문제 id
        - submit_id: 제출 id
        
    '''
    return crud_chatGPT.ai_code(db_cursor, info)