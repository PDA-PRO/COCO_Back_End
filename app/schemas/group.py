from pydantic import BaseModel

class MakeGroup(BaseModel):
    name: str
    desc: str
    leader: str
    members: list

class ModifyGroup(BaseModel):
    group_id: int
    user_id: str

class GroupProblem(BaseModel):
    group_id: int
    task_id: int

class SearchMember(BaseModel):
    user_id: str
    group_id: int
