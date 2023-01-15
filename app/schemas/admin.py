from pydantic import BaseModel

class Notice(BaseModel):
    content: str = ""

class Info(BaseModel):
    PW: str = ""