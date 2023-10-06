from fastapi import APIRouter, Depends, HTTPException,status
from app.core import security
from app.schemas.submission import *
from app.core.celery_worker import process_sub
from app.crud.submission import submission_crud
from app.crud.task import task_crud
from app.api.deps import get_cursor,DBCursor
from app.core.wpc import *
import json

router = APIRouter()

@router.post("/submission/", tags=["submission"],response_model=BaseResponse)
def scoring(submit:Submit,token: dict = Depends(security.check_token),db_cursor=Depends(get_cursor)):
    """
    제출된 코드 채점

    - submit
        - taskid
        - sourcecode
        - callbackurl
        - lang : c언어 1 | 파이썬 0
    - token :jwt
    """
    sub_id=submission_crud.create_sub(db_cursor,submit,token['id'])
    #클라이언트와 celery worker 간에 전송되는 데이터는 직렬화되어야 하기 때문에 db_cursor 객체를 넘기지 못한다.
    process_sub.apply_async([submit.taskid,submit.sourcecode,submit.callbackurl,"hi",sub_id,submit.lang,token['id']])

    return {"code": 1}

@router.get("/result/{sub_id}", tags=["submission"],response_model=SubResult|None)
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
        if sub_info[0]['user_id']==token['id'] or sub_info[0]['task_id'] in submission_crud.get_solved(db_cursor,token['id']):
            rows=submission_crud.read_sub(db_cursor,sub_id)
            if len(rows):
                return {'subDetail':rows[0], 'lint': read_lint(sub_id)}
            else:
                return None
    
    raise HTTPException(
            status_code=403,
            detail="Insufficient permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )



@router.get("/status/", tags=["submission"],response_model=StatusListOut)
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
    return submission_crud.read_status(db_cursor,info)

@router.get("/wpc", tags=["submission"],response_model=Wpc)
def get_wpc(sub_id:int,task_id:int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    WPC:Wrong Part of Code 분석 결과 조회
    서버에 WPC 확장기능이 적용되어 있어야함.
    WPC 분석이 가능한 제출코드는 TC틀림으로 인한 오답, 512토큰 이하, 문제 제목에 wpc:p00000 형식의 wpc문제 코드가 존재해야함

    params
    - sub_id : 제출 id
    - task_id : 문제 id
    - token :jwt
    ------------------------------------
    returns
    - status : wpc 분석 결과 `1`분석 성공 `2`TC틀림 오답이 아님 `3`wpc 불가능 문제 `4`512토큰 초과
    """
    
    if not is_active:
        raise HTTPException(status.HTTP_510_NOT_EXTENDED,"wpc 확장 기능이 존재하지 않습니다.")
    
    prev_result=submission_crud.read(db_cursor,db="coco",table="wpc",sub_id=sub_id)
    if prev_result:
        if prev_result[0]["status"]==2: #TC 실패로 틀린 제출이 아님
            return {"status":2}
        elif prev_result[0]["status"]==3: #wpc가 불가능한 문제
            return {"status":3}
        elif prev_result[0]["status"]==4: #wpc의 제한사항(512토큰 이하)을 초과
            return {"status":4}
        else:
            return {"status":1,"wpc_result":prev_result[0]["result"]}
    else:
        task_title=task_crud.read(db_cursor,["title"],id=task_id)
        if "wpc:" not in task_title[0]["title"]:
            submission_crud.create(db_cursor,{"sub_id":sub_id,"status":3},"coco","wpc")
            return {"status":3}

        sub_data=submission_crud.read(db_cursor,["code","message"],id=sub_id)
        if sub_data[0]["message"]!="TC 실패":
            submission_crud.create(db_cursor,{"sub_id":sub_id,"status":2},"coco","wpc")
            return {"status":2}
        
        wpc_desc_id=task_title[0]["title"].split("wpc:")[-1]
        wpc_result=process_wpc(sub_data[0]["code"],wpc_desc_id)
        if wpc_result is None:
            submission_crud.create(db_cursor,{"sub_id":sub_id,"status":4},"coco","wpc")
            return {"status":4}
        
        submission_crud.create(db_cursor,{"sub_id":sub_id,"status":1,"result":wpc_result},"coco","wpc")
        return {"status":1,"wpc_result":wpc_result}
    
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