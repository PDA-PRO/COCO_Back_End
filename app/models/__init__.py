class User():
    id: str
    pw: str
    name: str
    role: int

class Student():
    std_id: str
    rate: float
    age: int
    user_id: str

class Teacher():
    tea_id: str
    is_manager: int
    user_id: str