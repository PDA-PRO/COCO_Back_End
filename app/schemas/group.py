from pydantic import BaseModel

class MakeGroup(BaseModel):
    name: str
    desc: str
    members: list