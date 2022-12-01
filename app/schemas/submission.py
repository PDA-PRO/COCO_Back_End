from pydantic import BaseModel

class Submit(BaseModel):
    taskid: int
    userid: str
    time: int
    sourcecode:str
    callbackurl:str
    token:str