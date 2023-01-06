import pymysql
import db
import uuid
from schemas.submission import Submit
import time
from .base import Crudbase

db_server = db.db_server

class CrudSubmission(Crudbase):
    
    def init_submit(self,submit:Submit):
        now = time
        a=uuid.uuid1()
        sql=[]
        data=[]
        sql.append("INSERT into coco.submissions (code,time,token,callback_url,status,lang ) values(%s, %s, %s, %s, %s,%s);")
        sql.append("insert into coco.sub_ids values (%s,%s,LAST_INSERT_ID());")
        data.append((
            submit.sourcecode,
            now.strftime('%Y-%m-%d %H:%M:%S'),
            a.hex,
            submit.callbackurl,
            1,
            submit.lang))
        data.append((
            submit.userid,
            submit.taskid
        ))
        id=self.insert_last_id(sql,data)
        return id

    def select_submit(self,sub_id):
        sql="SELECT * FROM coco.submissions WHERE sub_id=%s;"
        data=(sub_id)
        row=self.select_sql(sql,data)
        return row

    def status_update(self, sub_id,status):
        sql="UPDATE coco.submissions SET status=%s WHERE sub_id=%s;"
        data=(
            status,
            sub_id)
        self.execute_sql(sql,data)

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
        self.execute_sql(sql,data)

submission_crud=CrudSubmission()