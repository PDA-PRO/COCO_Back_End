from pydantic import BaseModel

class MyStudents(BaseModel):
    tea_id: str
    std_id: str