from pydantic import BaseModel


class AskQ(BaseModel):
    content: str
    code: str
    room_id: int
    q_id: int