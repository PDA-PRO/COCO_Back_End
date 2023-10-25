from fastapi import HTTPException,status
from app.schemas.user import *
from .base import Crudbase
from app.core import security
from app.models.user import User
from app.db.base import DBCursor
from app.crud.alarm import alarm_crud

class CrudUser(Crudbase[User,str]):
    def get_user(self, db_cursor:DBCursor,user_id:int, user_pw:int):
        """
        해당 user가 존재하고 pw가 맞으면 
        유저 정보 조회
        없으면 None

        - user_id : id
        - user_pw : pw
        """
        sql = "SELECT id, pw, name, role, exp, tutor FROM `coco`.`user` where id = %s;"
        data=(user_id)
        result = db_cursor.select_sql(sql,data)

        alarm = alarm_crud.read_alarm(db_cursor, user_id)
        if len(result) == 0:#로그인 정보가 없다면
            return None
        else:#로그인 정보가 있다면
            if security.verify_password(user_pw, result[0]["pw"]):#패스워드가 맞다면
                return (result[0], alarm)
            return None

    def create_user(self,db_cursor:DBCursor, user:SignUp):
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
        db_cursor.execute_sql(sql,data)
        return 1

    def search_user(self, db_cursor:DBCursor,info:UserListIn):
        """
        user의 id나 name, role, tutor로 검색
        id, name, role, tutor 값 리턴

        params
        - info
            - keyword : user의 id나 name | 값이 없을 시 모든 user 리스트 리턴
            - size : 한 페이지의 크기
            - page : 페이지
            - role : 0 -> 일반 유저 1-> 관리자
            - tutor : 0 -> 일반 유저 1-> 튜터
        -----------------------------------------------
        returns
        - userlist : 쿼리 결과
        - size와 page가 있을 경우 
            - total : 전체 결과
            - size : 페이지 크기
        """
        if info.keyword or info.role!=None or info.tutor!=None:
            sql = "SELECT id, name, role, exp FROM coco.user WHERE"
            plus_sql=[]
            plus_data=[]
            if info.keyword:
                plus_sql.append( " (id LIKE %s OR name LIKE %s)")
                plus_data.append('%'+info.keyword+'%')
                plus_data.append('%'+info.keyword+'%')
            if info.role!=None:
                plus_sql.append(" role=%s")
                plus_data.append(info.role)
            if info.tutor!=None:
                plus_sql.append(" tutor=%s")
                plus_data.append(info.tutor)
            sql+=" and".join(plus_sql)
            data=tuple(plus_data)
        else:
            sql = "SELECT id, name, role, exp FROM coco.user"
            data = ()
        
        if info.size and info.page:
            total,result=db_cursor.select_sql_with_pagination(sql, data,info.size,info.page)
            for i in range(len(result)):
                level = self.get_level(result[i]['exp'])
                result[i]['level'] = level['level']
            return {"total":total,"size":info.size,"userlist":result}
        else:
            result=db_cursor.select_sql(sql, data)
            print(result)
            for i in range(len(result)):
                level = self.get_level(result[i]['exp'])
                result[i]['level'] = level['level']
            return {"userlist":result}

    def create_mytask(self,db_cursor:DBCursor, user_id,task_id):
        data = (user_id, task_id)
        check_sql = "select exists( select 1 from coco.my_tasks where user_id = %s and task_num = %s) as my_task;"
        result = db_cursor.select_sql(check_sql, data)
        check_result = result[0]['my_task']
        if check_result == 0:
            sql ="INSERT INTO `coco`.`my_tasks` (`user_id`, `task_num`, `solved`) VALUES (%s, %s, %s);"
            data = (user_id, task_id, 0)
            db_cursor.execute_sql(sql, data)
            return True
        else:
            return False
        
    def read_mytask(self, db_cursor:DBCursor,user_id):
        sql = """
            SELECT t.*, m.solved
            FROM coco.my_tasks as m, coco.task_list as t
            WHERE user_id = %s and m.task_num = t.id;
        """
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        return result

    def delete_mytask(self, db_cursor:DBCursor,user_id,task_id):
        sql = "DELETE FROM `coco`.`my_tasks` WHERE (`user_id` = %s) and (`task_num` = %s);"
        data = (user_id, task_id)
        db_cursor.execute_sql(sql, data)
        return True

    def user_level(self, db_cursor:DBCursor, user_id):
        sql = 'SELECT id, exp FROM coco.user where id = %s;'
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        if not result:
            raise HTTPException(status_code=404, detail="user not found")
        
        level_info = self.get_level(result[0]['exp'])

        # 전체에서 몇등인지
        rank_sql = 'SELECT ROW_NUMBER() OVER ( ORDER BY exp desc ) AS ranking, id, exp FROM coco.user;'
        rank_result = db_cursor.select_sql(rank_sql, ())
        for i in range(len(rank_result)):
            if user_id == rank_result[i]['id']:
                rank = rank_result[i]['ranking']
                break

        return {'user_id': user_id, 'exp': result[0]['exp'], 
                'level': level_info['level'], 'points': level_info['points'], 'rank': rank}

    # 레벨 계산
    def get_level(self, exp):
        level = 1
        points = 0
        # 레벨 도달 포인트
        arr_points = [0, 200, 700, 1500, 3100, 6300, 12700, 25500, 55300]
        for i in range(1, len(arr_points)):
            if exp < arr_points[i]:
                level = i
                points = arr_points[i] - exp
                break

        return {'level': level, 'points': points}

    def update_board(self, db_cursor:DBCursor, info, user_id):
        if info.code == None:
            sql = "UPDATE `coco`.`boards` SET `context` = %s, `title` = %s WHERE (`id` = %s);"
            data = (info.context, info.title, info.board_id)
        else:
            sql = "UPDATE `coco`.`boards` SET `context` = %s, `title` = %s, `code` = %s WHERE (`id` = %s);"
            data = (info.context, info.title, info.code, info.board_id)
        db_cursor.execute_sql(sql, data)
        return {'id': info.board_id}
    
user_crud=CrudUser(User)