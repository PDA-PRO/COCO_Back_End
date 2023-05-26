from pydantic import BaseModel

class MakeGroup(BaseModel):
    name: str
    desc: str
    leader: str
    members: list

class GroupMember(BaseModel):
    group_id: int
    user_id: str

class GroupProblem(BaseModel):
    group_id: int
    task_id: int

class JoinGroup(BaseModel):
    group_id: int
    user_id: str
    message: str

