from pydantic import BaseModel

class Submit(BaseModel):
    taskid: int
    userid: str
    sourcecode:str
    callbackurl:str
    lang:int