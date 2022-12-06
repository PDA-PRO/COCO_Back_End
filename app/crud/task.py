import shutil
import pymysql
import db
import json
import os
import zipfile

db_server = db.db_server

class CrudTask():
    def select_task(self,id):
        sql="SELECT * FROM coco.task WHERE id=%s"
        data=id
        result = self.execute_mysql_jong(sql,data)
        return result[0]
    
    def select_simplelist():
        sql="SELECT t.id,t.title,s.* FROM coco.task t left outer join coco.sub_per_task s on t.id=s.task_id;"
        result = CrudTask.execute_mysql(sql)
        print(result)
        return result

    def delete_task(id):
        sql=f"DELETE FROM coco.submissions where sub_id in (SELECT sub_id FROM coco.sub_ids where task_id={id})"
        CrudTask.insert_mysql(sql)
        sql=f"DELETE FROM coco.task where id={id}"
        CrudTask.insert_mysql(sql)
        shutil.rmtree(f'/home/sjw/COCO_Back_End/tasks/{id}')
        return 1

    #coco.task insert
    def insert_task(task):
        testCase = f'/home/sjw/COCO_Back_End/tasks'     
        imgs = [file.filename for file in task.desPic]
        cLan = 1 if task.C_Lan == True else 0
        py = 1 if task.python == True else 0 
        desc=[task.description,task.inputDescription,task.outputDescription]

        #time_limit, diff는 한자리 숫자
        sql= f"""INSERT INTO `coco`.`task` ( `title`, `sample`, `rate`, `test_case`, `mem_limit`, 
            `time_limit`, `img`, `diff`, `lan_c`, `lan_py`) 
            VALUES ( '{task.title}',  
            json_object("input", "{[task.inputEx1, task.inputEx2]}", "output", "{[task.outputEx1, task.outputEx2]}")
            , '{0.00}', '{testCase}', '{task.memLimit}', '{task.timeLimit}', json_object("desPic", "{imgs}"), 
            '{task.diff}', '{cLan}', '{py}');"""
        
        id=CrudTask.insert_last_mysql(sql,desc)
        CrudTask.save_testcase(task.testCase,id[0][0])

    #test case zip파일 압축해서 저장
    def save_testcase(zip, task_id):
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
    def read_problems():
        sql =  f"SELECT * FROM view_task;"
        result = CrudTask.execute_mysql(sql)
        problems = []
        for i in result:
            problem = {
                'id': i[0],
                'title': i[1],
                'diff': i[2],
                'rate': i[3]            
            }
            problems.append(problem)
        return problems
    

    #problem 페이지에서 문제 클릭 시 문제 id로 검색
    def search_task(id):
        sql = f"SELECT * FROM coco.task WHERE id = '{id}';"
        result = CrudTask.execute_mysql(sql)
        sample = CrudTask.sample_json(result[0][2])
        desc_sql = f"SELECT * FROM coco.descriptions where task_id = '{id}';"
        desc_result = CrudTask.execute_mysql(desc_sql)
        task = {
            'id': result[0][0],
            'title': result[0][1],
            'rate': result[0][3],
            'memLimit': result[0][5],
            'timeLimit': result[0][6],
            'img': result[0][7],     
            'diff': result[0][8],      
            'C_Lan': result[0][9],
            'python': result[0][10],
            'inputEx1': sample[0],
            'inputEx2': sample[1],
            'outputEx1': sample[2],
            'outputEx2': sample[3],
            'mainDesc': desc_result[0][1],
            'inDesc': desc_result[0][2],
            'outDesc': desc_result[0][3],
        }
        return task

    def pic_json(text):
        pics = json.loads(text)['desPic']
        pics = CrudTask.modify_string(pics)
        return pics

    #sample column을 json parsing
    def sample_json(text):
        sample = json.loads(text)
        input = sample['input']
        output = sample['output']
        input = CrudTask.modify_string(input)
        output = CrudTask.modify_string(output)
        return [input[0], input[1], output[0], output[1]]

    #json parsing해서 리스트에 저장위해 전처리
    def modify_string(text):
        text = text[1:-1]
        text = text.replace("'", "")
        text = text.split(",")
        result = []
        for i in text:
            if i[0] == " ":
                i = i[1:]
            result.append(i)
        return result

    def execute_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result
        
    def execute_mysql_jong(self,query,data):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password='twkZNoRsk}?F%n5n*t_4',port=3307,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        result = cur.fetchall()
        con.close()
        return result

    # 회원가입 정보 insert
    def insert_mysql_jong(self,query,data):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password='twkZNoRsk}?F%n5n*t_4',port=3307,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        con.commit()
        con.close()
        
    def insert_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()

    def insert_last_mysql(query,desc):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        cur.execute("select LAST_INSERT_ID();")
        id=cur.fetchall()
        cur.execute(f"insert into coco.descriptions values (LAST_INSERT_ID(),'{desc[0]}','{desc[1]}','{desc[2]}');")
        con.commit()
        con.close()
        return id

