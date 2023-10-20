import json
import os
from bs4 import BeautifulSoup
from fastapi import Depends
import openai
from app.api.deps import get_cursor
from app.core import security
from app.db.base import DBCursor
from app.plugin.interface import AbstractPlugin
from pydantic import BaseModel

class AskQ(BaseModel):
    content: str
    code: str|None
    room_id: int|None
    q_id: int|None


class Plugin(AbstractPlugin):
    router_path='/qa'
    feature_docs='스터디룸 Q&A에서 질문에 대한 답을 생성해주는 AI'
    base='ChatGPT 3.5-turbo'

    class TableModel(AbstractPlugin.AbstractTable):
        __key__='a_id'
        __tablename__='answer_geration'
        room_id: int
        a_id: int
        q_id: int

    @staticmethod
    def test():
        return 1
        
    @staticmethod
    def endpoint_main(info: AskQ,token: dict = Depends(security.check_token), db_cursor:DBCursor=Depends(get_cursor)):
        #커뮤니티에서 질문하기
        if info.room_id == None or info.q_id == None:
            if info.code == "": 
                prompt = '''
%s


반드시 다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "code": "<답변에 필요한 예시 코드>",
    "content": "<질문에 대한 답변>"
}
            ''' % (info.content)
            # GPT에 보낼 질문
            else:
                prompt = '''
%s

%s

반드시 다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "code": "<답변에 필요한 예시 코드>",
    "content": "<질문에 대한 답변>"
}
        ''' % (info.content, info.code)
            result = ask_ai(prompt)
            print('origin', result)
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
            print(result)

            result = json.loads(result, strict=False)


            return {'result': True, 'content': result['content'], 'code': result['code']}


        # 해당 질문에 대한 ai 답변이 있는지 확인
        exist_sql = "SELECT count(*) as cnt FROM room.%s_qa where q_id = %s and ans_writer is Null;"
        exist = db_cursor.select_sql(exist_sql, (info.room_id, info.q_id))
        exist = exist[0]['cnt']

        # 이미 답변이 있으면 함수 종료
        if exist != 0:
            return False


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
    "code": "<파이썬 리스트에 저장된 수정 코드>",
    "content": "<문제 원인 설명>"
}
        ''' % (content, info.code)

        
        # 답변 오면 JSON 형태로 저장
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
        result = json.loads(result, strict=False)
        

        if info.code != "": # 질문에 코드 포함
            ans_code =  result['code']
            ans_content = '<p>'+result['content']+'</p>'
            data = (info.room_id, info.q_id, ans_content, ans_code)
            
        else: # 코드 없이 질문만
            ans_content = '<p>'+result['content']+'</p>'
            data = (info.room_id, info.q_id, ans_content, info.code)
        
        # 해당 스터디룸 테이블에 데이터 insert
        sql = """
            INSERT INTO `room`.`%s_qa` (`q_id`, `answer`, `code`, `time`, `check`) 
            VALUES (%s, %s, %s, now(), 0);
        """
        ans_id = db_cursor.insert_last_id(sql, data)

        # 플러그인 테이블에 추가
        answer=Plugin.TableModel(room_id=info.room_id, a_id=ans_id, q_id=info.q_id)
        Plugin.create(db_cursor, answer)
        return True
    
    
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

# def extract_json_objects(text):
#     """
#         문자열 속 json 추출
#     """
#     decoder = json.JSONDecoder()
#     pos = 0
#     while True:
#         match = text.find('{', pos)
#         if match == -1:
#             break
#         try:
#             result, index = decoder.raw_decode(text[match:])
#             yield result
#             pos = match + index
#         except ValueError:
#             pos = match + 1
