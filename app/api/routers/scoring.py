from fastapi import APIRouter
from schemas.submission import Submit
from core.celery_worker import process_sub
from crud.submission import CrudSubmission
import redis
from crud.task import CrudTask

router = APIRouter()


@router.post("/submission/", tags=["submission"])
async def root(submit:Submit):
    # db에 새로운 제출 저장하기
    crud_sub=CrudSubmission()
    sub_id=crud_sub.init_submit(submit)
    process_sub.apply_async([submit.taskid,submit.sourcecode,submit.callbackurl,"hi",sub_id])

    return {"result": 1}

@router.get("/running_stat/", tags=["submission"])
async def work_result():
    i=1
    temp=[]
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while i<9:
            temp.append(int(conn.get(str(i))))
            i+=1
    return {"message": (temp)}

@router.get("/result/{sub_id}", tags=["submission"])
async def load_result(sub_id: int):
    crud_sub=CrudSubmission()
    rows=crud_sub.select_submit(sub_id)
    if len(rows):
        return rows[0]
    else:
        return None
