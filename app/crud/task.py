import shutil
import pymysql
import db
import json
import os
import zipfile
from .base import Crudbase

db_server = db.db_server

class CrudTask(Crudbase):
    #해당 id의 문제 정보 검색
    def select_task(self,id):
        sql="SELECT * FROM coco.task WHERE id=%s"
        data=id
        result = self.select_sql(sql,data)
        return result[0]
    
    def select_simplelist(self):
        sql="SELECT t.id,t.title,s.* FROM coco.task t left outer join coco.sub_per_task s on t.id=s.task_id;"
        result = self.select_sql(sql)
        return result

    def delete_task(self,id):
        sql="DELETE FROM coco.submissions where sub_id in (SELECT sub_id FROM coco.sub_ids where task_id=%s)"
        data=(id)
        self.execute_sql(sql,data)
        sql="DELETE FROM coco.task where id=%s"
        data=(id)
        self.execute_sql(sql,data)
        shutil.rmtree(f'/home/sjw/COCO_Back_End/tasks/{id}')
        return 1

    #coco.task insert
    def insert_task(self,task):  
        cLan = 1 if task.C_Lan == True else 0
        py = 1 if task.python == True else 0 
        desc=(task.description,task.inputDescription,task.outputDescription)
        sql=[]
        data=[]

        #time_limit, diff는 한자리 숫자
        sql.append("INSERT INTO `coco`.`task` ( `title`, `sample`, `rate`, `mem_limit`, `time_limit`, `diff`, `lan_c`, `lan_py`) VALUES ( %s,json_object('input', %s, 'output',%s), %s, %s, %s, %s, %s, %s);")
        data.append((task.title,f"[{task.inputEx1}, {task.inputEx2}]",f"[{task.outputEx1}, {task.outputEx2}]",0.00,task.memLimit,task.timeLimit,task.diff,cLan,py))
        sql.append("insert into coco.descriptions values (LAST_INSERT_ID(),%s,%s,%s);")
        data.append(desc)

        id=self.insert_last_id(sql,data)
        self.save_testcase(task.testCase,id)

    #test case zip파일 압축해서 저장
    def save_testcase(self,zip, task_id):
        zip_file_path = f'/home/sjw/COCO_Back_End/tasks/{task_id}'
        os.mkdir(zip_file_path)

        with open(f"{zip_file_path}/temp.zip", 'wb') as upload_zip:
                shutil.copyfileobj(zip.file, upload_zip)
        with zipfile.ZipFile(f"{zip_file_path}/temp.zip") as encrypt_zip:
                encrypt_zip.extractall(
                    zip_file_path,
                    None
                )
        os.remove(f"{zip_file_path}/temp.zip")

    #problem view에서 가져옴
    def read_problems(self):
        sql =  "SELECT * FROM view_task;"
        result = self.select_sql(sql)
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


task_crud=CrudTask()