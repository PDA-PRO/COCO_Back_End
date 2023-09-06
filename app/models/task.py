from .base import ModelBase

class Task(ModelBase):
    id:int
    title:str
    sample:str
    rate:float
    mem_limit:int
    time_limit:int
    diff:int