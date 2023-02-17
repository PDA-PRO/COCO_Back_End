from pydantic import BaseModel

class Notice(BaseModel):
    entity: dict={}
    html:str =""


class Info(BaseModel):
    PW: str = ""