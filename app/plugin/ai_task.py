from ast import literal_eval
import json
import os
import zipfile
from bs4 import BeautifulSoup
from fastapi import Depends, Form
import openai
from app.api.deps import get_cursor
from app.core.image import image
from app.db.base import DBCursor
from app.plugin.interface import AbstractPlugin
from app.schemas.ai import CreateTask

class Plugin(AbstractPlugin):
    router_path='/ai-task'

    class TableModel(AbstractPlugin.AbstractTable):
        __key__='id'
        __tablename__='task'
        id: int

    @staticmethod
    def test():
        return 1
        
    @staticmethod
    def main(info: CreateTask, db_cursor:DBCursor=Depends(get_cursor)):
        if info.is_final == False:
            prompt = '''
%s


반드시 다음과 같은 형식을 사용해서 알려주세요:

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
                "input": "<공백으로 구분된 입력 예시>",
                "output": "<출력 예시>"
            },
            {
                "input": "<공백으로 구분된 입력 예시>",
                "output": "<출력 예시>"
            }
        ]
    },
    "constraints": {
        "memory": "<메모리 제약 조건>",
        "time": '<시간 제약 조건>'
    },
    "code" : {
        "code": "<줄바꿈으로 구분되는 파이썬 정답 코드>"
    }
}
        ''' % (info.content)

            # 문제 내용 JSON 변환
            result = ask_ai(prompt)



            start, end = 0, len(result)-1
            for i in range(len(result)):
                if result[i] == '{':
                    start = i
                    break
            for i in range(len(result)-1, -1, -1):
                if result[i] == '}':
                    end = i
                    break
                    
            result = result[start:end+1]
            print('origin', result)
            result = json.loads(result, strict=False)
            print('result', result)
            
            
            return {'data': True, 'result': result}
        else:   
            print(info)
            
            # 문제 메인 설명
            description = BeautifulSoup(info.form_data, "lxml").text
            prompt = '''
%s
        
위 문제에 대한 테스트 케이스를 다음과 같은 형식을 사용해서 20개 만들어주세요
{
    "testcase": [ 
        { 
            "input": "<공백으로 구분된 입력 예시>",
            "output": "<입력에 대한 출력>"
        }
    ]
}

''' % (description)
            result = ask_ai(prompt)
            
            # TC 생성 후 JSON 변환
            # for item in extract_json_objects(result):
            #     result = item
            
            # if str(type(result)) == "<class 'str'>":
            #     result = json.loads(result, strict=False)

            start, end = 0, len(result)-1
            for i in range(len(result)):
                if result[i] == '{':
                    start = i
                    break
            for i in range(len(result)-1, -1, -1):
                if result[i] == '}':
                    end = i
                    break

            result = result[start:end+1]
            result = json.loads(result, strict=False)
            testcase = result['testcase']   # TC
            task = info.task_data # 문제 정보

            print(testcase, task)

            # #time_limit, diff는 한자리 숫자 task 테이블에 문제 먼저 삽입해서 id추출
            sql="INSERT INTO `coco`.`task` ( `title`, `sample`,`mem_limit`, `time_limit`, `diff`, `is_ai` ) VALUES ( %s, json_object('input', %s, 'output',%s), %s, %s, %s, 1 );"
            data=(task['title'], f"[{task['inputEx1']}, {task['inputEx2']}]",f"[{task['outputEx1']}, {task['outputEx2']}]",task['memLimit'],task['timeLimit'],task['diff'])
            task_id=db_cursor.insert_last_id(sql,data)

            for i in map(lambda a:a.strip(),task['category'].split(",")):
                sql="INSERT INTO `coco`.`task_ids` (`task_id`, `category`) VALUES (%s, %s);"
                data=(task_id,i)
                db_cursor.execute_sql(sql,data)
            
            #desc에서 임시 이미지 삭제 및 실제 이미지 저장
            maindesc=image.save_update_image(os.path.join(os.getenv("TASK_PATH"),"temp"),os.path.join(os.getenv("TASK_PATH"),str(task_id)),description,task_id,"s")

                    
            #desc 저장
            sql="insert into coco.descriptions values (%s,%s,%s,%s);"
            data=(task_id,maindesc,task['inputDescription'],task['outputDescription'])
            db_cursor.execute_sql(sql,data)

            # 플러그인 task에 생성된 문제 아이디 저장
            task_result = Plugin.TableModel(id=task_id)
            Plugin.create(db_cursor, task_result)


            #테스트케이스 json 결과
            input_case, output_case = [], []
            for case in testcase:
                input_case.append(case['input'])
                output_case.append(case['output'])


            # TC 파일 경로 - AI가 생성한 문제는 ai_{task_id}
            testcase_file_path = os.path.join(os.getenv("TASK_PATH"), str(task_id))
            # os.makedirs(testcase_file_path)

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
 
    
    
def ask_ai(prompt):
    openai.api_key = os.getenv("CHATGPT_KEY")
    completion = openai.Completion.create(
    engine='text-davinci-003'  # 'text-curie-001'  # 'text-babbage-001' #'text-ada-001'
    , prompt=prompt
    , temperature=0.5
    , max_tokens=1024
    , top_p=1
    , frequency_penalty=0
    , presence_penalty=0)
    return completion['choices'][0]['text']

def extract_json_objects(text):
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

# result = '''
#     {
#         "testcase": [
#             {
#                 "input": "1",
#                 "output": "1"
#             },
#             {
#                 "input": "2",
#                 "output": "2"
#             },
#             {
#                 "input": "3",
#                 "output": "6"
#             },
#             {
#                 "input": "4",
#                 "output": "24"
#             },
#             {
#                 "input": "5",
#                 "output": "120"
#             },
#             {
#                 "input": "6",
#                 "output": "720"
#             },
#             {
#                 "input": "7",
#                 "output": "5040"
#             },
#             {
#                 "input": "8",
#                 "output": "40320"
#             },
#             {
#                 "input": "9",
#                 "output": "362880"
#             },
#             {
#                 "input": "10",
#                 "output": "3628800"
#             },
#             {
#                 "input": "11",
#                 "output": "39916800"
#             },
#             {
#                 "input": "12",
#                 "output": "479001600"
#             },
#             {
#                 "input": "13",
#                 "output": "6227020800"
#             },
#             {
#                 "input": "14",
#                 "output": "87178291200"
#             },
#             {
#                 "input": "15",
#                 "output": "1307674368000"
#             },
#             {
#                 "input": "16",
#                 "output": "20922789888000"
#             },
#             {
#                 "input": "17",
#                 "output": "355687428096000"
#             },
#             {
#                 "input": "18",
#                 "output": "6402373705728000"
#             },
#             {
#                 "input": "19",
#                 "output": "121645100408832000"
#             },
#             {
#                 "input": "20",
#                 "output": "2432902008176640000"
#             }
#         ]
#     }
#     '''
