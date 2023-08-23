import pymysql
import db
from db.base import DBCursor

db_server = db.db_server

def get_cursor():
    """
    db 연결 및 db cursor 획득
    정상 종료시 db 변경사항 commit 및 db 연결 종료
    """
    con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                        db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
    cur = con.cursor(pymysql.cursors.DictCursor)
    try:
        print("db 연결 생성")
        yield DBCursor(cursor=cur)
        con.commit()
    except :
        print("sql 오류로 연결을 종료합니다")
    finally:
        print("db 연결 종료")
        con.close()