from fastapi import FastAPI
from app.api.routers import auth,scoring, task, board, status, miscellaneous, mypage, image,room, user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#CORS(https://www.jasonchoi.dev/posts/fastapi/cors-allow-setting)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
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
app.include_router(task.router)
app.include_router(board.router)
app.include_router(status.router)
app.include_router(miscellaneous.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(mypage.router)
app.include_router(image.router)
app.include_router(room.router)