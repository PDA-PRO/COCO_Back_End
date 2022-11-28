from fastapi import FastAPI
from api.routers import submission, login, task
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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

#라우터 설정
app.include_router(submission.router)
app.include_router(login.router)
app.include_router(task.router)

@app.get("/test")
async def hello_test():
    return {"message": 'hello'}





