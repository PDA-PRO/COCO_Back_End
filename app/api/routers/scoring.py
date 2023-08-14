from fastapi import APIRouter, Depends
from core import security
from schemas.submission import Submit, subDetail
from core.celery_worker import process_sub
import redis
from crud.submission import submission_crud

router = APIRouter()

@router.post("/submission/", tags=["submission"])
async def scoring(submit:Submit,token: dict = Depends(security.check_token)):
    """
    제출된 코드 채점

    - submit
        - taskid
        - userid
        - sourcecode
        - callbackurl
        - lang : c언어 1 | 파이썬 0
    """
    sub_id=submission_crud.create_sub(submit)
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
async def load_result(sub_id: int,token: dict = Depends(security.check_token)):
    """
    제출된 코드 채점 결과 확인

    - sub_id : 제출 id
    """
    rows=submission_crud.read_sub(sub_id)
    if len(rows):
        return rows[0]
    else:
        return None
