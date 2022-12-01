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
        "desPic": [file.filename for file in task.desPic],
    }

@router.get('/problems', tags=['manage'])
async def read_task():
    return CrudTask.read_problems()

@router.get('/problems/{task_id}', tags=['manage'])
async def task_detail(task_id: int):
    return CrudTask.search_task(task_id)

@router.post('/test', tags=['manage'])
async def test_test(files: UploadFile):
    # 올릴 zip의 경로
    zip_file_path = f"C:/Users/sdjmc/Desktop/123242" 

    with zipfile.ZipFile(f"{zip_file_path}.zip") as encrypt_zip:
        encrypt_zip.extractall(
            # 압축 해제된 zip이 저장되는 경로
            f"C:/Users/sdjmc/vscode/COCO_Back_End/tasks",
            None,
            # bytes(256, encoding='utf-8')
        )
    # 문제 id에 맞게 폴더 이름 변경
    os.rename(f"C:/Users/sdjmc/vscode/COCO_Back_End/tasks/test", 'C:/Users/sdjmc/vscode/COCO_Back_End/tasks/100')
    return {'filename': files}