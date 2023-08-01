import pymysql
import db
import uuid
from schemas.submission import StatusListIn, Submit
import time
from .base import Crudbase

db_server = db.db_server

class CrudSubmission(Crudbase):
    def create_sub(self,submit:Submit):
        """
        status 1("대기") 상태로 새로운 제출 생성
        생성된 제출의 id 리턴

        - submit
            - taskid
            - userid
            - sourcecode
            - callbackurl
            - lang : c언어 1 | 파이썬 0
        """
        a=uuid.uuid1()
        sql=[]
        data=[]
        sql.append("INSERT into coco.submissions (code,time,token,callback_url,status,lang ) values(%s, now(), %s, %s, %s,%s);")
        sql.append("insert into coco.sub_ids values (%s,%s,LAST_INSERT_ID());")
        data.append((
            submit.sourcecode,
            a.hex,
            submit.callbackurl,
            1,
            submit.lang))
        data.append((
            submit.userid,
            submit.taskid
        ))
        id=self.insert_last_id(sql,data)
        return id

    def read_sub(self,sub_id:int):
        """
        제출 정보 조회

        - sub_id
        """
        sql="SELECT * FROM coco.submissions WHERE sub_id=%s;"
        data=(sub_id)
        row=self.select_sql(sql,data)
        return row

    def update_status(self, sub_id:int, status:int):
        """
        status만 업데이트

        - sub_id
        - status : 채점 상태 1 - 대기, 2 - 채점중, 3 - 정답, 4 - 오답
        """
        sql="UPDATE coco.submissions SET status=%s WHERE sub_id=%s;"
        data=(status, sub_id)
        self.execute_sql(sql,data)

    def update_sub(self,sub_id:int,exit_code:int,status:int=4,stdout:str=None,stderr:str=None,message:str=None,number_of_runs:int=100,status_id:str=None):
        """
        제출 정보 업데이트

        - sub_id
        - exit_code : 런타임 채점시 종료 코드 0 - 정상종료, 1 - 런타임 오류
        - status : 채점 상태 1 - 대기, 2 - 채점중, 3 - 정답, 4 - 오답
        - stdout : 표준 출력값
        - stderr : 표준 에러값
        - message : 채점 결과
        - number_of_runs : 테스트케이스 통과 개수
        - status_id : isolate 런타임 결과 RE - 런타임 오류, TO - 시간 초과, SG - 메모리 초과
        """
        
        sql="UPDATE coco.submissions SET status_id=%s ,exit_code=%s, stdout=%s, stderr=%s, message=%s, number_of_runs=%s, status=%s WHERE sub_id=%s;"
        data=(
            status_id,
            exit_code,
            stdout,
            stderr,
            message,
            number_of_runs,
            status,
            sub_id)
        self.execute_sql(sql,data)
    
    def calc_rate(self,task_id:int):
        """
        문제의 정답률 수정을 위해 제출 회수 대비 맞은 제출 비율 조회

        - task_id
        """
        sql="SELECT status FROM coco.status_list where task_id=%s;"
        data=(task_id)
        all_sub=self.select_sql(sql,data)
        right_sub=0
        for i in all_sub:
            if i.get("status")==3:
                right_sub+=1
        return round(right_sub/len(all_sub)*100,1)
    
    def get_solved(self,user_id:str):
        """
        유저가 맞힌 문제 id 조회

        - user_id
        """
        sql="select group_concat(ids.task_id) as task_id from coco.submissions as sub, coco.sub_ids as ids where ids.user_id=%s and sub.status=3 and sub.sub_id=ids.sub_id"
        data=(user_id)
        
        result=self.select_sql(sql,data)[0]["task_id"]
        solved_task=[]
        if result:
            solved_task=list(set(result.split(",")))
        return solved_task
    
    def read_status(self, info : StatusListIn):
        """
        제출 조회

        - info
            - size: 한 페이지의 크기
            - page: 현재 페이지 번호
            - task_id: 문제 id 
            - lang: 제출 코드 언어 0 -> 파이썬 1-> c언어
            - user_id: 
            - answer: status가 3("정답") 인지 여부
        """
        sql ="select * from coco.status_list "
        data=[]

        condition=[]
        if info.user_id:
            condition.append(" user_id = %s ")
            data.append(info.user_id)
        if info.lang:
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

        total,result=self.select_sql_with_pagination(sql,tuple(data),info.size,info.page)
        
        if info.user_id:
            solved_list=self.get_solved(info.user_id)
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

submission_crud=CrudSubmission()