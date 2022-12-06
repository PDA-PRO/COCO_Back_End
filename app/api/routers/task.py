import shutil
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, Depends
from crud.task import CrudTask
from typing import List
import zipfile
import os

router = APIRouter()

class Task(BaseModel):
    title: str
    description: str
    desPic: List[UploadFile]
    diff: int
    timeLimit: int
    memLimit: int
    inputDescription: str
    inputEx1: str
    inputEx2: str
    outputDescription: str
    outputEx1: str
    outputEx2: str
    python: bool
    C_Lan: bool
    testCase: UploadFile

#일단은 입출력 예제 두개씩 넣기
@router.post('/manage/', tags=['manage'])
async def upload_task(task: Task = Depends()):
    CrudTask.insert_task(task)
    return {
        "result": 1,
    }

@router.get('/problems', tags=['manage'])
async def read_task():
    return CrudTask.read_problems()

@router.get('/problems/{task_id}', tags=['manage'])
async def task_detail(task_id: int):
    return CrudTask.search_task(task_id)

@router.post('/test', tags=['manage'])
async def test_test(files: UploadFile):
    zip_file_path = f'/home/sjw/COCO_Back_End/tasks/temp/temp'

    with open(f"{zip_file_path}.zip", 'wb') as upload_zip:
            shutil.copyfileobj(files.file, upload_zip)
    with zipfile.ZipFile(f"{zip_file_path}.zip") as encrypt_zip:
            encrypt_zip.extractall(
                f'/home/sjw/COCO_Back_End/tasks/temp/re',
                None
            )
    # 문제 id에 맞게 폴더 이름 변경
    # os.rename(f"C:/Users/sdjmc/vscode/COCO_Back_End/tasks/test", 'C:/Users/sdjmc/vscode/COCO_Back_End/tasks/100')
    return {'filename': files}