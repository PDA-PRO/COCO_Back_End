from fastapi import APIRouter, Depends, security, Form
from app.crud.ai import crud_ai
from app.core import security
from app.api.deps import get_cursor,DBCursor
from app.schemas.ai import *

router = APIRouter(prefix='/ai')

@router.get("/status", tags=['ai'])
def ai_status(db_cursor:DBCursor=Depends(get_cursor)):
    '''
    ai 플러그인 on/off 여부 확인
    '''
    return check_status(db_cursor)

def check_status(db_cursor):
    return db_cursor.select_sql("select * from `plugin`.`status`;", ())[0]


@router.put("/status", tags=['ai'])
def update_status(info: AiStatus, db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: ai plugin on/off 설정
        - plugin: ai 종류
        - status: on/off 여부
    '''
    data = (info.status)
    if info.plugin == 'wpc':
        sql = "UPDATE `plugin`.`status` SET `wpc` = %s"
        db_cursor.execute_sql(sql, data)
    elif info.plugin == 'similar':
        sql = "UPDATE `plugin`.`status` SET `similar` = %s"
        db_cursor.execute_sql(sql, data)
    else:
        sql = "UPDATE `plugin`.`status` SET `qa` = %s"
        db_cursor.execute_sql(sql, data)
        sql = "UPDATE `plugin`.`status` SET `task` = %s"
        db_cursor.execute_sql(sql, data)
        sql = "UPDATE `plugin`.`status` SET `efficient` = %s"
        db_cursor.execute_sql(sql, data)

@router.post("/ai-answer", tags=['ai'])
def ai_answer(info: AskQ, token: dict = Depends(security.check_token), db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: question 생성에 필요한 입력 데이터
        - content: user가 작성한 질문
        - code: user가 작성한 코드
        - room_id: question이 등록된 study room의 id
        - q_id: 답변이 달린 question id
    
    '''
    status = check_status(db_cursor)['qa']
    if status == 0:
        return ModuleNotFoundError
    else:
        return crud_ai.ai_answer(db_cursor, info)

@router.post("/create-task", tags=['ai'])
def create_task( info: CreateTask, db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: 처음 문제 생성 질문
        - content: 문제 생성 질문
    '''
    status = check_status(db_cursor)['task']
    if status == 0:
        return ModuleNotFoundError
    else:
        return crud_ai.create_task(db_cursor, info)


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
    return crud_ai.upload_task(db_cursor, info, description)

@router.post("/ai-code", tags=["ai"], response_model=CodeImprovement)
def ai_code(info: AiCode, token: dict = Depends(security.check_token), db_cursor: DBCursor=Depends(get_cursor)):
    '''
    - info: AI의 코드 개선 추천
        - code: 사용자의 코드
        - task_id: 문제 id
        - sub_id: 제출 id
        
    '''
    status = check_status(db_cursor)['efficient']
    if status == 0:
        return ModuleNotFoundError
    else:
        return crud_ai.ai_code(db_cursor, info)

@router.put("/code-select", tags=['ai'])
def code_select(info: CodeSelect, token: dict = Depends(security.check_token), db_cursor: DBCursor=Depends(get_cursor)):
    '''
    - info: AI 코드 개선 채택
        - task_id: 문제 id
        - sub_id: 제출 id
        - check: 채택 여부
    '''
    return crud_ai.code_select(db_cursor, info)