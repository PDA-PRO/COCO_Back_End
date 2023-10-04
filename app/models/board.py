from .base import ModelBase
from datetime import datetime
class Boards(ModelBase):
    id:int
    context:str
    title:str
    rel_task:int
    time:datetime
    category:int
    likes:int
    views:int
    comments:int
    code:str