from .base import Crudbase

class CrudStatus(Crudbase):
    def select_status(self):
        sql="select s.*,t.title from coco.status_all as s, coco.task as t where s.task_id=t.id order by s.sub_id desc;"
        result = self.select_sql(sql)
        return result

    def select_status_user(self,user):
        sql="select s.*,t.title from coco.status_all as s, coco.task as t where s.task_id=t.id and s.user_id=%s order by s.sub_id desc"
        data=(user)
        result = self.select_sql(sql,data)
        return result

status_crud=CrudStatus()