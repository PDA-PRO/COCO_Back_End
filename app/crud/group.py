from datetime import datetime
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
    
    def userlist(self):
        sql = "select id, name, exp from coco.user;"
        return self.select_sql(sql)
    
    def make_group(self, info):
        group_sql, group_data = [], []
        group_sql.append("INSERT INTO `coco`.`group` (`name`, `desc`) VALUES (%s, %s);")
        group_data.append((info.name, info.desc))
        last_idx = self.insert_last_id(group_sql, group_data)
        print(last_idx)
        member_sql = "INSERT INTO coco.group_users (group_id, user_id) VALUES (%s, %s);"
        for member in info.members:
            data = (last_idx, member)
            self.execute_sql(member_sql, data)

    def search_user(self, info):
        print(info)
        sql = "SELECT id, name, exp, level FROM coco.user WHERE id LIKE %s OR name LIKE %s;"
        data = ('%'+info+'%', '%'+info+'%')
        return self.select_sql(sql, data)

            

group = CrudGroup()