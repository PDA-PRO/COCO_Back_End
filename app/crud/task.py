import pymysql
import db
import uuid

db_server = db.db_server

class CrudTask():
    def insert_task(task):
        cnt = CrudTask.get_count()
        testCase = f'testCase_{uuid.uuid1()}_{task.testCase.filename}'      
        imgs = CrudTask.create_imgPath(task.desPic.filename, task.inputFile.filename, task.outputFile.filename)
        
        #time_limit, diff는 한자리 숫자
        sql= f"""INSERT INTO `coco`.`task` (`id`, `title`, `description`, `sample`, `rate`, `test_case`, `memory_limit`, `time_limit`, `img`, `diff`) 
            VALUES ('{cnt+1}', '{task.title}', '{task.desc}', 
            json_object("input", "{[task.inputEx1, task.inputEx2]}", "output", "{[task.outputEx1, task.outputEx2]}")
            , '{0.00}', '{testCase}', '{task.mem}', '{task.time}', 
            json_object("desPic", "{imgs['desPic']}", "inputFile", "{imgs['inputFile']}", "outputFile", "{imgs['outputFile']}"),
             '{task.diff}');"""
    
        CrudTask.insert_mysql(sql)

    def get_count():
        sql = f'SELECT COUNT(`id`) FROM coco.task;'       
        return CrudTask.execute_mysql(sql)[0][0]

    def create_imgPath(desPic, inputFile, outputFile):
        desPic = f'desPic_{uuid.uuid1()}_{desPic}'
        inputFile = f'inputFile_{uuid.uuid1()}_{inputFile}'
        outputFile = f'outputFile_{uuid.uuid1()}_{outputFile}'
        return {
            'desPic': desPic,
            'inputFile': inputFile,
            'outputFile': outputFile
        }

    # def create_sampleJson(input1, input2, output1, output2):
    #     return {
    #         'input': [input1, input2],
    #         'output': [output1, output2]
    #     }

    def execute_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    def insert_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()

crud_task = CrudTask()