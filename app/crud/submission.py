import uuid
from app.schemas.submission import StatusListIn, Submit
from .base import Crudbase
from app.models.submission import Submissions
from app.db.base import DBCursor

class CrudSubmission(Crudbase):   
    def create_sub(self,db_cursor:DBCursor,submit:Submit,user_id:str):
        """
        status 1("대기") 상태로 새로운 제출 생성
        생성된 제출의 id 리턴

        - submit
            - taskid
            - sourcecode
            - lang : 파이썬 0 | c 1 | c++ 2 | java 3
        - user_id
        """
        sql="INSERT into coco.submissions (code,time,status,lang ) values(%s, now(), %s,%s);"
        data=(submit.sourcecode,1,submit.lang)
        id=db_cursor.insert_last_id(sql,data)
        
        sql="insert into coco.sub_ids values (%s,%s,%s);"
        data=(user_id,submit.taskid,id)        
        db_cursor.execute_sql(sql,data)
        return id

    def read_sub(self,db_cursor:DBCursor,sub_id:int):
        """
        제출 정보 조회

        - sub_id
        """
        sql="SELECT submit.*,task.rate,task.diff FROM coco.task as task, coco.sub_ids as ids, coco.submissions as submit where submit.id= %s and submit.id=ids.sub_id and task.id=ids.task_id;"
        data=(sub_id)
        row=db_cursor.select_sql(sql,data)
        return row
    
    def get_solved(self, db_cursor:DBCursor,user_id:str):
        """
        유저가 맞힌 문제 id 조회

        - user_id
        """
        sql="select group_concat(ids.task_id) as task_id from coco.submissions as sub, coco.sub_ids as ids where ids.user_id=%s and sub.status=3 and sub.id=ids.sub_id"
        data=(user_id)
        
        result=db_cursor.select_sql(sql,data)[0]["task_id"]
        solved_task=[]
        if result:
            solved_task=list(map(int,set(result.split(","))))
        return solved_task
    
    def read_status(self,  db_cursor:DBCursor,info : StatusListIn):
        """
        제출 조회

        - info
            - size: 한 페이지의 크기
            - page: 현재 페이지 번호
            - task_id: 문제 id 
            - lang: 제출 코드 언어 0 -> 파이썬 1-> c언어
            - onlyme : 내 제출코드만 보기 여부
            - user_id: 
            - answer: status가 3("정답") 인지 여부
        """
        sql ="select * from coco.status_list "
        data=[]

        condition=[]
        if info.onlyme:
            condition.append(" user_id = %s ")
            data.append(info.user_id)
        if info.lang is not None:
            condition.append(" lang = %s ")
            data.append(info.lang)
        if info.answer:
            condition.append(" status = 3 ")
        if info.task_id:
            condition.append(" task_id = %s ")
            data.append(int(info.task_id))
                
        #where 조건이 존재한다면 sql에 추가
        if len(condition):
            sql+=" WHERE "+"AND".join(condition)
        sql+=" ORDER BY time desc"

        total,result=db_cursor.select_sql_with_pagination(sql,tuple(data),info.size,info.page)
        
        if info.user_id:
            solved_list=self.get_solved(db_cursor,info.user_id)
            for i in result:
                if i["task_id"] in solved_list:
                    i["is_solved"]=True
                else:
                    i["is_solved"]=False

        return {
            "total" : total,
            "size":info.size,
            "statuslist" : result
        }

    def read_mysub(self,  db_cursor:DBCursor,user_id):
        data = user_id
        total_submit, total_solved = 1, 1
        #월별 제출수
        submit_cnt_sql = """
            SELECT time, count(*) as cnt FROM coco.user_problem
            where user_id = %s
            GROUP BY time ORDER BY time DESC;     
        """
        submit_cnt_result = db_cursor.select_sql(submit_cnt_sql, data)
        submit_cnt = []
        for i in submit_cnt_result:
            total_submit += i['cnt']
            if not submit_cnt:
                submit_cnt.append([i['time'], i['cnt']])
            else:
                if i['time'] == submit_cnt[-1][0]:
                    submit_cnt[-1][1] += i['cnt']
                else:
                    submit_cnt.append([i['time'], i['cnt']])


            
        #월별 맞은 문제 수
        solved_cnt_sql = """
            SELECT time, count(*) as cnt FROM coco.user_problem
            WHERE user_id = %s AND status = '3'
            GROUP BY time ORDER BY time DESC;
        """
        solved_cnt_result = db_cursor.select_sql(solved_cnt_sql, data)
        solved_cnt = []
        for i in solved_cnt_result:
            total_solved += i['cnt']
            if not solved_cnt:
                solved_cnt.append([i['time'], i['cnt']])
            else:
                if i['time'] == solved_cnt[-1][0]:
                    solved_cnt[-1][1] += i['cnt']
                else:
                    solved_cnt.append([i['time'], i['cnt']])

        #전체 맞은 문제 리스트 + 성장 그래프
        solved_list_sql = """
            SELECT time, task_id, diff
            FROM coco.user_problem
            WHERE user_id = %s AND status = 3
            GROUP BY task_id, time ORDER BY time DESC;   
        """
        solved_list_result = db_cursor.select_sql(solved_list_sql, data)
        solved_list = [] #맞은 문제 리스트
        growth = [] #성장 그래프
        for i in range(len(solved_list_result)-1, -1, -1):
            solved_list.append(solved_list_result[i]['task_id']) # 맞은 문제 저장
            if not growth: #성장 그래프 리스트가 비어있으면
                growth.append([solved_list_result[i]['time'], solved_list_result[i]['diff']])
                #새로운 달에 저장
            else:
                if solved_list_result[i]['time'] == growth[-1][0]: #리스트 마지막 달과 같으면
                    growth[-1][1] += solved_list_result[i]['diff'] #해당 달에 누적
                else: #새로운 달에 그 전까지 누적값 저장
                    growth.append([solved_list_result[i]['time'], growth[-1][1]+solved_list_result[i]['diff']])

        solved_list = sorted(solved_list) #문제 아이디로 정렬

        #전체 푼 문제 리스트
        submit_list_sql = """
            SELECT task_id
            FROM coco.user_problem
            WHERE user_id = %s
            GROUP BY task_id, time ORDER BY time DESC;  
        """
        submit_list_result = db_cursor.select_sql(submit_list_sql, data)
        submit_list = []
        for i in range(len(submit_list_result)-1, -1, -1):
            submit_list.append(submit_list_result[i]['task_id'])
        submit_list = sorted(submit_list)
        unsolved_list = set(submit_list) - set(solved_list) 
               

        if len(submit_cnt) < 8:
            for i in range(len(submit_cnt), 18):
                submit_cnt.append(['0000', 0])

        if len(growth) < 8:
            for i in range(len(growth), 8):
                growth.append(['0000', 0])      

        # print('total: ', total_submit, total_solved)
        # print("월별 제출 수: ", submit_cnt)
        # print("월별 정답 수: ", solved_cnt)
        # print("전체 맞은 문제 리스트: ", solved_list)
        # print("성장 그래프: ", sorted(growth, reverse=True))          

        return {
            'month_submit': submit_cnt,
            'month_solved': solved_cnt,
            'solved_list': set(solved_list),
            'unsolved_list': unsolved_list,
            'growth': sorted(growth, reverse=True),
            'rate': round((total_solved/total_submit)*100, 1)
        }
    
    def read_my_sub(self, db_cursor:DBCursor, user_id:str):
        sql="select ids.task_id,sub.status from coco.submissions as sub, coco.sub_ids as ids where ids.user_id=%s and sub.id=ids.sub_id group by task_id,status"
        data=(user_id)
        db_cursor.select_sql(sql,data)
        return db_cursor.select_sql(sql,data)

submission_crud=CrudSubmission(Submissions)