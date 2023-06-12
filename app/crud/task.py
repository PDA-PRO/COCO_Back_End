import shutil
import db
import json
import os
import zipfile
from .base import Crudbase
from core.image import image

db_server = db.db_server

class CrudTask(Crudbase):
    #해당 id의 문제 정보 검색 -> 문제 상세 페이지 이동
    def select_task(self,id):
        sql="SELECT * FROM coco.task WHERE id=%s"
        data=id
        result = self.select_sql(sql,data)
        return result[0]
    
    def select_simplelist(self):
        sql="SELECT t.id,t.title,t.rate,t.diff,t.lan_c,t.lan_py,s.* FROM coco.task t left outer join coco.sub_per_task s on t.id=s.task_id;"
        result = self.select_sql(sql)
        return result

    def order_task(self, order):
        """
        문제 리스트에서 쿼리에 맞는 문제들의 정보만 리턴
        
        - order : 문제 쿼리 정보
        """

        #기본 sql 뼈대, order의 형식에 맞춰 sql이 지정되기 때문에 sql인젝션 걱정없습니다.
        sql="SELECT * FROM coco.task_list "

        #언어 구별 조건
        lang_cond=""
        if order['lang'][0] and order['lang'][1]:
            lang_cond="lan_c=1 or lan_py=1 "
        elif order['lang'][0] or order['lang'][1]:
            if order['lang'][1]:
                lang_cond="lan_c=1 "
            if order['lang'][0]:
                lang_cond="lan_py=1 "

        #난이도 구별 조건
        search_diff=[]
        for idx,value in enumerate(order["diff"],1):
            if value:
                search_diff.append(str(idx))

        #언어 조건, 난이도 조건 존재 유무에 따른 sql 변경
        if lang_cond:
            sql+="where "+lang_cond
        if search_diff:
            if lang_cond:
                sql+="having diff in ("+",".join(search_diff)+") "
            else:
                sql+="where diff in ("+",".join(search_diff)+") "

        #정렬 기준 추가
        if order["rate"]=="1":
            sql+="ORDER BY rate"
        elif order["rate"]=="2":
            sql+="ORDER BY rate desc"
        print(sql)
        return  self.select_sql(sql)

    def find_task(self, info):
        print(info)
        sql = "select * from coco.task_list where title like %s or id like %s"
        data = ('%'+info+'%', '%'+info+'%')
        result = self.select_sql(sql, data)
        return result

    def delete_task(self,id):
        sql="DELETE FROM coco.submissions where sub_id in (SELECT sub_id FROM coco.sub_ids where task_id=%s)"
        data=(id)
        self.execute_sql(sql,data)
        sql="DELETE FROM coco.task where id=%s"
        data=(id)
        self.execute_sql(sql,data)
        image.delete_image(os.path.join(os.getenv("TASK_PATH"),str(id)))
        return 1

    def insert_task(self,task,description):
        """
        새로운 문제를 저장

        - task : 문제의 다른 요소들
        - description : 텍스트 에디터의 raw format 즉 json형식의 str
        """
        cLan = 1 if task.C_Lan == True else 0
        py = 1 if task.python == True else 0 
        
        sql=[]
        data=[]
        
        #time_limit, diff는 한자리 숫자 task 테이블에 문제 먼저 삽입해서 id추출
        sql.append("INSERT INTO `coco`.`task` ( `title`, `sample`, `rate`, `mem_limit`, `time_limit`, `diff`, `lan_c`, `lan_py`) VALUES ( %s, json_object('input', %s, 'output',%s), %s, %s, %s, %s, %s, %s);")
        data.append((task.title, f"[{task.inputEx1}, {task.inputEx2}]",f"[{task.outputEx1}, {task.outputEx2}]",0.00,task.memLimit,task.timeLimit,task.diff,cLan,py))
        id=self.insert_last_id(sql,data)

        #이미지 저장
        maindesc=image.save_image(os.path.join(os.getenv("TASK_PATH"),"temp"),os.path.join(os.getenv("TASK_PATH"),str(id)),description,id)

        #desc 및 테스트케이스 저장
        temp=(id,maindesc,task.inputDescription,task.outputDescription)
        self.execute_sql("insert into coco.descriptions values (%s,%s,%s,%s);",temp)
        self.save_testcase(task.testCase,id)

        return 1

    def save_testcase(self,zip, task_id):
        """
        테스트 케이스의 압축을 풀고 저장

        - zip :테스트 케이스 압축파일
        - task_id : 문제 id
        """
        zip_file_path = os.path.join(os.getenv("TASK_PATH"),str(task_id))
        
        with open(f"{zip_file_path}/temp.zip", 'wb') as upload_zip:
                shutil.copyfileobj(zip.file, upload_zip)
        with zipfile.ZipFile(f"{zip_file_path}/temp.zip") as encrypt_zip:
                encrypt_zip.extractall(
                    zip_file_path,
                    None
                )
        os.remove(f"{zip_file_path}/temp.zip")

    def read_problems(self,keyword:str=None,sort:str="id"):
        '''
        problem view에서 문제 리스트를 가져옴 
        keyword가 존재할 시 해당 키워드를 포함하는 문제만 쿼리
        sort가 id, title, diff, rate 중 한개라면 그에 맞게 정렬 쿼리
        '''
        if sort not in ["id","title","diff","rate"]:
            sort="id"
        if keyword:
            sql =  "SELECT * FROM view_task where title like %s order by %s"
            data=('%'+keyword+'%',sort)
        else:
            sql =  "SELECT * FROM view_task order by %s;"
            data=(sort)
        result = self.select_sql(sql,data)
        return result
    

    #problem 페이지에서 문제 클릭 시 문제 id로 검색
    def search_task(self,id):
        sql = "SELECT * FROM coco.task WHERE id = %s;"
        data=(id)
        result = self.select_sql(sql,data)
        sample = self.sample_json(result[0]["sample"])
        desc_sql = "SELECT * FROM coco.descriptions where task_id = %s;"
        data=(id)
        desc_result = self.select_sql(desc_sql,data)
        task = {
            'id': result[0]["id"],
            'title': result[0]["title"],
            'rate': result[0]["rate"],
            'memLimit': result[0]["mem_limit"],
            'timeLimit': result[0]["time_limit"],   
            'diff': result[0]["diff"],      
            'C_Lan': result[0]["lan_c"],
            'python': result[0]["lan_py"],
            'inputEx1': sample[0],
            'inputEx2': sample[1],
            'outputEx1': sample[2],
            'outputEx2': sample[3],
            'mainDesc': desc_result[0]["main"],
            'inDesc': desc_result[0]["in"],
            'outDesc': desc_result[0]["out"],
        }
        return task

    #sample column을 json parsing
    def sample_json(self,text):
        sample = json.loads(text)
        input = sample['input']
        output = sample['output']
        input = self.modify_string(input)
        output = self.modify_string(output)
        return [input[0], input[1], output[0], output[1]]

    #json parsing해서 리스트에 저장위해 전처리
    def modify_string(self,text):
        text = text[1:-1]
        text = text.replace("'", "")
        text = text.split(",")
        result = []
        for i in text:
            if i[0] == " ":
                i = i[1:]
            result.append(i)
        return result

    def update_rate(self, task_id,rate):
        sql = "UPDATE task SET rate = %s WHERE (id = %s);"
        data=(rate,task_id)
        self.execute_sql(sql,data)

    def manage_tasklist(self):
        sql = """
            SELECT id, title, diff, rate, lan_c, lan_py, count(i.sub_id) as submits
            FROM coco.task as t, coco.sub_ids as i
            where t.id = i.task_id;
        """
        result = self.select_sql(sql)
        return result


task_crud=CrudTask()