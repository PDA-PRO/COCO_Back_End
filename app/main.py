from dotenv import load_dotenv
load_dotenv(verbose=True,override=True)
from fastapi import FastAPI
from app.api.routers import auth,submission, task, board, miscellaneous, mypage, image,room, user,plugin, chatgpt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#CORS(https://www.jasonchoi.dev/posts/fastapi/cors-allow-setting)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:1000",
    "http://localhost:8080",
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
app.include_router(task.router)
app.include_router(board.router)
app.include_router(miscellaneous.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(mypage.router)
app.include_router(image.router)
app.include_router(room.router)
app.include_router(chatgpt.router)
app.include_router(plugin.router)
