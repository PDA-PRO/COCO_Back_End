from api.deps import get_cursor
from contextlib import contextmanager
from core.security import get_password_hash
import os
from tenacity import retry, stop_after_attempt, wait_fixed 

@retry(wait=wait_fixed(5),stop=stop_after_attempt(10),)
def ready():
    #fastapi 시작
    print("백엔드 static 폴더 검증")
    if not os.path.exists(os.getenv("TASK_PATH")):
        os.mkdir(os.getenv("TASK_PATH"))
    if not os.path.exists(os.getenv("NOTICE_PATH")):
        os.mkdir(os.getenv("NOTICE_PATH"))
    if not os.path.exists(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt")):
        with open(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt"),"w", encoding="UTF-8") as file:
            file.write("")
    if not os.path.exists(os.getenv("BOARD_PATH")):
        os.mkdir(os.getenv("BOARD_PATH"))
    if not os.path.exists(os.getenv("PROFILE_PATH")):
        os.mkdir(os.getenv("PROFILE_PATH"))
    if not os.path.exists(os.getenv("ROADMAP_PATH")):
        os.mkdir(os.getenv("ROADMAP_PATH"))
    if not os.path.exists(os.getenv("LINT_PATH")):
        os.mkdir(os.getenv("LINT_PATH"))

    # admin 계정이 없을 시 초기값으로 계정 생성
    try:
        with contextmanager(get_cursor)() as cur:
            if cur.select_sql("select * from coco.user where id='admin'"):
                pass
            else:
                sql = "INSERT INTO `coco`.`user` (`id`, `pw`, `name`, `role`, `email`) VALUES (%s,%s,%s,%s,%s)"
                data=(os.getenv("ADMIN_ID"), get_password_hash(os.getenv("ADMIN_PW")), 'admin', 1, 'admin@dot.com')
                cur.execute_sql(sql,data)
    except Exception as e:
        raise e
        

if __name__=="__main__":
    ready()

