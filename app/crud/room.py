from datetime import datetime
from .base import Crudbase
from core import security
from schemas.room import *
from models.room import *
import db

db_server = db.db_server

class CrudRoom(Crudbase):
    def create_room(self, info:CreateRoom):
        """
        study room 생성에 관련된 데이터, 테이블 생성
        
        - info : study room 생성에 필요한 입력 데이터
            - name : 이름
            - desc : 간략한 설명
            - leader : 만든 user id
            - members : user들의 id
        """
        #study room 정보 추가
        room_sql="INSERT INTO `coco`.`room` ( `name`, `desc`, `leader`) VALUES (%s, %s, %s);"
        room_data=(info.name,info.desc,info.leader)
        last_idx = self.insert_last_id([room_sql], [room_data])

        #study room에 포함된 멤버 추가
        member_sql = "INSERT INTO coco.room_ids (room_id, user_id) VALUES (%s, %s);"
        for member in info.members:
            member_data = (last_idx, member)
            self.execute_sql(member_sql, member_data)

        #관련 테이블 생성
        table_sql=[]
        table_data=[]
        table_sql.append("""
            CREATE TABLE `room`.`%s_roadmap` (
            `id` INT NOT NULL auto_increment,
            `name` VARCHAR(45) NULL,
            `desc` TEXT NULL,
            PRIMARY KEY (`id`));
        """)
        table_sql.append("""
            CREATE TABLE `room`.`%s_question` (
            `id` INT NOT NULL auto_increment,
            `question` MEDIUMTEXT NULL,
            `writer` VARCHAR(45) NULL,
            PRIMARY KEY (`id`));
        """)
        table_sql.append("""
            CREATE TABLE `room`.`%s_qa` (
            `a_id` INT NOT NULL auto_increment,
            `q_id` INT NOT NULL,
            `answer` MEDIUMTEXT NULL,
            `ans_writer` VARCHAR(45) NULL,
            PRIMARY KEY (`a_id`),
            foreign key (`q_id`) REFERENCES `%s_question` (`id`));
        """)
        table_sql.append("""
            CREATE TABLE `room`.`%s_roadmap_ids` (
            `roadmap_id` INT NOT NULL,
            `task_id` INT NOT NULL,
            PRIMARY KEY (`roadmap_id`,`task_id`),
            foreign key (`roadmap_id`) REFERENCES `%s_roadmap` (`id`));
        """)
            
        table_data=[(last_idx),(last_idx),(last_idx,last_idx),(last_idx,last_idx)]
        for sql,data in zip(table_sql,table_data):
            self.execute_sql(sql,data)

        return True
    
    def read_all_rooms(self):
        """
        모든 study room 정보 리턴
        """
        sql = "SELECT * FROM coco.room;"
        return self.select_sql(sql)
    
    def delete_room(self, room_id:int):
        """
        study room삭제에 관련된 데이터, 테이블 삭제
        
        - room_id : 삭제할 room의 id값
        """
        #room 테이블에서 id값의 정보 삭제
        sql = "DELETE FROM `coco`.`room` WHERE (`id` = %s);"
        data = (room_id)
        self.execute_sql(sql,data)

        #관련 테이블 삭제
        sql = "DROP TABLE `room`.`%s_qa`, `room`.`%s_question`, `room`.`%s_roadmap`, `room`.`%s_roadmap_ids`"
        data = (room_id,room_id,room_id,room_id)
        self.execute_sql(sql, data)

        return True
    
    def insert_members(self, members:RoomMember):
        """
        해당 id의 study room에 member를 추가
        
        - members : 추가할 room의 id
            - room_id : room id
            - user_id : user id
        """
        #study room에 포함된 멤버 추가
        member_sql = "INSERT INTO coco.room_ids (room_id, user_id) VALUES (%s, %s);"
        for member in members.user_id:
            try:
                member_data = (members.room_id, member)
                self.execute_sql(member_sql, member_data)
            except Exception as e:
                print(e,"멤버 추가 오류")
        
        return True


    def delete_members(self, members:RoomMember):
        '''
        해당 id의 study room에 member를 삭제

        - members : 삭제할 room의 id
            - room_id : room id
            - user_id : user id
        '''
        member_sql = "DELETE FROM `coco`.`room_ids` WHERE (`room_id` = %s) and (`user_id` = %s);"
        for member in members.user_id:
            member_data = (members.room_id, member)
            self.execute_sql(member_sql, member_data)

        return True
    
    def myroom(self, user_id):
        data = (user_id)
        sql = """
            select g.id, g.name, g.desc, g.leader, count(u.user_id) as members
            from coco.room as g, coco.room_users as u
            where u.room_id = g.id in (
                select room_id from  coco.room_users where user_id = %s
            )
            room by g.id;
        """
        return self.select_sql(sql, data)
    
    def userlist(self):
        sql = "select id, name, exp from coco.user;"
        return self.select_sql(sql)
    
    

    def search_user(self, user_id):
        sql = "SELECT id, name, exp, level FROM coco.user WHERE id LIKE %s OR name LIKE %s;"
        data = ('%'+user_id+'%', '%'+user_id+'%')
        return self.select_sql(sql, data)
    
    def leave_room(self, info):
        sql = "DELETE FROM `coco`.`room_users` WHERE (`room_id` = %s AND `user_id` = %s);"
        data = (info.room_id, info.user_id)
        self.execute_sql(sql, data)
        len_sql = "select count(room_id) as cnt from coco.room_users where room_id = %s;"
        len_data = (info.room_id)
        room_len = self.select_sql(len_sql, len_data)
        if room_len == 0:
            self.delete_room(info.room_id)
        return True

    

    def invite_member(self, info):
        check_sql = """
            select exists( select 1 from coco.room_users 
            where room_id = %s and user_id = %s) as is_member;
        """
        data = (info.room_id, info.user_id)
        result = self.select_sql(check_sql, data)
        print(result[0]['is_member'])
        if result[0]['is_member'] == 1:
            return False
        else:
            sql = "INSERT INTO coco.room_users (room_id, user_id) VALUES (%s, %s);"
            self.execute_sql(sql, data)
            if info.apply:
                del_sql = "DELETE FROM `coco`.`room_apply` WHERE (`room_id` = %s) and (`user_id` = %s);"
                del_data = (info.room_id, info.user_id)
                self.execute_sql(del_sql, del_data)
            return True

    def get_room(self, info):
        sql = """
            select g.id, g.name, g.desc, g.leader, gu.user_id, u.exp
            from coco.room as g, coco.room_users as gu, coco.user as u
            where gu.room_id = g.id and gu.room_id = %s and gu.user_id = u.id;
        """
        data = (info)
        result = self.select_sql(sql, data)
        members = []
        exp = 0
        for user in result:
            members.append([user['user_id'],user['exp']])
            exp += user['exp']

        return {
            'room_id': result[0]['id'],
            'name': result[0]['name'],
            'desc': result[0]['desc'],
            'leader': result[0]['leader'],
            'members': members,
            'exp': exp
        }
    
    def room_boardlist(self, room_id):
        sql = "SELECT * FROM coco.view_board WHERE room_id = %s order by time desc;"
        data = (room_id)
        return self.select_sql(sql, data)

    def room_workbooks(self, room_id):
        sql = """
            select w.room_id, t.*
            from coco.workbook_problems as w, coco.task_list as t
            where w.room_id = %s and w.task_id = t.id;
        """
        data = (room_id)
        return self.select_sql(sql, data)
    
    def add_problem(self, info):
        check_sql = "select exists( select 1 from coco.workbook_problems where room_id = %s and task_id = %s) as room_workbook;" 
        data = (info.room_id, info.task_id)
        result = self.select_sql(check_sql, data)
        check_result = result[0]['room_workbook']
        if check_result == 1:
            return False
        else:
            sql = "INSERT INTO `coco`.`workbook_problems` (`room_id`, `task_id`) VALUES (%s, %s);"
            data = (info.room_id, info.task_id)
            self.execute_sql(sql, data)
            return True
        
    def delete_problem(self, info):
        sql = "DELETE FROM `coco`.`workbook_problems` WHERE (`room_id` = %s) and (`task_id` = %s);"
        data = (info.room_id, info.task_id)
        self.execute_sql(sql, data)
        return True
    
    def is_my_room(self, info):
        sql = "select exists( select 1 from coco.room_users where room_id = %s and user_id = %s) as isMember;"
        data = (info.room_id, info.user_id)
        result = self.select_sql(sql, data)
        if result[0]['isMember'] == 0:
            return False
        else:
            return True
        
    def join_room(self, info):
        check_sql = "select exists( select 1 from coco.room_apply where room_id = %s and user_id = %s) as isJoin;"
        check_data = (info.room_id, info.user_id)
        result = self.select_sql(check_sql, check_data)
        if result[0]['isJoin'] == 1:
            return False
        else:
            sql = "INSERT INTO `coco`.`room_apply` (`room_id`, `user_id`, `message`) VALUES (%s, %s, %s);"
            data = (info.room_id, info.user_id, info.message)
            self.execute_sql(sql, data)
            return True
        
    def room_leader(self, room_id):
        print("room_id", room_id)
        sql = "select leader from coco.room where id = %s;"
        result = self.select_sql(sql, room_id)
        return result[0]['leader']
    
    def room_apply(self, room_id):
        sql = """
            select a.*, u.name, u.exp, u.level
            from coco.room_apply as a, coco.user as u
            where a.user_id = u.id and a.room_id = %s;
        """
        result = self.select_sql(sql, room_id)
        leader = self.room_leader(room_id)
        return {
            'leader': leader,
            'apply': result
        }
    
    def reject_apply(self, info):
        del_sql = "DELETE FROM `coco`.`room_apply` WHERE (`room_id` = %s) and (`user_id` = %s);"
        del_data = (info.room_id, info.user_id)
        self.execute_sql(del_sql, del_data)
        return True


            

room = CrudRoom()