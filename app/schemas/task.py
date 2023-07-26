from pydantic import BaseModel, conint
from fastapi import  UploadFile

class Task(BaseModel):
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
    
class ReadTask(BaseModel):
    keyword:str|None
    diff:str|None
    category:str|None
    rateSort:conint(ge=0,le=2)|None
    size:conint(ge=1)
    page:conint(ge=0)

class TaskMeta(BaseModel):
    id : int
    title : str
    diff : int
    rate : int

class TaskMetaWithCount(TaskMeta):
    count:int|None

class TaskList(BaseModel):
    total : int
    size:int
    tasks : list[TaskMeta]

class TaskListWithCount(BaseModel):
    total : int
    size:int
    tasks : list[TaskMetaWithCount]

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