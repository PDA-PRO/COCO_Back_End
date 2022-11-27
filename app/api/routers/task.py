from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, Depends
from crud.task import CrudTask

router = APIRouter()

class Task(BaseModel):
    title: str
    desc: str
    desPic: UploadFile
    diff: int
    time: int
    mem: int
    inputDesc: str
    inputEx1: str
    inputEx2: str
    inputFile: UploadFile
    outputDesc: str
    outputEx1: str
    outputEx2: str
    outputFile: UploadFile
    py: bool
    cLan: bool
    testCase: UploadFile

@router.post('/manage/', tags=['manage'])
async def upload_task(task: Task = Depends()):
    CrudTask.insert_task(task)
    return {
        "desc": task.desPic.filename,
        "inputFile": task.inputFile,
        "outputFile":task. outputFile,
        "testCase": task.testCase,
        "task": task.title
    }
