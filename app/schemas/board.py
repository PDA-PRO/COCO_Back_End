from pydantic import BaseModel


class Board(BaseModel):
    id: int
    title: str
    user_id: str
    time: str
    category: int
    likes: int
    views: int
    comments: int

# class FastWrite(BaseModel):
#     user_id: str
#     title: str
#     context: str

class WriteBoard(BaseModel):
    user_id: str
    title: str
    context: str
    category: int

class BoardLikes(BaseModel):
    user_id: str
    board_id: int
    likes: int
    type: bool

class CommentLikes(BaseModel):
    user_id: str
    board_id: int
    comment_id: int
    likes: int
    type: bool

class CommentInfo(BaseModel):
    user_id: str
    context: str
    board_id: int

class DeleteBoard(BaseModel):
    board_id: int
    user_id: str


class DeleteComment(BaseModel):
    comment_id: int
    user_id: str