import pymysql
from app import db
from app.db.base import DBCursor
import os
from pymysql import converters


converions = converters.conversions
converions[pymysql.FIELD_TYPE.BIT] = lambda x: False if x == b'\x00' else True

db_server = db.db_server

def get_cursor():
    """
    db 연결 및 db cursor 획득
    정상 종료시 db 변경사항 commit 및 db 연결 종료
    """
    # con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port, charset='utf8')  # 한글처리 (charset = 'utf8')
    con = pymysql.connect(host=os.getenv("DATABASE_HOST"),
                                 port=int(os.getenv("DATABASE_SOCKET")),
                                 user=os.getenv("DATABASE_USERNAME"),
                                 password=os.getenv("DATABASE_PASSWORD"),
                                 database='coco',
                                 charset='utf8',
                                 conv=converions)
    cur = con.cursor(pymysql.cursors.DictCursor)
    try:
        yield DBCursor(cursor=cur)
        con.commit()
    # except :
    #     print("sql 오류로 연결을 종료합니다")
    finally:
        con.close()