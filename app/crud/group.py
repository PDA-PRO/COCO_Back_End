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
        group_sql.append("INSERT INTO `coco`.`group` (`name`, `desc`, `leader`) VALUES (%s, %s, %s);")
        group_data.append((info.name, info.desc, info.leader))
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
    
    # 그룹 개수 -> ai 초기화 때문에
    def group_len(self):
        sql = "select count(id) as cnt from coco.group;"
        result =  self.select_sql(sql)
        return result[0]['cnt']
    
    # ai 초기화
    def ai_reset(self, num):
        sql = ["set @cnt = 0;", "update coco.group set coco.group.id = @cnt:=@cnt+1;", "alter table coco.group auto_increment = %s;"]
        data = (num)
        self.group_ai_reset(sql, data)
    
    def leave_group(self, info):
        sql = "DELETE FROM `coco`.`group_users` WHERE (`group_id` = %s AND `user_id` = %s);"
        data = (info.group_id, info.user_id)
        self.execute_sql(sql, data)
        len_sql = "select count(group_id) as cnt from coco.group_users where group_id = %s;"
        len_data = (info.group_id)
        group_len = self.select_sql(len_sql, len_data)
        if group_len == 0:
            self.delete_group(info.group_id)

    def delete_group(self, info):
        sql = "DELETE FROM `coco`.`group` WHERE (`id` = %s);"
        data = (info)
        self.execute_sql(sql, data)
        len = self.group_len()
        print(len)
        self.ai_reset(len)

    def invite_member(self, info):
        sql = "INSERT INTO coco.group_users (group_id, user_id) VALUES (%s, %s);"
        data = (info.group_id, info.user_id)
        self.execute_sql(sql, data)


            


            

group = CrudGroup()