import db
import uuid
from .base import Crudbase
from core import security

db_server = db.db_server

class CrudUser(Crudbase):

    def get_user(self,user):
        sql = "SELECT id, pw, name, role, exp, level FROM `coco`.`user` where id = %s;"
        data=(user)
        result = self.select_sql(sql,data)
        return result

    def check_db(self, user_id, user_pw):
        result = self.get_user(user_id)
        if len(result) == 0:#로그인 정보가 없다면
            return None
        else:#로그인 정보가 있다면
            if security.verify_password(user_pw, result[0]["pw"]):#패스워드가 맞다면
                return result[0]
            return None

    def insert_db(self, user):
        """
        새로운 회원 정보 insert
        pw해쉬값 저장
        """
        sql = "INSERT INTO `coco`.`user` (`id`, `pw`, `name`, `role`, `email`) VALUES (%s,%s,%s,%s,%s)"
        data=(user.id, security.get_password_hash(user.pw), user.name, user.role, user.email)
        self.execute_sql(sql,data)
        return 1


    def check_id(self, id):
        """
        회원가입시 아이디 중복 검사
        """
        sql = "SELECT id FROM `coco`.`user` where id = %s;"
        data=(id)
        result = self.select_sql(sql,data)
        if len(result) == 0:
            return 1
        else:
            return 0

    def find_id(self, info):
        """
        id 찾기
        """
        sql = "SELECT id FROM `coco`.`user` WHERE name = %s AND email = %s"
        data=(info.name,info.email)
        result = self.select_sql(sql,data)
        if len(result) == 0:
            return 0
        else:
            return result[0]["id"]

    #pw 찾기
    def find_pw(self, info):
        sql = "SELECT pw FROM `coco`.`user` WHERE name = %s AND id = %s AND email = %s"
        data=(info.name,info.id,info.email)
        result = self.select_sql(sql,data)
        if len(result) == 0:
            return 0
        else:
            return result[0]["pw"]
    
    #유저의 경험치 업데이트
    def update_exp(self,user_id):
        sql="SELECT distinct user_id,task_id,diff FROM coco.user_problem where user_id=%s and status=3;"
        data=(user_id)
        result=self.select_sql(sql,data)

        new_exp=0
        for i in result:
            new_exp+=i.get("diff")*100
        sql="UPDATE coco.user SET exp = %s WHERE (id = %s);"
        data=(new_exp,user_id)
        self.execute_sql(sql,data)

    def user_list(self):
        sql = "select id, name,exp,level from coco.user;"
        result = self.select_sql(sql)
        return result

    def manager_list(self):
        sql = "select id, name from coco.user where (role = '1');"
        result = self.select_sql(sql)
        return result
    
    def add_manager(self, user_id):
        sql = "UPDATE `coco`.`user` SET `role` = '1' WHERE (`id` = %s);"
        data = (user_id)
        self.execute_sql(sql, data)
        return True
    
    def delete_manager(self, user_id):
        sql = "UPDATE `coco`.`user` SET `role` = '0' WHERE (`id` = %s);"
        data = (user_id)
        self.execute_sql(sql, data)
        return True

    def search_user(self, user_id):
        sql = "SELECT id, name, exp, level FROM coco.user WHERE id LIKE %s OR name LIKE %s;"
        data = ('%'+user_id+'%', '%'+user_id+'%')
        return self.select_sql(sql, data)
    


user_crud=CrudUser()