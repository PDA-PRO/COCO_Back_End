from fastapi import APIRouter, Depends, HTTPException
from app.core import security
from app.schemas.submission import *
from app.core.celery_worker import process_sub
from app.crud.submission import submission_crud
from app.api.deps import get_cursor,DBCursor
import json
import os
router = APIRouter()

@router.post("/submissions", tags=["submission"],response_model=BaseResponse)
def scoring(submit:Submit,token: dict = Depends(security.check_token),db_cursor=Depends(get_cursor)):
    """
    제출된 코드 채점

    - submit
        - taskid
        - sourcecode
        - callbackurl
        - lang : 파이썬 0 | c 1 | c++ 2 | java 3
    - token :jwt
    """
    sub_id=submission_crud.create_sub(db_cursor,submit,token['id'])
    #클라이언트와 celery worker 간에 전송되는 데이터는 직렬화되어야 하기 때문에 db_cursor 객체를 넘기지 못한다.
    process_sub.apply_async([submit.taskid,submit.sourcecode,sub_id,submit.lang,token['id']])

    return {"code": 1}

@router.get("/submissions/{sub_id}", tags=["submission"],response_model=SubResult|None)
def load_result(sub_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    제출된 코드 채점 결과 조회
    조회를 요청하는 유저가 제출하거나 맞은 문제에 대한 제출결과만 조회 가능
    lint 도구를 이용한 분석 결과도 포함 없으면 빈 리스트 

    params
    - sub_id : 제출 id
    - token : jwt
    --------------------------------------------------------
    returns
    - subDetail : 채점 결과
    - lint : lint 도구로 분석한 결과 리스트
    """
    sub_info=submission_crud.read(db_cursor,["task_id","user_id"],table="sub_ids",sub_id=sub_id)
    if sub_info:
        if token['role'] or sub_info[0]['user_id']==token['id'] or sub_info[0]['task_id'] in submission_crud.get_solved(db_cursor,token['id']):
            rows=submission_crud.read_sub(db_cursor,sub_id)
            lang_list=submission_crud.read(db_cursor,["id","name"],"coco","lang")
            lang_dict={}
            for i in lang_list:
                lang_dict[i['id']]=i["name"]
            if len(rows):
                rows[0]['lang']=lang_dict[rows[0]['lang']]
                return {'subDetail':rows[0], 'lint': read_lint(sub_id)}
            else:
                return None
    
    raise HTTPException(
            status_code=403,
            detail="Insufficient permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )



@router.get("/submissions", tags=["submission"],response_model=StatusListOut)
def read_status(info:StatusListIn=Depends(),db_cursor:DBCursor=Depends(get_cursor)):
    """
    제출 조회

    - info
        - size: 한 페이지의 크기
        - page: 현재 페이지 번호
        - task_id: 문제 id 
        - lang: 제출 코드 언어 0 -> 파이썬 1-> c언어
        - onlyme : 내 제출만 보기 여부
        - user_id
        - answer: status가 3("정답") 인지 여부
    """
    status_list=submission_crud.read_status(db_cursor,info)
    lang_list=submission_crud.read(db_cursor,["id","name"],"coco","lang")
    lang_dict={}
    for i in lang_list:
        lang_dict[i['id']]=i["name"]
    for i in status_list['statuslist']:
        i['lang']=lang_dict[i['lang']]
    return status_list
    
def read_lint(sub_id:int)->list:
    """
    오답 제출 코드에 대해 pylint 분석 결과 조회
    TC틀림 오답코드 제외

    params
    - sub_id : 제출 id
    ------------------------------------
    returns
    - pylint 분석 결과 리스트 
    """
    err_msg = []
    lint_path=os.path.join(os.getenv("LINT_PATH"),str(sub_id)+".json")
    if not os.path.exists(lint_path):
        return []
    with open(os.path.join(os.getenv("LINT_PATH"),str(sub_id)+".json"), 'r') as file:
        datas = json.load(file)
        for data in datas:
            err_msg.append({
                'type': data['type'],
                'line': data['line'],
                'column': data['column'],
                'endLine': data['endLine'],
                'endColumn': data['endColumn'],
                'symbol': data['symbol'],
                'message': data['message'],
                "message_id": data['message-id'],
            })
    return err_msg

@router.get("/languages", tags=["submission"])
def read_lang(db_cursor:DBCursor=Depends(get_cursor)):
    lang_list=submission_crud.read(db_cursor,["id","name","highlighter"],"coco","lang")
    return lang_list