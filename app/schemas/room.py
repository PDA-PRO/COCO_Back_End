from pydantic import BaseModel
from datetime import datetime

from app.schemas.common import *

class RoomBase(BaseModel):
    id:int
    name:str
    desc:str
    leader:str
    members:int
    exp: int
    ranking: int|None

class RoomBaseIn(PaginationIn):
    query:str|None

class RoomBaseOut(PaginationOut):
    room_list:list[RoomBase]

class CreateRoom(BaseModel):
    name: str
    desc: str
    members: list[str]

class RoomQuestion(BaseModel):
    room_id: int
    title: str
    question: str
    code: str

class Answer(BaseModel):
    a_id: int
    answer: str
    code: str
    ans_writer: str|None
    time: datetime
    check: int
    

class Question(BaseModel):
    id: int
    title: str
    question: str
    code: str
    writer: str
    answers:list[Answer]
    check: bool
    time: datetime
    q_writer_level: int

class QuestionListOut(PaginationOut):
    question_list:list[Question]

class MyRoom(BaseModel):
    id: int
    name: str
    leader: str
    members: int
    exp: int
    ranking: int 

class RoomAnswer(BaseModel):
    room_id: int
    q_id: int
    answer: str
    code: str

class RoomMember(BaseModel):
    room_id: int
    user_id: str

class RoomMemberExp(BaseModel):
    user_id: str
    exp:int

class RoomDetail(RoomBase):
    members:list[RoomMemberExp]
class RoomRoadMap(BaseModel):
    id: int
    name: str
    desc: str
    last_modify:datetime|None
    tasks: list[int]

class RoomRoadMapList(BaseModel):
    room_info :list[RoomRoadMap]
    solved_task : list[int]

class SelectAnswer(BaseModel):
    room_id: int
    a_id: int
    select: int
    ans_writer: str|None