from fastapi import FastAPI
from api.routers import scoring, login, task, board, status, hot, admin, authentication, mypage, image, std_manage, group
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#CORS(https://www.jasonchoi.dev/posts/fastapi/cors-allow-setting)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:8000/write_board/"
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
app.include_router(scoring.router)
app.include_router(login.router)
app.include_router(task.router)
app.include_router(board.router)
app.include_router(status.router)
app.include_router(hot.router)
app.include_router(admin.router)
app.include_router(authentication.router)
app.include_router(mypage.router)
app.include_router(image.router)
app.include_router(std_manage.router)
app.include_router(group.router)
