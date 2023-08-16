from fastapi import APIRouter, Depends
from core import security
from schemas.submission import Submit, subDetail
from core.celery_worker import process_sub
import redis
from crud.submission import submission_crud
from api.deps import get_cursor,DBCursor

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
