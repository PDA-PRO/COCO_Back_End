from fastapi import FastAPI, File, UploadFile,Path
from celery_worker import process_sub
import subprocess
import redis
from typing import Union
from pydantic import BaseModel
app = FastAPI()

class Submission(BaseModel):
    taskid: int
    stdid: int
    time: int
    sourcecode:str
    callbackurl:str
    token:str

@app.post("/submission")
async def root(sub:Submission):
    # db에 새로운 제출 저장하기
    process_sub.apply_async([sub.taskid,sub.stdid,sub.time,sub.sourcecode,sub.callbackurl,sub.token])
    return {"message": sub}
    
@app.get("/running_stat")
async def work_result():
    i=1
    temp=[]
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while i<9:
            temp.append(int(conn.get(str(i))))
            i+=1
    return {"message": (temp)}

