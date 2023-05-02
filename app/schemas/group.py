from pydantic import BaseModel

class MakeGroup(BaseModel):
    name: str
    desc: str
    leader: str
    members: list

class ModifyGroup(BaseModel):
    group_id: int
    user_id: str

class GroupWorkBook(BaseModel):
    group_id: int
    workbook_name: str


class AddProblem(BaseModel):
    workbook_id: int
    task_id: int
