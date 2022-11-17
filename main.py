from fastapi import FastAPI, File, UploadFile
import os
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import db
# import pymysql

#회원가입 정보
class SignUp(BaseModel):
    name: str
    id: str
    pw: str
    type: int #1이면 학생, 2이면 선생

#아이디 중복 확인
class ID(BaseModel):
    id:str

#로그인
class Login(BaseModel):
    id: str
    pw: str
    
app = FastAPI()

#CORS(https://www.jasonchoi.dev/posts/fastapi/cors-allow-setting)
origins = [
    "http://localhost",
    "http://localhost:3000",
]

# 미들웨어 추가 -> CORS 해결위해 필요(https://ghost4551.tistory.com/46)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/submission")
async def root(code:UploadFile,box_id:int,stdin:str):
    f=open("/var/local/lib/isolate/"+str(box_id)+"/box/2temp.py",'wb+')
    content = await code.read()
    f.write(content)
    f.close()
    f1=open('stdin.txt','w')
    f1.write(stdin)
    f1.close()
    f1=open('stdout.txt','w')
    f1.close()
    temp=os.popen('isolate --cg -b '+str(box_id)+' -M ./metadata.txt -d /etc:noexec --run -- /usr/bin/python3 2temp.py < ./stdin.txt > ./stdout.txt 2> ./stderr.txt').read()
    f1=open('stdout.txt','r')
    result=f1.readline()
    f1.close()
    return {"message": result}

@app.post("/init")
async def root(num:int):
    temp=os.popen('isolate --cg -b '+str(num)+' --init').read()
    return {"message": temp}


@app.post('/login/')
async def login(user:Login):
    return {'code': db.check_db(user)}

@app.post("/signup/")
async def create_user(user: SignUp):
    return {"code":db.insert_db(user)}

@app.post("/checkids/")
async def check_ids(id: ID):
    return {"code": db.find_ids(id.id)} 