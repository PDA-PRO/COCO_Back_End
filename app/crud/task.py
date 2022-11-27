import pymysql
import db
import uuid
from models.task import Task
import time

db_server = db.db_server

class Crudtask():
    
    def select_task(self,id):
        sql="SELECT * FROM coco.task WHERE id=%s"
        data=id
        result=self.execute_mysql(sql,data)
        print(result[0])
        return result[0]


    def execute_mysql(self,query,data):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password='twkZNoRsk}?F%n5n*t_4',port=3307,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        result = cur.fetchall()
        con.close()
        return result

    # 회원가입 정보 insert
    def insert_mysql(self,query,data):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password='twkZNoRsk}?F%n5n*t_4',port=3307,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        con.commit()
        con.close()
