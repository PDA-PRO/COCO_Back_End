from .base import Crudbase
from schemas.room import *
from models.room import *
from db.base import DBCursor
from core.image import image
from schemas.common import PaginationIn
import os

class CrudRoom(Crudbase[Room,int]):
    def create_room(self, db_cursor:DBCursor,info:CreateRoom):
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
        last_idx = db_cursor.insert_last_id(room_sql, room_data)

        #study room에 포함된 멤버 추가
        member_sql = "INSERT INTO coco.room_ids (room_id, user_id) VALUES (%s, %s);"
        for member in info.members:
            member_data = (last_idx, member)
            db_cursor.execute_sql(member_sql, member_data)

        #관련 테이블 생성
        table_sql=[]
        table_data=[]
        table_sql.append("""
            CREATE TABLE `room`.`%s_roadmap` (
            `id` INT NOT NULL auto_increment,
            `name` VARCHAR(45) NULL,
            `desc` TEXT NULL,
            `last_modify` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (`id`));
        """)
        table_sql.append("""
            CREATE TABLE `room`.`%s_question` (
            `id` INT NOT NULL auto_increment,
            `title` TEXT NULL,
            `question` MEDIUMTEXT NULL,
            `code` MEDIUMTEXT NULL,             
            `writer` VARCHAR(45) NULL,
            PRIMARY KEY (`id`));
        """)
        table_sql.append("""
            CREATE TABLE `room`.`%s_qa` (
            `a_id` INT NOT NULL auto_increment,
            `q_id` INT NOT NULL,
            `answer` MEDIUMTEXT NULL,
            `code` MEDIUMTEXT NULL,
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
            db_cursor.execute_sql(sql,data)

        return last_idx
    
    def read_all_rooms(self,params:RoomBaseIn, db_cursor:DBCursor):
        """
        모든 study room 정보 리턴
        """
        sql=""
        data=[]
        if params.query:
            sql = '''
                select g.id, g.name, g.desc, g.leader, count(i.user_id) as members, sum(u.exp) as exp, row_number() over(order by sum(u.exp) desc) as ranking
                from coco.room as g, coco.room_ids as i, coco.user as u
                where g.id = i.room_id and i.user_id = u.id and g.name like %s group by g.id order by exp desc
            '''
            data.append(f'%{params.query}%')
        else:
            sql = '''
                select g.id, g.name, g.desc, g.leader, count(i.user_id) as members, sum(u.exp) as exp, row_number() over(order by sum(u.exp) desc) as ranking
                from coco.room as g, coco.room_ids as i, coco.user as u
                where g.id = i.room_id and i.user_id = u.id group by g.id order by exp desc
            '''

        total,result=db_cursor.select_sql_with_pagination(sql,data,params.size,params.page)
        return {"total":total,"room_list":result,"size":params.size}
    
    def delete_room(self, db_cursor:DBCursor,room_id:int):
        """
        study room삭제에 관련된 데이터, 테이블 삭제
        
        - room_id : 삭제할 room의 id값
        """
        #room 테이블에서 id값의 정보 삭제
        sql = "DELETE FROM `coco`.`room` WHERE (`id` = %s);"
        data = (room_id)
        db_cursor.execute_sql(sql,data)

        #관련 테이블 삭제
        sql = "DROP TABLE `room`.`%s_qa`, `room`.`%s_question`, `room`.`%s_roadmap`, `room`.`%s_roadmap_ids`"
        data = (room_id,room_id,room_id,room_id)
        db_cursor.execute_sql(sql, data)

        return True
    
    def insert_members(self, db_cursor:DBCursor,members:RoomMember):
        """
        해당 id의 study room에 member를 추가
        
        - members : 추가할 room의 id
            - room_id : room id
            - user_id : user id
        """
        #study room에 포함된 멤버 추가
        member_sql = "INSERT INTO coco.room_ids (room_id, user_id) VALUES (%s, %s);"
        for member in members.user_id:
            member_data = (members.room_id, member)
            db_cursor.execute_sql(member_sql, member_data)
        return True

    def delete_members(self, db_cursor:DBCursor,members:RoomMember):
        '''
        해당 id의 study room에 member를 삭제

        - members : 삭제할 room의 id
            - room_id : room id
            - user_id : user id
        '''
        member_sql = "DELETE FROM `coco`.`room_ids` WHERE (`room_id` = %s) and (`user_id` = %s);"
        for member in members.user_id:
            member_data = (members.room_id, member)
            db_cursor.execute_sql(member_sql, member_data)

        return True
    
    def myroom(self,db_cursor:DBCursor, user_id):
        '''
        해당 user가 속한 study room의 정보를 리턴            
        '''
        data = (user_id)
        sql = """
            select g.id, g.name, g.leader, count(i.user_id) as members, sum(u.exp) as exp, row_number() over(order by sum(u.exp) desc) as ranking
            from coco.room as g, coco.room_ids as i, coco.user as u
            where g.id = i.room_id and u.id = i.user_id and g.id in (
                select room_id from coco.room_ids where user_id = %s
            )
            group by g.id order by exp desc;
        """
        return db_cursor.select_sql(sql, data)
    
    def write_question(self,db_cursor:DBCursor, info):
        '''
        Study room의 질문 생성
        
        - info: question 생성에 필요한 입력 데이터
            - room_id: question이 등록될 study room의 id
            - question: user가 작성한 질문
            - code: user가 작성한 코드
            - writer: 질문 작성 user
        '''
        data = (info.room_id, info.title, info.question, info.code, info.writer)
        sql = """
            INSERT INTO `room`.`%s_question` (`title`, `question`, `code`, `writer`) 
            VALUES (%s, %s, %s, %s);
        """
        db_cursor.execute_sql(sql, data)
        return True
    
    def room_questions(self, db_cursor:DBCursor,room_id,pagination:PaginationIn):
        '''
        해당 study room에 등록된 모든 질문 리스트 리턴
        '''
        data = (room_id)
        sql = 'SELECT * FROM room.%s_question'
        total,q_result = db_cursor.select_sql_with_pagination(sql, [data],pagination.size,pagination.page)
        qa = []
        for q in q_result:
            ans_sql = """
                select q.id, a.answer, a.code, a.ans_writer from room.%s_qa as a, room.%s_question as q
                where a.q_id = q.id and q.id = %s;
            """
            ans_data = (room_id,room_id, q['id'])
            ans_result = db_cursor.select_sql(ans_sql, ans_data)
            qa.append({
                **q,
                'answers':ans_result,
            })
        return {"question_list":qa,"total":total,'size':pagination.size}
    
    def write_answer(self,db_cursor:DBCursor, info):
        data = (info.room_id, info.q_id, info.answer, info.code, info.ans_writer)
        sql = """
            INSERT INTO `room`.`%s_qa` (`q_id`, `answer`, `code`, `ans_writer`) 
            VALUES (%s, %s, %s, %s);
        """
        db_cursor.execute_sql(sql, data)
        return True

    def create_roadmap(self,db_cursor:DBCursor, info:RoomRoadMap, user_id:str):
        '''
        Study room의 roadmap 생성
        
        - info: roadmap 생성에 필요한 입력 데이터
            - room_id: room id
            - name: roadmap 제목
            - desc: roadmap 메인 설명
            - task_id: 관련 문제 목록
        '''
        data = (info.id, info.name, info.desc)
        sql = """
            INSERT INTO `room`.`%s_roadmap` ( `name`, `desc`) 
            VALUES (%s, %s);
        """
        last_idx=db_cursor.insert_last_id(sql, data)
        new_desc=image.save_update_image(os.path.join(os.getenv("ROADMAP_PATH"),"temp",user_id),os.path.join(os.getenv("ROADMAP_PATH"),f"{str(info.id)}_{str(last_idx)}"),info.desc,f"{str(info.id)}_{str(last_idx)}","s")
        self.update(db_cursor,{"`desc`":new_desc},"`room`",f"`{str(info.id)}_roadmap`",id=last_idx)
        for i in info.tasks:
            data = (info.id,last_idx, i)
            sql = """
                INSERT INTO `room`.`%s_roadmap_ids` ( `roadmap_id`, `task_id`) 
                VALUES (%s, %s);
            """
            db_cursor.execute_sql(sql,data)
        return True
    
    def read_roadmap(self, db_cursor:DBCursor,room_id):
        '''
        Study room의 모든 roadmap 조회 
        
        - room_id: room id
        '''
        
        sql = """
            select r.*,group_concat(rids.task_id) as tasks from room.%s_roadmap as r, room.%s_roadmap_ids as rids
                where r.id = rids.roadmap_id group by rids.roadmap_id;
        """
        data = (room_id,room_id)
        result=db_cursor.select_sql(sql,data)
        for i in result:
            i["tasks"]=list(map(int,i["tasks"].split(",")))
        return result

    def delete_roadmap(self,db_cursor:DBCursor,room_id:int,roadmap_id:int):
        '''
        해당 id의 study room에서 roadmap을 삭제

        - room_id : room id
        - roadmap_id : roadmap id
        '''
        sql = "DELETE FROM `room`.`%s_roadmap_ids` WHERE (`roadmap_id` = %s);"
        data = (room_id, roadmap_id)
        db_cursor.execute_sql(sql, data)
        sql = "DELETE FROM `room`.`%s_roadmap` WHERE (`id` = %s);"
        data = (room_id, roadmap_id)
        db_cursor.execute_sql(sql, data)
         
        return True

    def get_room(self,db_cursor:DBCursor, info):
        sql = """
            select g.id, g.name, g.desc, g.leader, gu.user_id, u.exp
            from coco.room as g, coco.room_ids as gu, coco.user as u
            where gu.room_id = g.id and gu.room_id = %s and gu.user_id = u.id;
        """
        data = (info)
        result = db_cursor.select_sql(sql, data)
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
    
    def get_roadmap(self, db_cursor:DBCursor,room_id, roadmap_id):
        '''
            해당 id의 study room의 특정 roadmap 정보를 가져옴

            - room_id: room id
            - roadmap_id: roadmap id
        '''
        # 스룸 로드맵 정보
        roadmap_sql = "SELECT r.*, c.leader FROM room.%s_roadmap as r, coco.room as c where c.id = %s and r.id = %s;"
        roadmap_data = (room_id, room_id, roadmap_id)
        roadmap_result = db_cursor.select_sql(roadmap_sql, roadmap_data)

        # 로드맵에 속한 문제 리스트
        problem_sql = '''
            select * from coco.task_list where id in ( SELECT i.task_id 
            FROM room.%s_roadmap as r, room.%s_roadmap_ids as i where r.id = %s and r.id = i.roadmap_id);
        '''
        problem_data = (room_id, room_id, roadmap_id)
        problem_result = db_cursor.select_sql(problem_sql, problem_data)
        
        # 문제 번호만 추출
        problems = []
        for result in problem_result:
            problems.append(result['id'])

        # 스룸 멤버 아이디만 추출
        users = []
        user_sql = "SELECT i.user_id FROM coco.room as r, coco.room_ids as i where r.id = %s and r.id = i.room_id;"
        user_data = (room_id)
        user_result = db_cursor.select_sql(user_sql, user_data)
        for result in user_result:
            users.append(result['user_id'])

        # 스룸 멤버가 로드맵 문제 풀었는지 안풀었는지
        solved_result = {}
        for user in users:
            solved = []
            for problem in problems:
                sql = "SELECT user_id, task_id, status FROM coco.user_problem WHERE user_id = %s AND task_id = %s and status = 3;"
                data = (user, problem)
                result = db_cursor.select_sql(sql, data)
                if not result:
                    continue
                else:
                    solved.append(problem)
            solved_result[user] = solved

        return{
            'roadmap': roadmap_result[0],
            'problem_list': problem_result,
            'solved_list': solved_result
        }

        




            

room = CrudRoom(Room)