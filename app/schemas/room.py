from pydantic import BaseModel

class RoomBase(BaseModel):
    id:int
    name:str
    desc:str
    leader:str

class CreateRoom(BaseModel):
    name: str
    desc: str
    leader: str
    members: list[str]

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

class UserID(BaseModel):
    user_id: str
