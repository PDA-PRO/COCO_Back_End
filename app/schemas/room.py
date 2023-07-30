from pydantic import BaseModel
from datetime import datetime
class RoomBase(BaseModel):
    id:int
    name:str
    desc:str
    leader:str
    members:int
    exp: int
    ranking: int

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