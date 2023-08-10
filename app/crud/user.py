from fastapi import HTTPException,status
import db
from schemas.user import *
from .base import Crudbase
from core import security
from models.user import User

db_server = db.db_server

class CrudUser(Crudbase[User,str]):
    def get_user(self, user_id:int, user_pw:int):
        """
        해당 user가 존재하고 pw가 맞으면 
        유저 정보 조회
        없으면 None

        - user_id : id
        - user_pw : pw
        """
        sql = "SELECT id, pw, name, role, exp, level FROM `coco`.`user` where id = %s;"
        data=(user_id)
        result = self.select_sql(sql,data)
        if len(result) == 0:#로그인 정보가 없다면
            return None
        else:#로그인 정보가 있다면
            if security.verify_password(user_pw, result[0]["pw"]):#패스워드가 맞다면
                return result[0]
            return None

    def create_user(self, user:SignUp):
        """
        새로운 회원 생성
        pw해쉬값 저장

        - user
            - name : 실명
            - id : id
            - pw : 비밀번호는 영어, 숫자, 특수기호를 포함하고 8-15 길이
            - email : 이메일
        """
        sql = "INSERT INTO `coco`.`user` (`id`, `pw`, `name`, `role`, `email`) VALUES (%s,%s,%s,%s,%s)"
        data=(user.id, security.get_password_hash(user.pw), user.name, 0, user.email)
        self.execute_sql(sql,data)
        return 1


    def exist_id(self, id:str):
        """
        아이디 조회
        존재하면 1 존재하지 않으면 0

        - id : user id
        """
        sql = "SELECT id FROM `coco`.`user` where id = %s;"
        data=(id)
        result = self.select_sql(sql,data)
        if len(result):
            return id
        else:
            raise HTTPException(            
                status_code=status.HTTP_404_NOT_FOUND,
                detail="id가 존재하지 않습니다.")

    def get_id(self, info:FindId):
        """
        id 찾기

        - info
            - name : 실명
            - email : 이메일
        """
        sql = "SELECT id FROM `coco`.`user` WHERE name = %s AND email = %s"
        data=(info.name,info.email)
        result = self.select_sql(sql,data)
        if len(result) == 0:
            return 0
        else:
            return result[0]["id"]

    def update_pw(self, info:Login):
        """
        해당 user의 pw 업데이트

        - info 
            - id : id
            - pw : pw
        """
        sql = "UPDATE coco.user SET pw = %s WHERE id = %s;"
        data = (security.get_password_hash(info.pw), info.id)
        self.execute_sql(sql, data)
        
    def update_email(self, info:UpdateEmail):
        """
        해당 user의 email 업데이트

        - info 
            - id : id
            - email : email
        """
        
        sql = "UPDATE coco.user SET email = %s WHERE id = %s;"
        data = (info.email, info.id)
        self.execute_sql(sql, data)
        return 1
    
    def update_role(self, info:UpdateRole):
        """
        해당 user의 role 업데이트

        - info 
            - id : id
            - role : role | 0 -> 일반 유저 1 -> 관리자
        """
        
        sql = "UPDATE coco.user SET role = %s WHERE id = %s;"
        data = (info.role, info.id)
        self.execute_sql(sql, data)
        return 1
    
    def update_exp(self,user_id:str):
        """
        user 경험치 업데이트

        - user_id : id
        """
        sql="SELECT distinct user_id,task_id,diff FROM coco.user_problem where user_id=%s and status=3;"
        data=(user_id)
        result=self.select_sql(sql,data)

        new_exp=0
        for i in result:
            new_exp+=i.get("diff")*100
        sql="UPDATE coco.user SET exp = %s WHERE (id = %s);"
        data=(new_exp,user_id)
        self.execute_sql(sql,data)
    
    def add_manager(self, user_id:str):
        """
        일반 user에서 관리자로 업데이트

        - user_id 
        """
        sql = "UPDATE `coco`.`user` SET `role` = '1' WHERE (`id` = %s);"
        data = (user_id)
        self.execute_sql(sql, data)
        return True
    
    def read_manager(self):
        """
        모든 관리자 조회

        """
        sql = "select id, name, role from `coco`.`user` where `role` = 1"
        return self.select_sql(sql)

    def search_user(self, info:UserListIn):
        """
        user의 id나 name으로 검색
        id, name, role 값 리턴

        - info
            - keyword : user의 id나 name | 값이 없을 시 모든 user 리스트 리턴
            - size : 한 페이지의 크기
            - page : 페이지
            - role : 0 -> 일반 유저 1-> 관리자
        """
        if info.keyword or info.role!=None:
            sql = "SELECT id, name, role FROM coco.user WHERE"
            plus_sql=[]
            plus_data=[]
            if info.keyword:
                plus_sql.append( " (id LIKE %s OR name LIKE %s)")
                plus_data.append('%'+info.keyword+'%')
                plus_data.append('%'+info.keyword+'%')
            if info.role!=None:
                plus_sql.append(" role=%s")
                plus_data.append(info.role)
            sql+=" and".join(plus_sql)
            data=tuple(plus_data)
        else:
            sql = "SELECT id, name, role FROM coco.user"
            data = ()
        total,result=self.select_sql_with_pagination(sql, data,info.size,info.page)
        return {"total":total,"size":info.size,"userlist":result}

    def create_mytask(self, user_id,task_id):
        data = (user_id, task_id)
        check_sql = "select exists( select 1 from coco.my_tasks where user_id = %s and task_num = %s) as my_task;"
        result = self.select_sql(check_sql, data)
        check_result = result[0]['my_task']
        if check_result == 0:
            sql ="INSERT INTO `coco`.`my_tasks` (`user_id`, `task_num`, `solved`) VALUES (%s, %s, %s);"
            data = (user_id, task_id, 0)
            self.execute_sql(sql, data)
            return True
        else:
            return False
        
    def read_mytask(self, user_id):
        sql = """
            SELECT t.*, m.solved
            FROM coco.my_tasks as m, coco.task_list as t
            WHERE user_id = %s and m.task_num = t.id;
        """
        data = (user_id)
        result = self.select_sql(sql, data)
        return result

    def delete_mytask(self, user_id,task_id):
        sql = "DELETE FROM `coco`.`my_tasks` WHERE (`user_id` = %s) and (`task_num` = %s);"
        data = (user_id, task_id)
        self.execute_sql(sql, data)
        return True

user_crud=CrudUser(User)