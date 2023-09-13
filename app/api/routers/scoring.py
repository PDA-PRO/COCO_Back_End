from fastapi import APIRouter, Depends, HTTPException,status
from core import security
from schemas.submission import Submit, subDetail
from core.celery_worker import process_sub
import redis
from crud.submission import submission_crud
from crud.task import task_crud
from api.deps import get_cursor,DBCursor
from core.wpc import *
router = APIRouter()

@router.post("/submission/", tags=["submission"])
async def scoring(submit:Submit,token: dict = Depends(security.check_token),db_cursor=Depends(get_cursor)):
    """
    제출된 코드 채점

    - submit
        - taskid
        - userid
        - sourcecode
        - callbackurl
        - lang : c언어 1 | 파이썬 0
    """
    sub_id=submission_crud.create_sub(db_cursor,submit)
    #클라이언트와 celery worker 간에 전송되는 데이터는 직렬화되어야 하기 때문에 db_cursor 객체를 넘기지 못한다.
    process_sub.apply_async([submit.taskid,submit.sourcecode,submit.callbackurl,"hi",sub_id,submit.lang,submit.userid])

    return {"result": 1}

@router.get("/running_stat/", tags=["submission"])
async def work_result():
    """
    isolate id 1~8중 비어있는 격리공간 조회
    """
    i=1
    temp=[]
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while i<9:
            temp.append(int(conn.get(str(i))))
            i+=1
    return {"message": (temp)}

@router.get("/result/{sub_id}", tags=["submission"],response_model=subDetail|None)
async def load_result(sub_id: int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
    """
    제출된 코드 채점 결과 확인

    - sub_id : 제출 id
    """
    rows=submission_crud.read_sub(db_cursor,sub_id)
    if len(rows):
        return rows[0]
    else:
        return None

@router.get("/wpc", tags=["submission"])
def get_wpc(sub_id:int,task_id:int,db_cursor:DBCursor=Depends(get_cursor)):
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
        print(task_title)
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