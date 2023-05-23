from pydantic import BaseModel
from fastapi import  UploadFile

class Task(BaseModel):
    title: str
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