import pymysql
import db

db_server = db.db_server

class CrudStatus():
    def select_status(self):
        sql="select s.*,t.title from coco.status_all as s, coco.task as t where s.task_id=t.id order by s.sub_id desc;"
        result = self.execute_mysql(sql)
        contents = []
        for i in result:
            content = {
                'sub_id': i[0],
                'user_id': i[1],
                'task_id': i[2],
                'status': i[3],
                'time': i[4],
                'title':i[5]
            }
            contents.append(content)
        return contents

    def select_status_user(self,user):
        sql="select s.*,t.title from coco.status_all as s, coco.task as t where s.task_id=t.id and s.user_id=%s order by s.sub_id desc"
        data=(user)
        result = self.execute_mysql(sql,data)
        contents = []
        for i in result:
            content = {
                'sub_id': i[0],
                'user_id': i[1],
                'task_id': i[2],
                'status': i[3],
                'time': i[4],
                'title':i[5]
            }
            contents.append(content)
        return contents

    def execute_mysql(self,query,data=None):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        if data:
            cur.execute(query,data)
        else:
            cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    def insert_mysql(self,query,data=None):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        if data:
            cur.execute(query,data)
        else:
            cur.execute(query)
        con.commit()
        con.close()