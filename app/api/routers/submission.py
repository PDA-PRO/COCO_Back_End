from fastapi import APIRouter
from pydantic import BaseModel
from core.celery_worker import process_sub
import redis

router = APIRouter()

class Submission(BaseModel):
    taskid: int
    stdid: int
    time: int
    sourcecode:str
    callbackurl:str
    token:str


@router.post("/submission/", tags=["submission"])
async def root(sub:Submission):
    # db에 새로운 제출 저장하기
    process_sub.apply_async([sub.taskid,sub.stdid,sub.time,sub.sourcecode,sub.callbackurl,sub.token])
    return {"message": sub}

@router.get("/running_stat/", tags=["submission"])
async def work_result():
    i=1
    temp=[]
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while i<9:
            temp.append(int(conn.get(str(i))))
            i+=1
    return {"message": (temp)}