import os
import json
from datetime import datetime
import shutil
from dotenv import load_dotenv

load_dotenv(verbose=True)
class Image():
    def upload_temp(self,file,type,id=None):
        """
        텍스트 에디터 작성중 임시로 생성되는 사진을 저장
        
        - file : 원하는 사진 파일
        - type : 1-공지글 2-게시판 3-문제글 4-프로필
        - id : type이 게시판, 문제글, 프로필일 경우 관련된 id
        """
        nowtime=datetime.now().strftime('%Y%m%d%H%M%S%f')
        extension=file.filename.split(".")[-1].lower()
        filepath=""
        filename=""

        if type==1:#공지글 이미지
            filepath=os.getenv("NOTICE_PATH")
            filename=nowtime+"."+extension
        elif type==2:#게시판 이미지
            filepath=os.path.join(os.getenv("BOARD_PATH"),"temp",id)
            filename=nowtime+"."+extension
        elif type==3:#문제글 이미지
            filepath=os.path.join(os.getenv("TASK_PATH"),"temp")
            filename=nowtime+"."+extension
        elif type==4:#프로필 이미지
            filepath=os.getenv("PROFILE_PATH")
            filename=id+".jpg"

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        with open(os.path.join(filepath,filename),"wb+") as new_image:
            new_image.write(file.file.read())
        return filename

    def download(self,filename,type,id=None):
        """
        저장된 사진의 경로 출력
        
        - filename : 원하는 사진 파일
        - type : 1-공지글 2-게시판 3-문제글 4-프로필
        - id : type이 게시판, 문제글, 프로필일 경우 관련된 id
        """
        print("dd")
        filepath=""
        if type==1:#공지글 이미지
            filepath=os.getenv("NOTICE_PATH")
        elif type==2:#게시판 이미지
            filepath=os.path.join(os.getenv("BOARD_PATH"),str(id))
        elif type==3:#문제글 이미지
            filepath=os.path.join(os.getenv("TASK_PATH"),str(id))
        elif type==4:#프로필 이미지
            filepath=os.getenv("PROFILE_PATH")
            if not os.path.exists(os.path.join(filepath,filename)):
                shutil.copyfile(os.path.join(filepath,"base.jpg"),os.path.join(filepath,filename))
                
        target_path=os.path.join(filepath,filename)
        if not os.path.exists(target_path):
            return None
        return target_path
    
    def download_temp(self,filename,type,id=None):
        """
        임시로 저장된 사진의 경로 출력
        
        - filename : 원하는 사진 파일
        - type : 1-공지글 2-게시판 3-문제글 4-프로필
        - id : type이 게시판일 경우 작성한 userid
        """
        filepath=""
        if type==1:#공지글 이미지
            filepath=os.getenv("NOTICE_PATH")
        elif type==2:#게시판 이미지
            filepath=os.path.join(os.getenv("BOARD_PATH"),"temp",id)
        elif type==3:#문제글 이미지
            filepath=os.path.join(os.getenv("TASK_PATH"),"temp")
        elif type==4:#프로필 이미지
            filepath=os.getenv("PROFILE_PATH")

        target_path=os.path.join(filepath,filename)
        if not os.path.exists(target_path):
            return None
        return target_path

    def save_image(self,temp_path,save_path,data,id=None):
        """
        data에서 실제 저장되는 사진들만 temp_path에서 save_path로 이동하고 나머지 temp_path는 삭제
        
        - temp_path : 사진 임시 저장소
        - save_path : 사진 실제 저장소
        - data: textedit의 json형식
        - id : DB에 저장된 data의 id값
        """
        #저장된 data에서 쓰인 사진만 추출 및 텍스트 에디터의 사진 경로를 실제 사진 경로로 수정
        jsonObject = json.loads(data)
        imagelist=[]
        for entity in jsonObject.get("entityMap").values():
            image_params=entity.get("data").get("src").split('/')
            imagename=image_params[-2]
            imagelist.append(imagename)
            entity["data"]["src"]="/".join(image_params[:-1])
            if id:
                entity["data"]["src"]+="?id="+str(id)
        new_data=json.dumps(jsonObject)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
                
        #temp폴더에서 실제로 저장되지 않은 사진 삭제 및 실제로 쓰인 사진를 문제 id에 맞는 경로로 이동
        tempimagelist=os.listdir(temp_path)
        for i in tempimagelist:
            if i.split(".")[-1]!="keep" and not i in imagelist:
                os.remove(os.path.join(temp_path,i))
            else:
                shutil.move(os.path.join(temp_path,i),os.path.join(save_path,i))
        os.rmdir(temp_path)

        return new_data
    
    def delete_image(self,path,userid=None):
        """
        이미지 파일 및 폴더 삭제
        
        - path : 삭제할 파일, 폴더의 경로
        - userid : 프로필 사진 삭제시 유저id
        """
        if userid:
            os.remove(os.path.join(os.getenv("PROFILE_PATH"),userid+".jpg"))
        if os.path.exists(path) and os.path.isdir(path):
                shutil.rmtree(path)
                
    
image=Image()