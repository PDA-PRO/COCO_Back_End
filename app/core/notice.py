import os
from app.core.image import image

def get_notice():
    """
    txt파일에 html형식으로 저장된 공지사항 조회
    읽는 도중 오류 발생시 None 리턴

    params
    ---------------
    returns
    - 성공적으로 파일을 읽었다면 내용 리턴
    - 읽는 도중 오류 발생시 None 리턴
    """
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
    
def update_notice(new_content):
    """
    txt파일에 html형식으로 저장된 공지사항 업데이트
    성공시 True, 실패시 False

    params
    - new_content : 새로운 공지사항 내용
    ---------------
    returns
    - bool
    """
    try:
        image.save_update_image(os.getenv("NOTICE_PATH"),os.getenv("NOTICE_PATH"),new_content,mode="u")
        with open(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt"),"w", encoding="UTF-8") as file:
            file.write(new_content)
    except Exception as e:
        print("공지사항 파일 notice.txt 를 업데이트하는 중 오류가 발생하였습니다.",e)
        return False
    return True