from pydantic import BaseModel
from .common import *
from datetime import datetime

class Lint(BaseModel):
    type:str
    line:int
    column:int
    endLine:int|None
    endColumn:int|None
    symbol:str
    message:str
    message_id :str
class Submit(BaseModel):
    taskid: int
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

class SubResult(BaseModel):
    subDetail: subDetail
    lint: list[Lint]|None

class StatusBase(BaseModel):
    sub_id:int
    user_id:str
    task_id:int
    title:str
    lang : conint(le=1,ge=0)
    status : int
    time : datetime
    is_solved:bool=False

class StatusListIn(PaginationIn):
    task_id:conint(ge=1)|None
    lang:conint(le=1,ge=0)|None
    onlyme:bool|None
    answer:bool|None
    user_id:str|None

class StatusListOut(PaginationOut):
    statuslist:list[StatusBase]
class Wpc(BaseModel):
    status:int
    wpc_result:str=None
