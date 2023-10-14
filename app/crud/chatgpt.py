import openai
from .base import Crudbase
from app.db.base import DBCursor
from bs4 import BeautifulSoup
import json
import os
import zipfile
import shutil
from app.crud.task import task_crud
from app.core.image import image
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

    def ai_answer(self, db_cursor:DBCursor, info):
        '''
            스터디룸에 등록된 질문에 대한 AI 답변
        '''

        content = BeautifulSoup(info.content, "lxml").text
        if info.code == "": 
            prompt = '''
%s


다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "content": "<문제 원인 설명>"
}
        ''' % (content)
        # GPT에 보낼 질문
        else:
            prompt = '''
%s

%s

다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "code": <파이썬 리스트에 저장된 수정 코드>,
    "content": "<문제 원인 설명>"
}
        ''' % (content, info.code)

        
        # 답변 오면 JSON 형태로 저장
        result = self.chatGPT(prompt)
        for item in self.extract_json_objects(result):
            result = item
        result = json.loads(result, strict=False)

        # 해당 질문에 대한 ai 답변이 있는지 확인
        exist_sql = "select count(*) as exist FROM `plugin`.`qa` WHERE (`room_id` = %s and `q_id` = %s);"
        exist = db_cursor.select_sql(exist_sql, (info.room_id, info.q_id))
        exist = exist[0]['exist']

        if exist == 0: # ai 답변이 없으면
            if info.code != "": # 질문에 코드 포함
                ans_code =  result['code']
                ans_content = '<p>'+result['content']+'</p>'
                data = (info.room_id, info.q_id, ans_content, ans_code)
            else: # 코드 없이 질문만
                ans_content = '<p>'+result['content']+'</p>'
                data = (info.room_id, info.q_id, ans_content, info.code)
            
            # 플러그인 스키마 qa에 저장
            sql = """
                INSERT INTO `plugin`.`qa` (`room_id`, `q_id`, `answer`, `code`, `time`, `check`)
                VALUES (%s, %s, %s, %s, now(), 0);
            """
            db_cursor.execute_sql(sql, data)
        else: # ai에 답변이 있으면
            if info.code != "":
                ans_code =  result['code']
                ans_content = '<p>'+result['content']+'</p>'
                data = (ans_content, ans_code, info.room_id, info.q_id)
            else:
                ans_content = '<p>'+result['content']+'</p>'
                data = (ans_content, info.code, info.room_id, info.q_id)
                
            # 플러그인 스키마 qa의 기존 답변 업뎃
            sql = "UPDATE `plugin`.`qa` SET `answer` = %s, `code` = %s, `time` = now() WHERE (`room_id` = %s and `q_id` = %s);"
            db_cursor.execute_sql(sql, data)

        return True

    def create_task(self, db_cursor:DBCursor, info):
        '''
            AI가 생성한 문제 내용
        '''

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

        # 문제 내용 JSON 변환
        task_result = self.chatGPT(task_prompt)
        for item in self.extract_json_objects(task_result):
            task_result = item
        task_result = json.loads(task_result, strict=False)
        return {'data': True, 'result': task_result}

    def upload_task(self, db_cursor, task, description):
        '''
            AI가 생성한 문제 DB에 저장 및 TC 저장
        '''

        print(task)
        print(description)
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

# '''
        # 테스트 케이스 생성 후 JSON 변환
        testcase_result = self.chatGPT(testcase_prompt)
        for item in self.extract_json_objects(testcase_result):
            testcase_result = item
        testcase_result = json.loads(testcase_result, strict=False)
        testcase = testcase_result["testcase"]


        # 문제 내용 DB 저장
        sql="INSERT INTO `coco`.`task` ( `title`, `sample`,`mem_limit`, `time_limit`, `diff` ) VALUES ( %s, json_object('input', %s, 'output',%s), %s, %s, %s );"
        data=(task.title, f"[{task.inputEx1}, {task.inputEx2}]",f"[{task.outputEx1}, {task.outputEx2}]",task.memLimit,task.timeLimit,task.diff)
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

        #테스트케이스 json 결과
        input_case, output_case = [], []
        for case in testcase:
            input_case.append(case['input'])
            output_case.append(case['output'])
        
        # TC 파일 경로
        testcase_file_path = os.path.join(os.getenv("TASK_PATH"), str(task_id))

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

    def extract_json_objects(self, text):
        """
            문자열 속 json 추출
        """
        decoder = json.JSONDecoder()
        pos = 0
        while True:
            match = text.find('{', pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1
        
    def ai_code(self, db_cursor: DBCursor, info):
        '''
            유저가 제출한 코드에 대한 ai의 추천 코드
        '''
        

        

crud_chatGPT = CrudChatGPT()


#         task_result = '''
# {
#     "problem": {
#         "title": "숫자의 합 구하기",
#         "description": "1부터 N까지의 숫자의 합을 구하는 알고리즘 문제입니다.",
#         "input": {
#             "description": "정수 N",
#             "constraint": "1 <= N <= 10000"
#         },
#         "output": {
#             "description": "1부터 N까지의 숫자의 합"
#         },
#         "examples": [
#             {
#                 "input": "5",
#                 "output": "15"
#             },
#             {
#                 "input": "10",
#                 "output": "55"
#             }
#         ]
#     },
#   "constraints": {
#         "memory": "256mb",
#         "time": "2s"
#   }
# }
# '''


#         testcase_result = '''
# {
#     "testcase": [
#         {
#             "input": "1",
#             "output": "1"
#         },
#         {
#             "input": "2",
#             "output": "2"
#         },
#         {
#             "input": "3",
#             "output": "6"
#         },
#         {
#             "input": "4",
#             "output": "24"
#         },
#         {
#             "input": "5",
#             "output": "120"
#         },
#         {
#             "input": "6",
#             "output": "720"
#         },
#         {
#             "input": "7",
#             "output": "5040"
#         },
#         {
#             "input": "8",
#             "output": "40320"
#         },
#         {
#             "input": "9",
#             "output": "362880"
#         },
#         {
#             "input": "10",
#             "output": "3628800"
#         },
#         {
#             "input": "11",
#             "output": "39916800"
#         },
#         {
#             "input": "12",
#             "output": "479001600"
#         },
#         {
#             "input": "13",
#             "output": "6227020800"
#         },
#         {
#             "input": "14",
#             "output": "87178291200"
#         },
#         {
#             "input": "15",
#             "output": "1307674368000"
#         },
#         {
#             "input": "16",
#             "output": "20922789888000"
#         },
#         {
#             "input": "17",
#             "output": "355687428096000"
#         },
#         {
#             "input": "18",
#             "output": "6402373705728000"
#         },
#         {
#             "input": "19",
#             "output": "121645100408832000"
#         },
#         {
#             "input": "20",
#             "output": "2432902008176640000"
#         }
#     ]
# }
# '''