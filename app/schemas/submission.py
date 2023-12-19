from pydantic import BaseModel
from .common import *
from datetime import datetime

class Lint(BaseModel):
    type:str
    line:int
    column:int
    endLine:int| None=None
    endColumn:int| None=None
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
    status_id:int| None=None
    code:str
    stdout:str| None=None
    time:datetime
    stderr:str| None=None
    token:str
    callback_url:str
    exit_code:int| None=None
    message:str| None=None
    number_of_runs:int| None=None
    status:int
    lang:str
    rate:float
    diff:int
    used_memory:int|None=None
    used_time:float|None=None

class SubResult(BaseModel):
    subDetail: subDetail
    lint: list[Lint]| None=None

class StatusBase(BaseModel):
    sub_id:int
    user_id:str
    task_id:int
    title:str
    lang : str
    status : int
    time : datetime
    is_solved:bool=False

class StatusListIn(PaginationIn):
    task_id:int | None=None
    lang: int | None=None
    onlyme:bool| None=None
    answer:bool| None=None
    user_id:str| None=None

class StatusListOut(PaginationOut):
    statuslist:list[StatusBase]
class Wpc(BaseModel):
    status:int
    wpc_result:str|None=None
