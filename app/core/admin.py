import os
from dotenv import load_dotenv,set_key,find_dotenv
from app.core import security
from app.core.image import image

#환경변수에서 민감한 정보 가져오기
load_dotenv(verbose=True)

class Check():

    def check_admin(self, id,user_pw):
        if security.verify_password(user_pw, os.getenv("ADMIN_PW")):#패스워드가 맞다면
            return True
        return False

    def modify_admin_key(self, new_pw:str):
        try:
            set_key(find_dotenv(),"ADMIN_PW",security.get_password_hash(new_pw))
        except Exception as e:
            print("어드민 PW 재설정 중 오류 발생",e)
            return False
        load_dotenv(verbose=True,override=True)
        return True

    def get_notice(self):
        try:
            with open(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt"),"r", encoding="UTF-8") as file:
                content=file.readlines()
        except Exception as e:
            print("공지사항 파일 notice.txt 를 불러오는 중 오류가 발생하였습니다.",e)
            return None
        html = ""
        for i in content:
            html+=i[:-1]
        return html
        
    def update_notice(self,new_content):
        try:
            image.save_update_image(os.getenv("NOTICE_PATH"),os.getenv("NOTICE_PATH"),new_content,mode="u")
            with open(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt"),"w", encoding="UTF-8") as file:
                file.write(new_content)
        except Exception as e:
            print("공지사항 파일 notice.txt 를 업데이트하는 중 오류가 발생하였습니다.",e)
            return False

        return True


check=Check()