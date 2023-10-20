from ast import literal_eval
import datetime
import json
import os
from bs4 import BeautifulSoup
from fastapi import Depends
import openai
import requests
from app.api.deps import get_cursor
from app.core import security
from app.db.base import DBCursor
from app.plugin.interface import AbstractPlugin
from app.schemas.ai import *

class Plugin(AbstractPlugin):
    router_path='/ai-code'

    class TableModel(AbstractPlugin.AbstractTable):
        __key__='sub_id'
        __tablename__='ai_code'
        task_id: int
        sub_id: int
        code: str
        desc: str
        check: int

    @staticmethod
    def test():
        return 1
        
    @staticmethod
    def main(info: AiCode, token: dict = Depends(security.check_token), db_cursor:DBCursor=Depends(get_cursor)):
        print(info)
        
         # 해당 코드에 대한 ai 코드가 있는지 확인
        exist_sql = "select count(*) as exist FROM `plugin`.`ai_code` WHERE (`task_id` = %s and `sub_id` = %s);"
        exist = db_cursor.select_sql(exist_sql, (info.task_id, info.sub_id))
        exist = exist[0]['exist']

        if exist == 1: #ai 개선 코드가 있다면
            sql = "SELECT * FROM plugin.ai_code where task_id = %s and sub_id = %s;"
            data = (info.task_id, info.sub_id)
            result = db_cursor.select_sql(sql, data)
            return {
                'data': True,
                'code': result[0]['code'],
                'desc': result[0]['desc']
            }

        efficient_prompt = '''
%s

위 코드를 수정해서 시간, 메모리 측면에서 효율적이고 개선된 코드를 생성해줘

만약 코드 수정이 필요 없을 때 다음과 같은 형식을 사용해서 출력해줘:
{ 
    "code": "False",
    "desc": "",
}

코드 수정이 필요하다면 다음과 같은 형식을 사용해서 위 코드를 수정해줘
코드의 각 라인은 줄바꿈을 정확히 지키고 주석을 추가해줘:
{
    "code": "<주석이 추가된 수정된 코드>",
    "desc": "<수정된 코드에 대한 두 줄 이상의 자세한 설명>"
}

           
        ''' % (info.code)



        #  ai 답변 결과를 dict 형태로 변경
        efficient_result = ask_ai(efficient_prompt)
        start_idx = 0
        for i in range(len(efficient_result)):
            if efficient_result[i] == '{':
                start_idx = i
                break
        efficient_result = efficient_result[start_idx: ]
        
        print(efficient_result)
        efficient_result = literal_eval(efficient_result)

        code = efficient_result['code']
        desc = efficient_result['desc']
        print(code, desc)

        sql = "INSERT INTO `plugin`.`ai_code` (`task_id`, `sub_id`, `code`, `desc`) VALUES (%s, %s, %s, %s);"
        data = (info.task_id, info.sub_id, code, desc)
        db_cursor.execute_sql(sql, data)
        return {
            'data': True,
            'code': code,
            'desc': desc
        }
    
    
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

