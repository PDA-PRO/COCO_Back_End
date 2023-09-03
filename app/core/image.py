import os
from datetime import datetime
import shutil
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv(verbose=True)
class Image():
    def upload_temp(self,file,type,id=None):
        """
        텍스트 에디터 작성중 임시로 생성되는 사진을 저장
        
        - file : 원하는 사진 파일
        - type : 1-공지글 2-게시판 3-문제글 4-프로필 5-로드맵
        - id : type이 게시판, 문제글, 프로필, 로드맵일 경우 관련된 id
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
        elif type==5:#로드맵 이미지
            filepath=os.path.join(os.getenv("ROADMAP_PATH"),"temp",id)
            filename=nowtime+"."+extension

        if not os.path.exists(filepath):
            os.makedirs(filepath)

        with open(os.path.join(filepath,filename),"wb+") as new_image:
            new_image.write(file.file.read())
        return filename

    def download(self,filename,type,id=None):
        """
        저장된 사진의 경로 출력
        
        - filename : 원하는 사진 파일
        - type : 1-공지글 2-게시판 3-문제글 4-프로필 5-로드맵
        - id : type이 게시판, 문제글, 프로필, 로드맵일 경우 관련된 id
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
        elif type==5:#로드맵 이미지
            filepath=os.path.join(os.getenv("ROADMAP_PATH"),str(id))

        target_path=os.path.join(filepath,filename)
        if not os.path.exists(target_path):
            return None
        return target_path
    
    def download_temp(self,filename,type,id=None):
        """
        임시로 저장된 사진의 경로 출력
        
        - filename : 원하는 사진 파일
        - type : 1-공지글 2-게시판 3-문제글 4-프로필 5-로드맵
        - id : type이 게시판,로드맵일 경우 작성한 userid
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
        elif type==5:#로드맵 이미지
            filepath=os.path.join(os.getenv("ROADMAP_PATH"),"temp",id)

        target_path=os.path.join(filepath,filename)
        if not os.path.exists(target_path):
            return None
        return target_path

    def save_update_image(self,temp_path:str,save_path:str,data:str,id:int|str=None,mode:str="su"):
        """
        data에서 실제 저장되는 사진들만 temp_path에서 save_path로 이동하고 나머지 temp_path는 삭제하거나
        data가 수정되어 save_path의 사진들중 필요없는 사진을 삭제
        
        - temp_path : 사진 임시 저장소
        - save_path : 사진 실제 저장소
        - data: 프론트엔드의 textEditor에서 작성된 html 문자열
        - id : DB에 저장된 data의 id값
        - mode : 's' - 새로운 이미지를 추가, 'u' - 기존의 이미지들중 필요없는 이미지를 삭제
        """

        #mode값이 틀리면 에러발생
        for i in mode:
            if i!="s" and i!="u":
                raise Exception("mode값은 's','u'값이어야합니다.")
            
        imagelist=[]
        soup = BeautifulSoup(data, 'html.parser')
        img_tags=soup.find_all('img')
        # 저장된 data에서 쓰인 사진만 추출 및 텍스트 에디터의 사진 경로를 실제 사진 경로로 수정
        for i in range(len(img_tags)):
            image_url=img_tags[i]["src"].split("/temp")[0].split("?id")[0]
            img_tags[i]["src"]=image_url
            imagelist.append(image_url.split("/")[-1])
            if id:
                try:
                    id=str(id)
                finally:
                    img_tags[i]["src"]+="?id="+id
        new_data=str(soup)

        if "s" in mode:
            if not os.path.exists(save_path):
                os.makedirs(save_path)
                    
            #temp폴더에서 실제로 저장되지 않은 사진 삭제 및 실제로 쓰인 사진를 문제 id에 맞는 경로로 이동
            if os.path.exists(temp_path):
                temp_imagelist=os.listdir(temp_path)
                for i in temp_imagelist:
                    if i.split(".")[-1]!="keep" and not i in imagelist:
                        os.remove(os.path.join(temp_path,i))
                    else:
                        shutil.move(os.path.join(temp_path,i),os.path.join(save_path,i))
                os.rmdir(temp_path)
        
        if "u" in mode:
            #save폴더에서 data에 더이상 쓰이지 않는 이미지 삭제
            if os.path.exists(save_path):
                save_imagelist=os.listdir(save_path)
                for i in save_imagelist:
                    temp=i.split(".")
                    if len(temp)<=1:
                        continue
                    if temp[-1]!="zip" and not i in imagelist:
                        os.remove(os.path.join(save_path,i))

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