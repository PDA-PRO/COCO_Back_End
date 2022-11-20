import pymysql


class db_server:
    host = 'localhost'
    user = 'root'
    password = 'qwer1234'
    db = 'coco'


# mysql 실행
def execute_mysql(query):
    con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                          db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
    cur = con.cursor()
    cur.execute(query)
    result = cur.fetchall()
    con.close()
    return result

# 회원가입 정보 insert
def insert_mysql(query):
    con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                          db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()
