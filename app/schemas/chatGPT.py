from pydantic import BaseModel


class AskQ(BaseModel):
    content: str
    code: str
    room_id: int
    q_id: int

class CreateTask(BaseModel):
    content: str
    category: str|None
    diff: int|None
    is_final: bool