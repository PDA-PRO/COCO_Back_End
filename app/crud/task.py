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
        print(order)
        if sum(order['diff']) == 0:
            for i in range(5):
                order['diff'][i] = i+1
        if sum(order['lang']) == 0:
            order['lang'][0], order['lang'][1] = 1, 1
        print(order['diff'], order['lang'], order['rate'] )

        if order['rate'] == '1':
            #정답률 낮은 순 
            sql = """
                SELECT * FROM coco.task_list WHERE id in (select id from coco.task_list
                where lan_c = %s and lan_py = %s)
                having diff = %s OR diff = %s OR diff = %s OR diff = %s OR diff = %s
                ORDER BY rate;
            """
            data = (order['lang'][1], order['lang'][0], order['diff'][0], order['diff'][1], order['diff'][2], order['diff'][3], order['diff'][4])
            return self.select_sql(sql, data)
        elif order['rate'] == '2':
            # 정답률 높은 순
            sql = """
                SELECT * FROM coco.task_list WHERE id in (select id from coco.task_list
                where lan_c = %s and lan_py = %s)
                having diff = %s OR diff = %s OR diff = %s OR diff = %s OR diff = %s
                ORDER BY rate DESC;
            """
            data = (order['lang'][1], order['lang'][0], order['diff'][0], order['diff'][1], order['diff'][2], order['diff'][3], order['diff'][4])
            return self.select_sql(sql, data)
        else:
            sql = """
                SELECT * FROM coco.task_list;
            """
            return self.select_sql(sql)

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
        shutil.rmtree(f'/home/sjw/COCO_Back_End/tasks/{id}')
        return 1

    #coco.task insert
    def insert_task(self,task,description):  
        cLan = 1 if task.C_Lan == True else 0
        py = 1 if task.python == True else 0 
        
        sql=[]
        data=[]
        
        #time_limit, diff는 한자리 숫자 task 테이블에 문제 먼저 삽입해서 id추출
        sql.append("INSERT INTO `coco`.`task` ( `title`, `sample`, `rate`, `mem_limit`, `time_limit`, `diff`, `lan_c`, `lan_py`) VALUES ( %s,json_object('input', %s, 'output',%s), %s, %s, %s, %s, %s, %s);")
        data.append((task.title,f"[{task.inputEx1}, {task.inputEx2}]",f"[{task.outputEx1}, {task.outputEx2}]",0.00,task.memLimit,task.timeLimit,task.diff,cLan,py))
        id=self.insert_last_id(sql,data)

        #저장된 main desc에서 쓰인 사진만 추출 및 텍스트 에디터의 사진 경로를 실제 사진 경로로 수정
        jsonObject = json.loads(description)
        imagelist=[]
        for entity in jsonObject.get("entityMap").values():
            imagename=entity.get("data").get("src").split('/')[-2]
            imagelist.append(imagename)
            entity["data"]["src"]=entity["data"]["src"][:-5]+"?id="+str(id)
        maindesc=json.dumps(jsonObject)

        #desc 저장
        temp=(id,maindesc,task.inputDescription,task.outputDescription)
        self.execute_sql("insert into coco.descriptions values (%s,%s,%s,%s);",temp)
        self.save_testcase(task.testCase,id)
        
        #temp폴더에서 실제로 저장되지 않은 사진 삭제 및 실제로 쓰인 사진를 문제 id에 맞는 경로로 이동
        tempimagelist=os.listdir(os.path.join(os.getenv("TASK_PATH"),"temp")) #jwt가 같이 들어오면 이걸 user id로 변경
        for i in tempimagelist:
            if i.split(".")[-1]!="keep" and not i in imagelist:
                os.remove(os.path.join(os.getenv("TASK_PATH"),"temp",i))
            else:
                shutil.move(os.path.join(os.getenv("TASK_PATH"),"temp",i),os.path.join(os.getenv("TASK_PATH"),str(id),i))


    #test case zip파일 압축해서 저장ㄴ
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

    #
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
        filepath=os.path.join(os.getenv("TASK_PATH"),str(id))
        taskinfo=os.listdir(filepath)
        img=[]
        for i in taskinfo:
            if i.split(".")[-1] in ['jpg','JPG','jpeg']:
                img.append(i)
        img.sort()
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
            "img":img
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