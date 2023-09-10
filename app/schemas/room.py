from pydantic import BaseModel
from datetime import datetime

from schemas.common import PaginationOut,PaginationIn
class RoomBase(BaseModel):
    id:int
    name:str
    desc:str
    leader:str
    members:int
    exp: int
    ranking: int

class RoomBaseIn(PaginationIn):
    query:str|None

class RoomBaseOut(PaginationOut):
    room_list:list[RoomBase]

class CreateRoom(BaseModel):
    name: str
    desc: str
    leader: str
    members: list[str]

class RoomQuestion(BaseModel):
    room_id: int
    title: str
    question: str
    code: str
    writer: str



class Answer(BaseModel):
    a_id: int
    answer: str
    code: str
    ans_writer: str
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
    level: int

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
    ans_writer: str

class RoomMember(BaseModel):
    room_id: int
    user_id: list[str]

class RoomProblem(BaseModel):
    room_id: int
    task_id: int

class JoinRoom(BaseModel):
    room_id: int
    user_id: str
    message: str

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