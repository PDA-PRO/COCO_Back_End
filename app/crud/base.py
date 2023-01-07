import pymysql
import db

db_server = db.db_server

class Crudbase():
    def select_sql(self, query,data:tuple=None):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute(query,data)
        result = cur.fetchall()
        con.close()
        return result

    def execute_sql(self, query:str,data:tuple):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        con.commit()
        con.close()

    def insert_last_id(self,query,data):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor(pymysql.cursors.DictCursor)
        for i in range(len(query)):
            cur.execute(query[i],data[i])
        cur.execute("select LAST_INSERT_ID() as id;")
        id=cur.fetchall()
        con.commit()
        con.close()
        return id[0]["id"]
    
    def reset_auto_increment(self, cnt_query, reset_query):
        print(cnt_query, reset_query)
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                    db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(cnt_query)
        row_cnt = cur.fetchall()
        print(row_cnt[0][0])
        if row_cnt[0][0] == 0:
            cur.execute(reset_query)
        con.commit()
        con.close()
        



