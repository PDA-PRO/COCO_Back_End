from typing import Annotated
from fastapi import Body
from pydantic import BaseModel,conint

class PaginationIn(BaseModel):
    size:conint(ge=1)| None=None
    page:conint(ge=1)| None=None

class PaginationOut(BaseModel):
    total : int| None=None
    size:int| None=None

class BaseResponse(BaseModel):
    code : int

class NoticeContent(BaseModel):
    content: Annotated[str, Body(embed=True)]