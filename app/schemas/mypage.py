from pydantic import BaseModel

class ChangeInfo(BaseModel):
    user_id: str
    new_info: str

class MyTask(BaseModel):
    user_id: str
    task_id: int

class MyBoard(BaseModel):
    board_id: int