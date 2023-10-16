from datetime import datetime
from pydantic import BaseModel
from .common import *

class LikesBase(BaseModel):
    board_id: int
    type: bool

class BoardBase(BaseModel):
    id: int    
    title: str
    rel_task:int|None
    time: datetime
    category: int
    likes: int
    views: int
    comments: int
    code : str|None
    user_id: str

class BoardListOut(PaginationOut):
    boardlist:list[BoardBase]

class BoardDetail(BoardBase):
    user_id:str
    context:str
    is_board_liked:bool

class CreateBoard(BaseModel):
    title: str
    context: str
    category: int
    code: str|None
    
class CommentBase(BaseModel):
    id: int
    context: str
    write_time : datetime
    likes : int
    user_id: str
    board_id: int
    is_liked : bool|None

class CommentLikes(LikesBase):
    comment_id: int

class CreateComment(BaseModel):
    context: str
    board_id: int