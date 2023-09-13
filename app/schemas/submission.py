from pydantic import BaseModel
from .common import *
from datetime import datetime
class Submit(BaseModel):
    taskid: int
    userid: str
    sourcecode:str
    callbackurl:str
    lang:int

class subDetail(BaseModel):
    id:int
    status_id:str|None
    code:str
    stdout:str|None
    time:datetime
    stderr:str|None
    token:str
    callback_url:str
    exit_code:int|None
    message:str|None
    number_of_runs:int|None
    status:int
    lang:conint(le=1,ge=0)
    rate:float
    diff:int

class Status(BaseModel):
    sub_id:int
    user_id:str
    task_id:int
    title:str
    lang : conint(le=1,ge=0)
    status : int
    time : datetime
    is_solved:bool=None

class StatusListIn(PaginationIn):
    task_id:conint(ge=1)|None
    lang:conint(le=1,ge=0)|None
    user_id:str|None
    answer:bool|None

class StatusListOut(PaginationOut):
    statuslist:list[Status]

class Lint(BaseModel):
    type:str
    line:int
    column:int
    endLine:int
    endColumn:int
    symbol:str
    message:str
    message_id :str

class Wpc(BaseModel):
    status:int
    wpc_result:str=None
