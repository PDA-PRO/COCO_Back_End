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
        sql="INSERT into coco.submissions (task_id, user_id, sub_id,code,time,token,callback_url ) values(%s, %s, %s, %s, %s, %s, %s)"
        data=(
            submit.taskid,
            submit.userid,
            a.hex,
            submit.sourcecode,
            now.strftime('%Y-%m-%d %H:%M:%S'),
            a.hex,
            submit.callbackurl)
        self.insert_mysql(sql,data)
        return a.hex

    def update(self,sub_id,exit_code,stdout=None,stderr=None,message=None,number_of_runs=100):
        now = time
        a=uuid.uuid1()
        sql="UPDATE coco.submissions SET exit_code=%s, stdout=%s, stderr=%s, message=%s, number_of_runs=%s WHERE sub_id=%s;"
        data=(
            exit_code,
            stdout,
            stderr,
            message,
            number_of_runs,
            sub_id)
        self.insert_mysql(sql,data)


    def execute_mysql(self,query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password='twkZNoRsk}?F%n5n*t_4',port=3307,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
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
