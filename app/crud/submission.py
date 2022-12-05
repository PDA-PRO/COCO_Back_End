import pymysql
import db
import uuid
from models.submission import Submission
from schemas.submission import Submit
import time

db_server = db.db_server

class CrudSubmission():
    
    def init_submit(self,submit:Submit):
        now = time
        a=uuid.uuid1()
        
        sql="INSERT into coco.submissions (code,time,token,callback_url,status ) values(%s, %s, %s, %s, %s);"
        sql2="insert into coco.sub_ids values (%s,%s,LAST_INSERT_ID());"
        sql3="select LAST_INSERT_ID();"
        data=(
            submit.sourcecode,
            now.strftime('%Y-%m-%d %H:%M:%S'),
            a.hex,
            submit.callbackurl,
            1)
        data2=(
            submit.userid,
            submit.taskid
        )
        query=[[sql,data],[sql2,data2]]
        id=self.insert_mysql_other(query,sql3)
        return id


    def status_update(self, sub_id,status):
        sql="UPDATE coco.submissions SET status=%s WHERE sub_id=%s;"
        data=(
            status,
            sub_id)
        self.insert_mysql([[sql,data]])

    def update(self,sub_id,exit_code,status=4,stdout=None,stderr=None,message=None,number_of_runs=100,status_id=None):
        sql="UPDATE coco.submissions SET status_id=%s ,exit_code=%s, stdout=%s, stderr=%s, message=%s, number_of_runs=%s, status=%s WHERE sub_id=%s;"
        data=(
            status_id,
            exit_code,
            stdout,
            stderr,
            message,
            number_of_runs,
            status,
            sub_id)
        self.insert_mysql([[sql,data]])

    def execute_mysql(self,query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    # 회원가입 정보 insert
    def insert_mysql(self,query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        for i in (query):
            cur.execute(i[0],i[1])
        con.commit()
        con.close()

    def insert_mysql_other(self,query,temp):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        for i in (query):
            cur.execute(i[0],i[1])
        cur.execute(temp)
        id=cur.fetchall()
        con.commit()
        con.close()
        return id[0][0]
