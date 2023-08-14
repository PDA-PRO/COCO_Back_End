from pydantic import BaseModel,conint

class PaginationIn(BaseModel):
    size:conint(ge=1)
    page:conint(ge=1)

class PaginationOut(BaseModel):
    total : int
    size:int
