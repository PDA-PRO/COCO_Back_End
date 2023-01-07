from pydantic import BaseModel

class ChangeInfo(BaseModel):
    user_id: str
    new_info: str