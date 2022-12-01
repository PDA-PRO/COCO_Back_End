import pymysql
import db
import uuid
import json
    
db_server = db.db_server

class CrudTask():
    def select_task(self,id):
        sql="SELECT * FROM coco.task WHERE id=%s"
        data=id
        result=self.execute_mysql_jong(sql,data)
        print(result[0])
        return result[0]

    #coco.task insert
    def insert_task(task):
        cnt = CrudTask.get_count() #row개수+1 -> 새로운 문제 id
        testCase = f'testCase_{cnt+1}_{task.testCase.filename}' #task폴더에 id맞춰서 저장      
        imgs = [file.filename for file in task.desPic]
        cLan = 1 if task.C_Lan == True else 0
        py = 1 if task.python == True else 0 

        #time_limit, diff는 한자리 숫자
        sql= f"""INSERT INTO `coco`.`task` (`id`, `title`, `main_desc`, `sample`, `rate`, `test_case`, `mem_limit`, 
            `time_limit`, `img`, `diff`, `in_desc`, `out_desc`, `lan_c`, `lan_py`) 
            VALUES ('{cnt+1}', '{task.title}', '{task.description}', 
            json_object("input", "{[task.inputEx1, task.inputEx2]}", "output", "{[task.outputEx1, task.outputEx2]}")
            , '{0.00}', '{testCase}', '{task.memLimit}', '{task.timeLimit}', json_object("desPic", "{imgs}"), 
            '{task.diff}', '{task.inputDescription}', '{task.outputDescription}','{cLan}', '{py}');"""
        CrudTask.insert_mysql(sql)

    def get_count():
        sql = f'SELECT COUNT(`id`) FROM coco.task;'       
        return CrudTask.execute_mysql(sql)[0][0]

    #problem view에서 가져옴
    def read_problems():
        sql =  f"SELECT * FROM coco.task;"
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
        sample = CrudTask.sample_json(result[0][3])
        task = {
            'id': result[0][0],
            'title': result[0][1],
            'desc': result[0][2],
            'inputEx1': sample[0],
            'inputEx2': sample[1],
            'outputEx1': sample[2],
            'outputEx2': sample[3],
            'rate': result[0][4],
            'memLimit': result[0][6],
            'timeLimit': result[0][7],
            'desPic': CrudTask.pic_json(result[0][8]),
            'diff': result[0][9],
            'inputDescription': result[0][10],
            'outputDescription': result[0][11],
            'C_Lan': result[0][12],
            'python': result[0][13]
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

crud_task = CrudTask()
