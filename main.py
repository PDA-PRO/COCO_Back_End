from fastapi import FastAPI, File, UploadFile
from celery_worker import divide
import os

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/submission_test")
async def root(code:UploadFile,box_id:int,stdin:str):
    f=open("/var/local/lib/isolate/"+str(box_id)+"/box/2temp.py",'wb+')
    content = await code.read()
    f.write(content)
    f.close()
    f1=open('stdin.txt','w')
    f1.write(stdin)
    f1.close()
    f1=open('stdout.txt','w')
    f1.close()
    temp=os.popen('isolate --cg -b '+str(box_id)+' -M ./metadata.txt -d /etc:noexec --run -- /usr/bin/python3 2temp.py < ./stdin.txt > ./stdout.txt 2> ./stderr.txt').read()
    f1=open('stdout.txt','r')
    result=f1.readline()
    f1.close()
    return {"message": result}

@app.post("/init")
async def root(num:int):
    temp=os.popen('isolate --cg -b '+str(num)+' --init').read()
    return {"message": temp}

@app.get("/work")
async def work(task_id: str, input_a: int, input_b: int):
    divide.apply_async([input_a, input_b], task_id=task_id)
    return {"message": "celery start"}
    
@app.get("/work_result")
async def work_result(task_id: str):
    result = divide.AsyncResult(task_id)
    return {"message": result.info}

