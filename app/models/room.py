from .base import ModelBase
class Room(ModelBase):
    id:int
    name:str
    desc:str
    leader:str