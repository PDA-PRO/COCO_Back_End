from datetime import datetime
from pydantic import BaseModel
from .common import *

class BoardBase(BaseModel):
    id: int    
    title: str
    rel_task:int| None=None
    time: datetime
    category: int
    likes: int
    views: int
    comments: int
    code : str| None=None
    user_id: str

class BoardListOut(PaginationOut):
    boardlist:list[BoardBase]

class BoardDetail(BoardBase):
    context:str
    is_board_liked:bool

class BoardBody(BaseModel):
    title: str
    context: str
    category: int
    code: str| None=None
    
class CommentBase(BaseModel):
    id: int
    context: str
    write_time : datetime
    likes : int
    user_id: str
    board_id: int
    is_liked : bool| None=None

class CreateComment(BaseModel):
    context: str