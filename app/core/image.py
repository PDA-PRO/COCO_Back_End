import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(verbose=True)
class Image():
    def upload(self,type,id,file,role):
        nowtime=datetime.now().strftime('%Y%m%d%H%M%S%f')
        filepath=""
        extension=file.filename.split(".")[-1].lower()
        filename=""
        if type==1:#공지글 이미지
            filepath=os.getenv("NOTICE_PATH")
            filename=nowtime+"."+extension
        elif type==2:#게시판 이미지
            filepath=os.path.join(os.getenv("BOARD_PATH"),str(id))
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            filename=nowtime+"."+extension
        elif type==3:#문제글 이미지
            filepath=os.path.join(os.getenv("TASK_PATH"),str(id))
            filename=nowtime+"."+extension
        elif type==4:#프로필 이미지
            filepath=os.getenv("PROFILE_PATH")
            filename=id+"."+extension
        
        with open(os.path.join(filepath,filename),"wb+") as new_image:
            new_image.write(file.file.read())
        return filename

    def download(self,filename,type,id):
        filepath=""
        if type==1:#공지글 이미지
            filepath=os.getenv("NOTICE_PATH")
        elif type==2:#게시판 이미지
            filepath=os.path.join(os.getenv("BOARD_PATH"),str(id))
        elif type==3:#문제글 이미지
            filepath=os.path.join(os.getenv("TASK_PATH"),str(id))
        elif type==4:#프로필 이미지
            filepath=os.getenv("PROFILE_PATH")
        return os.path.join(filepath,filename)

image=Image()