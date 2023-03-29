from .base import Crudbase
from core import security
import db

db_server = db.db_server

class CrudStdManage(Crudbase):
    def search_student(self):
        sql = """
            select u.id, u.name, u.role, u.email, u.exp
            from coco.student as s,coco.user as u
            where u.id = s.user_id;
        """
        result = self.select_sql(sql)
        return result
    
    def add_student(self, info):
        data = (info.tea_id, info.std_id)
        check_sql = "select exists( select 1 from coco.std_manage where tea_id = %s and std_id = %s) as my_student;"
        result = self.select_sql(check_sql, data)
        check_result = result[0]['my_student']
        if check_result == 0:
            sql = "INSERT INTO `coco`.`std_manage` (`tea_id`, `std_id`) VALUES (%s, %s);"
            self.execute_sql(sql, data)
            return True
        else:
            return False #학생이 이미 등록된 경우
    
    def my_students(self, tea_id):
        sql = """
            select u.id, u.name, u.role, u.email, u.exp
            from coco.std_manage as s, coco.user as u
            where s.tea_id = %s and s.std_id = u.id;
        """
        data = (tea_id)
        result = self.select_sql(sql, data)
        return result
    
    def delete_mystudents(self, info):
        sql = "DELETE FROM `coco`.`std_manage` WHERE (`tea_id` = %s) and (`std_id` = %s);"
        data = (info.tea_id, info.std_id)
        self.execute_sql(sql, data)
        return True


std_manage = CrudStdManage()