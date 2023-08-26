from .base import ModelBase
from datetime import datetime
class Comment(ModelBase):
    id: int
    context:str
    write_time:datetime
    likes:int