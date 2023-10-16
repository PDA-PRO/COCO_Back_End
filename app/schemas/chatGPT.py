from pydantic import BaseModel


class AskQ(BaseModel):
    content: str
    code: str | None
    room_id: int
    q_id: int


class CreateTask(BaseModel):
    content: str

class UploadAITask(BaseModel):
    title: str
    inputDescription: str
    inputEx1: str
    inputEx2: str
    outputDescription: str
    outputEx1: str
    outputEx2: str
    diff: int
    timeLimit: int
    memLimit: int
    category:str

class AiCode(BaseModel):
    code: str
    task_id: int
    sub_id: int


class CodeImprovement(BaseModel):
    data: bool
    code: str
    desc: str
    