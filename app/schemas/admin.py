from pydantic import BaseModel

class Notice(BaseModel):
    html:str =""


class Info(BaseModel):
    PW: str = ""