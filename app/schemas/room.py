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
    ranking: int| None=None

class RoomBaseIn(PaginationIn):
    query:str| None=None

class RoomBaseOut(PaginationOut):
    room_list:list[RoomBase]

class CreateRoom(BaseModel):
    name: str
    desc: str
    members: list[str]

class CreateQuestion(BaseModel):
    title: str
    question: str
    code: str

class Answer(BaseModel):
    a_id: int
    answer: str
    code: str
    ans_writer: str| None=None
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

class CreateAnswer(BaseModel):
    q_id: int
    answer: str
    code: str

class RoomMemberExp(BaseModel):
    user_id: str
    exp:int

class RoomDetail(RoomBase):
    members:list[RoomMemberExp]
    
class RoadmapBody(BaseModel):
    name: str
    desc: str
    tasks: list[int]
    
class RoadMap(BaseModel):
    id:int
    name: str
    desc: str
    last_modify:datetime| None=None
    tasks: list[int]

class RoadMapList(BaseModel):
    room_info :list[RoadMap]
    solved_task : list[int]

class SelectAnswer(BaseModel):
    a_id: int
    select: int
    ans_writer: str| None=None