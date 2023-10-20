import shutil
import json
import os
import zipfile
from .base import Crudbase
from app.core.image import image
from app.schemas.task import *
from app.models.task import *
from app.db.base import DBCursor


class CrudTask(Crudbase[Task,int]):
    def create_task(self,db_cursor:DBCursor,description:str,task:TaskBase):
        """ 
        새로운 문제를 생성
            
        - description: 문제 메인 설명
        - task : 문제의 요소들
            - title: 문제 제목
            - inputDescription: 입력 예제 설명
            - inputEx1: 입력 예제 1
            - inputEx2: 입략 예제 2
            - outputDescription: 출력 예제 설명
            - outputEx1: 출력 예제 1
            - outputEx2: 출력 예제 2
            - testCase: 테스트 케이스 zip파일
            - diff: 난이도
            - timeLimit: 시간제한
            - memLimit: 메모리제한
            - category: 문제 카테고리 ','로 구분된 문자열
        """
        input=[task.inputEx1,task.inputEx2]
        output=[task.outputEx1,task.outputEx2]
        sample={'input':input,'output':output}
        sample_str=json.dumps(sample)
        #time_limit, diff는 한자리 숫자 task 테이블에 문제 먼저 삽입해서 id추출
        sql="INSERT INTO `coco`.`task` ( `title`, `sample`,`mem_limit`, `time_limit`, `diff` ) VALUES ( %s, %s, %s, %s, %s );"
        data=(task.title, sample_str,task.memLimit,task.timeLimit,task.diff)
        task_id=db_cursor.insert_last_id(sql,data)

        #카테고리 연결
        for i in map(lambda a:a.strip(),task.category.split(",")):
            sql="INSERT INTO `coco`.`task_ids` (`task_id`, `category`) VALUES (%s, %s);"
            data=(task_id,i)
            db_cursor.execute_sql(sql,data)

        #desc에서 임시 이미지 삭제 및 실제 이미지 저장
        maindesc=image.save_update_image(os.path.join(os.getenv("TASK_PATH"),"temp"),os.path.join(os.getenv("TASK_PATH"),str(task_id)),description,task_id,"s")

        #desc 및 테스트케이스 저장
        sql="insert into coco.descriptions values (%s,%s,%s,%s);"
        data=(task_id,maindesc,task.inputDescription,task.outputDescription)
        db_cursor.execute_sql(sql,data)
        self.save_testcase(task.testCase,task_id)

        return 1

    def read_task_with_pagination(self, db_cursor:DBCursor,query:TaskListIn):
        """
        문제 리스트에서 쿼리에 맞는 문제들의 정보만 리턴
        keyword, diff, category는 AND 로 결합
        
        params
        - query : 문제 쿼리 정보
            - keyword: 검색할 id 혹은 title 정보
            - diff: 문제 난이도 | 1~5의 정수 값이 ','로 구분된 문자열 다중값 가능
            - category: 문제 카테고리 | ','로 구분된 문자열 다중값 가능
            - rateSort: 정답률 기준 정렬 | 0 - 기본 정렬 1 - 오름차순 2 - 내림차순 
            - size: 한페이지의 크기
            - page: 페이지 번호
        -----------------------------
        returns
        - [total,result]
            - total : 전체 문제 수
            - result : 조건에 맞는 문제 수
        """
        #기본 sql 뼈대.
        sql="SELECT * FROM coco.task_list"
        data=[]
        
        #where 조건 추가
        condition=[]
        #난이도 조건
        if query.diff:
            query.diff=map(int,query.diff.split(","))
            condition.append(" diff in("+",".join(map(str,query.diff))+")")
        #카테고리 조건
        if query.category:
            query.category=map(lambda a:a.strip(),query.category.split(","))
            condition.append(" id in (SELECT distinct task_id FROM coco.task_ids where category in ("+",".join(map(lambda a: '"'+a+'"',query.category))+"))")
        #키워드 조건
        if query.keyword:
            #숫자만 있다면 id로 검색
            if str.isnumeric(query.keyword):
                condition.append(" id = %s")
                data.append(int(query.keyword))
            #문자도 같이 있다면 like 검색
            else:
                condition.append(" title like %s")
                data.append("%"+query.keyword+"%")
        #각 문제별 제출수     
        sql+=" left outer join coco.sub_per_task s on id=s.task_id"

        #where 조건이 존재한다면 sql에 추가
        if len(condition):
            sql+=" WHERE"+" AND".join(condition)

        #정렬 기준 추가
        if query.rateSort==1:
            sql+=" ORDER BY rate"
        elif query.rateSort==2:
            sql+=" ORDER BY rate desc"

        total,result=db_cursor.select_sql_with_pagination(sql,tuple(data),query.size,query.page)

        return total,result

    def update_task(self,db_cursor:DBCursor,task_id:int,description:str,task:TaskBase):
        """ 
        문제 수정
            
        - task_id : 문제 id
        - description: 문제 메인 설명
        - task : 문제의 요소들
            - title: 문제 제목
            - inputDescription: 입력 예제 설명
            - inputEx1: 입력 예제 1
            - inputEx2: 입략 예제 2
            - outputDescription: 출력 예제 설명
            - outputEx1: 출력 예제 1
            - outputEx2: 출력 예제 2
            - testCase: 테스트 케이스 zip파일
            - diff: 난이도
            - timeLimit: 시간제한
            - memLimit: 메모리제한
            - category: 문제 카테고리 ','로 구분된 문자열
        - token : 사용자 인증
        """

        #task 테이블에서 정보 업데이트
        input=[task.inputEx1,task.inputEx2]
        output=[task.outputEx1,task.outputEx2]
        sample={'input':input,'output':output}
        sample_str=json.dumps(sample)
        sql="UPDATE `coco`.`task` SET `title` = %s , `sample` = %s ,`mem_limit` = %s, `time_limit` = %s, `diff` = %s WHERE (`id` = '%s')"
        data=(task.title, sample_str,task.memLimit,task.timeLimit,task.diff,task_id)
        db_cursor.execute_sql(sql,data)

        #카테고리 삭제
        sql="DELETE FROM `coco`.`task_ids` WHERE (`task_id` = %s)"
        data=(task_id)
        db_cursor.execute_sql(sql,data)

        #카테고리 연결
        for i in map(lambda a:a.strip(),task.category.split(",")):
            sql="INSERT INTO `coco`.`task_ids` (`task_id`, `category`) VALUES (%s, %s);"
            data=(task_id,i)
            db_cursor.execute_sql(sql,data)

        #desc에서 임시 이미지 삭제 및 실제 이미지 저장
        maindesc=image.save_update_image(os.path.join(os.getenv("TASK_PATH"),"temp"),os.path.join(os.getenv("TASK_PATH"),str(task_id)),description,task_id,"su")

        #desc 및 테스트케이스 업데이트
        sql="UPDATE `coco`.`descriptions` SET `main` = %s, `in` = %s, `out` = %s WHERE (`task_id` = %s);"
        data=(maindesc,task.inputDescription,task.outputDescription,task_id)
        db_cursor.execute_sql(sql,data)
        self.save_testcase(task.testCase,task_id)

        return 1

    def delete_task(self,db_cursor:DBCursor,task_id:int):
        """
        문제 삭제
        db에서 문제 데이터 삭제 및 로컬 스토리지에서 문제 데이터 삭제

        - task_id : 문제 id
        """
        sql="DELETE FROM coco.submissions where id in (SELECT sub_id FROM coco.sub_ids where task_id=%s)"
        data=(task_id)
        db_cursor.execute_sql(sql,data)
        sql="DELETE FROM coco.task where id=%s"
        data=(task_id)
        db_cursor.execute_sql(sql,data)
        image.delete_image(os.path.join(os.getenv("TASK_PATH"),str(task_id)))
        return 1
    
    def delete_category(self,db_cursor:DBCursor,category:str):
        """
        해당 카테고리를 가지는 문제가 존재하지 않는다면 삭제

        - category : 카테고리
        """
        sql="SELECT * FROM `coco`.`task_ids` WHERE (`category` = %s);"
        data=(category)
        result=db_cursor.select_sql(sql,data)

        if len(result)==0:
            sql="DELETE FROM `coco`.`task_category` WHERE (`category` = %s);"
            data=(category)
            db_cursor.execute_sql(sql,data)
            return 1
        else:
            return 0

    def save_testcase(self,zip:UploadFile, task_id:int):
        """
        테스트 케이스의 압축을 풀고 저장

        - zip :테스트 케이스 압축파일
        - task_id : 문제 id
        """

        zip_file_path = os.path.join(os.getenv("TASK_PATH"),str(task_id))
        #이전 테스트케이스가 있다면 제거
        zip_path=f"{zip_file_path}/testcase"+str(task_id)+".zip"
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(os.path.join(zip_file_path,"input")):
            shutil.rmtree(os.path.join(zip_file_path,"input"))
        if os.path.exists(os.path.join(zip_file_path,"output")):
            shutil.rmtree(os.path.join(zip_file_path,"output"))
        
        if not os.path.exists(zip_file_path):
            os.mkdir(zip_file_path)

        with open(zip_path, 'wb') as upload_zip:
            shutil.copyfileobj(zip.file, upload_zip)
        with zipfile.ZipFile(zip_path) as encrypt_zip:
            encrypt_zip.extractall(
                zip_file_path,
                None
            )
        
        # os.remove(f"{zip_file_path}/testcase"+str(task_id)+".zip")

    def task_detail(self,db_cursor:DBCursor,task_id:int):
        """
        원하는 문제의 상세한 정보 조회

        task_id: 문제 id
        """
        sql = "SELECT t.*,group_concat(c.category) as category FROM coco.task as t, task_ids as c WHERE t.id = %s and t.id=c.task_id group by c.task_id;"
        data=(task_id)
        result = db_cursor.select_sql(sql,data)
        if not len(result):
            return None
        sample = json.loads(result[0]["sample"])
        desc_sql = "SELECT * FROM coco.descriptions where task_id = %s;"
        data=(task_id)
        desc_result = db_cursor.select_sql(desc_sql,data)
        task = {
            'id': result[0]["id"],
            'title': result[0]["title"],
            'rate': result[0]["rate"],
            'memLimit': result[0]["mem_limit"],
            'timeLimit': result[0]["time_limit"],   
            'diff': result[0]["diff"],
            'category': list(result[0]["category"].split(',')),
            'inputEx1': sample['input'][0],
            'inputEx2': sample['input'][1],
            'outputEx1': sample['output'][0],
            'outputEx2': sample['output'][0],
            'mainDesc': desc_result[0]["main"],
            'inDesc': desc_result[0]["in"],
            'outDesc': desc_result[0]["out"],
            'is_ai': result[0]['is_ai']
        }
        return task
    
task_crud=CrudTask(Task)