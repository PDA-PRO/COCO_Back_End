from datetime import datetime
from pydantic import BaseModel


class BoardBase(BaseModel):
    id: int
    context:str
    title: str
    rel_task:int|None
    time: datetime
    category: int
    likes: int
    views: int
    comments: int
    code : str|None

class CommentBase(BaseModel):
    id: int
    context: str
    write_time : datetime
    likes : int
    user_id: str
    board_id: int
    is_liked : bool|None

class BoardDetail(BoardBase):
    user_id:str
    comments_datail:list[CommentBase]
    is_board_liked:bool

class CreateBoard(BaseModel):
    user_id: str
    title: str
    context: str
    category: int
    code: str=None

class LikesBase(BaseModel):
    user_id: str
    board_id: int
    type: bool

class CommentLikes(LikesBase):
    comment_id: int

class CreateComment(BaseModel):
    user_id: str
    context: str
    board_id: int