from fastapi import FastAPI
from api.routers import submission

app = FastAPI()

#라우터 설정
app.include_router(submission.router)

@app.get("/test")
async def hello_test():
    return {"message": 'hello'}
    
