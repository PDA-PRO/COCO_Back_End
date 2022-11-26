from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, Depends
from typing import List

router = APIRouter()


class Task(BaseModel):
    title: str
    desc: str
    # desPic: str
    diff: int
    time: str
    mem: int
    inputDesc: str
    inputEx1: str
    inputEx2: str
    # inputFile: UploadFile
    outputDesc: str
    outputEx1: str
    outputEx2: str
    # outputFile: UploadFile
    py: bool
    cLan: bool
    # testCase: UploadFile




@router.post('/manage/', tags=['manage'])
async def upload_task(desPic: UploadFile, inputFile: UploadFile, 
outputFile: UploadFile, testCase: UploadFile, task: Task = Depends()):
    return {
        "desc": desPic.filename,
        "inputFile": inputFile.filename,
        "outputFile": outputFile.filename,
        "testCase": testCase.filename,
        "task": task.title
    }

@router.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}



# @router.post('/manage/', tags=['manage'])
# async def up_load(task: Task):
#     return {'code': 1}