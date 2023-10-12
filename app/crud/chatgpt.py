import openai
from .base import Crudbase
from app.db.base import DBCursor
from bs4 import BeautifulSoup
import json
import os
import zipfile
import shutil
from app.crud.task import task_crud
class CrudChatGPT(Crudbase):
    def chatGPT(self, prompt):
        openai.api_key = os.getenv("CHATGPT_KEY")
        completion = openai.Completion.create(
        engine='text-davinci-003'  # 'text-curie-001'  # 'text-babbage-001' #'text-ada-001'
        , prompt=prompt
        , temperature=0.5
        , max_tokens=1024
        , top_p=1
        , frequency_penalty=0
        , presence_penalty=0)
        
        result = completion['choices'][0]['text']
        return result

    def get_answer(self, db_cursor:DBCursor, info):
        content = BeautifulSoup(info.content, "lxml").text
        # GPT에 보낼 질문
        prompt = '''
%s

%s

다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "code": <파이썬 리스트에 저장된 수정 코드>
    "content": "<문제 원인 설명>"
}
        ''' % (content, info.code)

        # openai.api_key = os.getenv("CHATGPT_KEY")
        # completion = openai.Completion.create(
        # engine='text-davinci-003'  # 'text-curie-001'  # 'text-babbage-001' #'text-ada-001'
        # , prompt=prompt
        # , temperature=0.5
        # , max_tokens=1024
        # , top_p=1
        # , frequency_penalty=0
        # , presence_penalty=0)
        
        # 답변 오면 JSON 형태로 저장
        result = self.chatGPT(prompt)
        result = json.loads(result, strict=False)
        ans_code =  result['code']
        ans_content = '<p>'+result['content']+'</p>'

        # 스터디룸 DB에 저장
        data = (info.room_id, info.q_id, ans_content, ans_code)
        sql = """
            INSERT INTO `room`.`%s_qa` (`q_id`, `answer`, `code`, `ans_writer`, `time`, `check`) 
            VALUES (%s, %s, %s, 'ai', now(), 0);
        """
        db_cursor.execute_sql(sql, data)

        return True

    def create_task(self, db_cursor:DBCursor, info):
        task_prompt = '''
%s


다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "problem": {
        "title": "<문제 제목>",
        "description": "<문제 설명>",
        "input": {
            "description": "<입력 설명>"
        },
        "output": {
            "description": "<출력 설명>"
        },
        "examples": [
            {
                "input": "<입력 예시>",
                "output": "<출력 예시>"
            },
            {
                "input": "<입력 예시>",
                "output": "<출력 예시>"
            }
        ]
    },
  "constraints": {
        "memory": "<메모리 제약 조건>",
        "time": "<시간 제약 조건>"
  }
}
        ''' % (info.content)
        task_result = self.chatGPT(task_prompt)

        # 최종 문제 생성 아니면 다시 리턴
        if info.is_final == False:
             return {'data': True, 'result': json.loads(task_result, strict=False)}
        else: #최종 문제 생성
            self.upload_task(json.loads(task_result, strict=False), db_cursor)

    def upload_task(self, task_info, db_cursor):
        testcase_prompt =  '''
다음과 같은 형식을 사용해서 위 문제에 대한 테스트 케이스를 20개 만들어주세요

{
    "testcase": [ 
        { 
            "input": "<입력>",
            "output": "<출력>"
        }
    ]
}

'''
        # testcase_result = self.chatGPT(testcase_prompt)

        testcase_result = '''
{
    "testcase": [
        {
            "input": "1",
            "output": "1"
        },
        {
            "input": "2",
            "output": "2"
        },
        {
            "input": "3",
            "output": "6"
        },
        {
            "input": "4",
            "output": "24"
        },
        {
            "input": "5",
            "output": "120"
        },
        {
            "input": "6",
            "output": "720"
        },
        {
            "input": "7",
            "output": "5040"
        },
        {
            "input": "8",
            "output": "40320"
        },
        {
            "input": "9",
            "output": "362880"
        },
        {
            "input": "10",
            "output": "3628800"
        },
        {
            "input": "11",
            "output": "39916800"
        },
        {
            "input": "12",
            "output": "479001600"
        },
        {
            "input": "13",
            "output": "6227020800"
        },
        {
            "input": "14",
            "output": "87178291200"
        },
        {
            "input": "15",
            "output": "1307674368000"
        },
        {
            "input": "16",
            "output": "20922789888000"
        },
        {
            "input": "17",
            "output": "355687428096000"
        },
        {
            "input": "18",
            "output": "6402373705728000"
        },
        {
            "input": "19",
            "output": "121645100408832000"
        },
        {
            "input": "20",
            "output": "2432902008176640000"
        }
    ]
}
'''
        testcase_result = json.loads(testcase_result, strict=False)
        testcase = testcase_result["testcase"]
       
        #문제 json 결과
        task_result = task_info
 
        # 문제 설명 파트
        problem = task_result["problem"]
        input_ex1 = str(problem['examples'][0]['input'])
        output_ex1 = str(problem['examples'][0]['output'])
        input_ex2 = str(problem['examples'][1]['input'])
        output_ex2 = str(problem['examples'][1]['output'])


        # 문제 제약 조건 파트
        constraints = task_result["constraints"]
        memory_limit = self.get_number(constraints["memory"])
        time_limit = self.get_number(constraints["time"])

        # #ai가 생성한 문제 db 저장
        task_sql="INSERT INTO `coco`.`task` ( `title`, `sample`,`mem_limit`, `time_limit`, `diff` ) VALUES ( %s, json_object('input', %s, 'output',%s), %s, %s, 1 );"
        task_data=(problem["title"], f"[{input_ex1}, {input_ex2}]",f"[{output_ex1}, {output_ex2}]",memory_limit,time_limit)
        task_id=db_cursor.insert_last_id(task_sql,task_data)
        print(task_id)

        #문제 desc 저장
        desc_sql="insert into coco.descriptions values (%s,%s,%s,%s);"
        main_desc = "<p>"+problem["description"]+"</p>"
        desc_data=(task_id,main_desc,problem["input"]["description"],problem["output"]["description"])
        db_cursor.execute_sql(desc_sql,desc_data)

        #테스트케이스 json 결과
        input_case, output_case = [], []
        for case in testcase:
            input_case.append(case['input'])
            output_case.append(case['output'])
        
        # TC 파일 경로
        testcase_file_path = os.path.join(os.getenv("TASK_PATH"), str(task_id))
        os.mkdir(testcase_file_path)

        # 입력 TC 파일
        input_file_path = os.path.join(testcase_file_path,'in')
        os.mkdir(input_file_path)
        for i in range(len(input_case)):
            file = open(input_file_path+"/"+str(i+1)+".txt",'w',encoding = 'utf-8') #텍스트파일 생성
            file.write(input_case[i])					#생성한 텍스트파일에 글자를 입력합니다.
            file.close()	

        # 출력 TC 파일
        output_file_path = os.path.join(testcase_file_path,'out')
        os.mkdir(output_file_path)
        for i in range(len(output_case)):
            file = open(output_file_path+"/"+str(i+1)+".txt",'w',encoding = 'utf-8') #텍스트파일 생성
            file.write(output_case[i])					#생성한 텍스트파일에 글자를 입력합니다.
            file.close()	

        # TC 파일 압축해서 저장
        zip_file = zipfile.ZipFile(os.getenv("TASK_PATH") + f"\\{str(task_id)}\\{str(task_id)}.zip", "w")
        for (path, dir, files) in os.walk(f"tasks\\{str(task_id)}\\"):
            for file in files:
                if file.endswith('.txt'):
                    zip_file.write(os.path.join(path, file), compress_type=zipfile.ZIP_DEFLATED)
        zip_file.close()
        
    # 문자열에서 숫자만 추출
    def get_number(self, string):
        result = ""
        for i in string:
            if i.isdigit():
                result+=i
        return result


crud_chatGPT = CrudChatGPT()




