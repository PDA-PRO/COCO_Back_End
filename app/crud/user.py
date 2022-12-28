import db
import uuid
from .base import Crudbase

db_server = db.db_server

class CrudUser(Crudbase):
    def check_db(self, user):
        sql = "SELECT id, pw, role FROM `coco`.`user` where id = %s;"
        data=(user.id)
        result = self.select_sql(sql,data)
        if len(result) == 0:#로그인 정보가 없다면
            return 0
        else:#로그인 정보가 있다면
            if user.pw == result[0]["pw"]:#패스워드가 맞다면
                if result[0]["role"]=='1':#로그인 한사람이 선생이라면
                    if self.check_manager(user.id):#매니저인지 확인
                        return 2#매니저면 매니저 로그인 2
                    else:#매니저가 아니면 그냥 로그인
                        return 1
                else:#선생이 아니라면 그냥 로그인
                    return 1
            return 0

    def check_manager(self, id):
        sql = "SELECT is_manager FROM `coco`.`teacher` where user_id = %s;"
        data=(id)
        result = self.select_sql(sql,data)
        if len(result) == 0:
            return False
        else:
            if result[0]["is_manager"]==1:
                return True
            return False

    # 새로운 회원 정보 insert
    def insert_db(self, user):
        sql = "INSERT INTO `coco`.`user` (`id`, `pw`, `name`, `role`, `email`) VALUES (%s,%s,%s,%s,%s)"
        data=(user.id, user.pw, user.name, user.role, user.email)
        self.execute_sql(sql,data)
        if user.role == 0:
            sql = "INSERT INTO `coco`.`student` (`std_id`, `rate`, `age`, `user_id`) VALUES (%s,%s,%s,%s);"
            data=(uuid.uuid1(), 0.00, user.age, user.id)
        else:
            sql = "INSERT INTO `coco`.`teacher` (`tea_id`, `is_manager`, `user_id`) VALUES (%s,%s,%s);"
            data=(uuid.uuid1(), 0, user.id)
        self.execute_sql(sql,data)
        return 1


    # 회원가입시 아이디 중복 검사
    def check_id(self, id):
        sql = "SELECT id FROM `coco`.`user` where id = %s;"
        data=(id)
        result = self.select_sql(sql,data)
        if len(result) == 0:
            return 1
        else:
            return 0

    #id 찾기
    def find_id(self, info):
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

user_crud=CrudUser()