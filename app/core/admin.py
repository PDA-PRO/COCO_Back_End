import os
from dotenv import load_dotenv
from core import security

#환경변수에서 민감한 정보 가져오기
load_dotenv(verbose=True)

class Check():
    def check_id(self,id):
        if id==os.getenv("ADMIN_ID"):
            return True
        else:
            False

    def check_admin(self, user_id, user_pw):
        if self.check_id(user_id):#로그인 정보가 없다면
            return False
        else:#로그인 정보가 있다면
            if security.verify_password(user_pw, os.getenv("ADMIN_PW")):#패스워드가 맞다면
                return True
            return False

    def get_notice(self):
        try:
            with open("./../../COCO_Back_End/notice/notice.txt","r") as file:
                content=file.readlines()
        except Exception as e:
            print("공지사항 파일 notice.txt 를 불러오는 중 오류가 발생하였습니다.",e)
            return None
        return content
        
    def update_notice(self,new_content):
        try:
            with open("./../../COCO_Back_End/notice/notice.txt","w") as file:
                file.write(new_content)
        except Exception as e:
            print("공지사항 파일 notice.txt 를 업데이트하는 중 오류가 발생하였습니다.",e)
            return False

        return True


check=Check()