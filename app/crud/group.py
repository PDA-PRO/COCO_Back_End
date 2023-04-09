from .base import Crudbase
from core import security
import db

db_server = db.db_server

class CrudGroup(Crudbase):
    def all_groups(self):
        sql = """
            select g.id, g.name, g.desc, count(g.id) as members
            from coco.group as g, coco.group_users as u
            where g.id = u.group_id group by g.id;
        """
        return self.select_sql(sql)
    
    def mygroup(self, user_id):
        data = (user_id)
        sql = """
            select g.id, g.name, g.desc, count(u.user_id) as members
            from coco.group as g, coco.group_users as u
            where u.group_id = g.id in (
                select group_id from  coco.group_users where user_id = %s
            );
        """
        return self.select_sql(sql, data)

group = CrudGroup()