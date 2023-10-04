import os
import shutil
def ready():
    '''
    worker에 필요한 sandbox 폴더들 초기화
    '''
    if not os.path.exists(os.getenv("SANDBOX_PATH")):
        os.mkdir(os.getenv("SANDBOX_PATH"))
    if os.listdir(os.getenv("SANDBOX_PATH")):
        print("샌드박스 폴더 있음 폴더 비움")
        for i in os.listdir(os.getenv("SANDBOX_PATH")):
            shutil.rmtree(os.path.join(os.getenv("SANDBOX_PATH"),i))

    for i in range(1,int(os.getenv("CELERY_CONCURRENCY"))+1):
        os.mkdir(os.path.join(os.getenv("SANDBOX_PATH"),str(i)))
        os.mkdir(os.path.join(os.getenv("SANDBOX_PATH"),str(i),"error"))
        os.mkdir(os.path.join(os.getenv("SANDBOX_PATH"),str(i),"meta"))
        os.mkdir(os.path.join(os.getenv("SANDBOX_PATH"),str(i),"out"))

if __name__=="__main__":
    ready()
