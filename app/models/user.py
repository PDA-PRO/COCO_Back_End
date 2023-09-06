from .base import ModelBase
class User(ModelBase):
    id:str
    pw:str
    name:str
    role:int
    email:str
    exp:int
    level:int