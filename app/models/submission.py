from datetime import datetime
from .base import ModelBase
class Submissions(ModelBase):
    id:int
    status_id:int
    code:str  
    stdout:str  
    time:datetime
    stderr:str
    token:str
    callback_url:str
    exit_code:int
    message:str
    number_of_runs:int
    status:int
    lang:int