from pydantic import BaseModel, conint
from fastapi import  UploadFile
from .common import *

class TaskBase(BaseModel):
    title: str
    inputDescription: str
    inputEx1: str
    inputEx2: str
    outputDescription: str
    outputEx1: str
    outputEx2: str
    testCase: UploadFile
    diff: int
    timeLimit: int
    memLimit: int
    category:str
    
class TaskListIn(PaginationIn):
    keyword:str| None=None
    diff:str| None=None
    category:str| None=None
    rateSort:conint(ge=0,le=2)| None=None
    user_id: str| None=None

class TaskMeta(BaseModel):
    id : int
    title : str
    diff : int
    rate : int
    count :int| None=None

class TaskListOut(PaginationOut):
    tasks : list[TaskMeta]
    solved_list : list[int]| None=None
    wrong_list : list[int]| None=None

class TaskDetail(BaseModel):
    id:int
    title: str
    mainDesc:str
    inDesc: str
    inputEx1: str
    inputEx2: str
    outDesc: str
    outputEx1: str
    outputEx2: str
    diff: int
    rate:float
    timeLimit: int
    memLimit: int
    category:list[str]
    is_ai:int| None=None