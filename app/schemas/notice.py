from pydantic import BaseModel

class Notice(BaseModel):
    content: str = ""