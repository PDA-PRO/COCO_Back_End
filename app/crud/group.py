from datetime import datetime
from .base import Crudbase
from core import security
import db

db_server = db.db_server

class CrudGroup(Crudbase):
    def all_groups(self):
        sql = """
            select g.id, g.name, g.desc, g.leader, count(g.id) as members, sum(u.exp) as exp
            from coco.group as g, coco.group_users as gu, coco.user as u
            where g.id = gu.group_id and gu.user_id = u.id
            group by g.id order by exp desc;
        """
        return self.select_sql(sql)
    
    def mygroup(self, user_id):
        data = (user_id)
        sql = """
            select g.id, g.name, g.desc, g.leader, count(u.user_id) as members
            from coco.group as g, coco.group_users as u
            where u.group_id = g.id in (
                select group_id from  coco.group_users where user_id = %s
            )
            group by g.id;
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
        return last_idx

    def search_user(self, user_id):
        sql = "SELECT id, name, exp, level FROM coco.user WHERE id LIKE %s OR name LIKE %s;"
        data = ('%'+user_id+'%', '%'+user_id+'%')
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
        check_sql = """
            select exists( select 1 from coco.group_users 
            where group_id = %s and user_id = %s) as is_member;
        """
        data = (info.group_id, info.user_id)
        result = self.select_sql(check_sql, data)
        print(result[0]['is_member'])
        if result[0]['is_member'] == 1:
            return False
        else:
            sql = "INSERT INTO coco.group_users (group_id, user_id) VALUES (%s, %s);"
            self.execute_sql(sql, data)
            return True

    def get_group(self, info):
        sql = """
            select g.id, g.name, g.desc, g.leader, gu.user_id, u.exp
            from coco.group as g, coco.group_users as gu, coco.user as u
            where gu.group_id = g.id and gu.group_id = %s and gu.user_id = u.id;
        """
        data = (info)
        result = self.select_sql(sql, data)
        members = []
        exp = 0
        for user in result:
            members.append([user['user_id'],user['exp']])
            exp += user['exp']

        return {
            'group_id': result[0]['id'],
            'name': result[0]['name'],
            'desc': result[0]['desc'],
            'leader': result[0]['leader'],
            'members': members,
            'exp': exp
        }
    
    def group_boardlist(self, group_id):
        sql = "SELECT * FROM coco.view_board WHERE group_id = %s order by time desc;"
        data = (group_id)
        return self.select_sql(sql, data)

    def group_workbooks(self, group_id):
        sql = """
            select w.group_id, t.*
            from coco.workbook_problems as w, coco.task_list as t
            where w.group_id = %s and w.task_id = t.id;
        """
        data = (group_id)
        return self.select_sql(sql, data)
    
    def add_problem(self, info):
        check_sql = "select exists( select 1 from coco.workbook_problems where group_id = %s and task_id = %s) as group_workbook;" 
        result = self.select_sql(check_sql, data)
        check_result = result[0]['group_workbook']
        if check_result == 1:
            return False
        else:
            sql = "INSERT INTO `coco`.`workbook_problems` (`group_id`, `task_id`) VALUES (%s, %s);"
            data = (info.group_id, info.task_id)
            self.execute_sql(sql, data)
            return True
        
    def delete_problem(self, info):
        sql = "DELETE FROM `coco`.`workbook_problems` WHERE (`group_id` = %s) and (`task_id` = %s);"
        data = (info.group_id, info.task_id)
        self.execute_sql(sql, data)
        return True

            


            

group = CrudGroup()