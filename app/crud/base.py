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

    def delete_sql(self, query:str, data:tuple):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        con.commit()
        cnt_query = 'SELECT COUNT(*) FROM coco.aitest;'
        cur.execute(cnt_query)
        result = cur.fetchall()
        if result[0][0] == 0:
            cur.execute('ALTER TABLE coco.aitest AUTO_INCREMENT = 0;')
        con.close()
        return result[0]

    # def delete_sql(self, query:str, data:tuple, table:str):
    #     con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
    #                         db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
    #     cur = con.cursor()
    #     cur.execute(query,data)
    #     con.commit()
    #     cnt_sql = 'SELECT COUNT(*) FROM %s;'
    #     table_name = table
    #     cur.execute(cnt_sql, table_name)
    #     result = cur.fetchall()
    #     if result[0][0] == 0:
    #         ai_sql = 'ALTER TABLE %s AUTO_INCREMENT = 0;'
    #         cur.execute(ai_sql, table_name)
    #     con.close()
    #     return result[0]


    def is_auto_increase(self, num):
        #ALTER TABLE '테이블 명' AUTO_INCREMENT = '초기화 할 int';
        sql = "DELETE FROM coco.aitest WHERE id = %s"
        data = (num)
        result = self.delete_sql(self, sql, data, 'coco.aitest')
        return result