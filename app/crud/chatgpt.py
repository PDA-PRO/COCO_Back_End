import openai
from .base import Crudbase
from app.db.base import DBCursor
from bs4 import BeautifulSoup
import json


class CrudChatGPT(Crudbase):
    def ask_gpt(self, db_cursor:DBCursor, info):
        content = BeautifulSoup(info.content, "lxml").text
        prompt = '''
%s

%s

다음과 같은 JSON 형식을 사용해서 알려주세요:
{
    "code": <파이썬 리스트에 저장된 수정 코드>
    "content": "<문제 원인 설명>"
}
        ''' % (content, info.code)


        YOUR_API_KEY = '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'
        openai.api_key = YOUR_API_KEY
        completion = openai.Completion.create(
        engine='text-davinci-003'  # 'text-curie-001'  # 'text-babbage-001' #'text-ada-001'
        , prompt=prompt
        , temperature=0.5
        , max_tokens=1024
        , top_p=1
        , frequency_penalty=0
        , presence_penalty=0)
        
        result = completion['choices'][0]['text']
        result = json.loads(result, strict=False)
        code =  result['code']
        content = '<p>'+result['content']+'</p>'
        print('code:', result['code'])
        print('content', result['content'])


        data = (info.room_id, info.q_id, content, code)
        sql = """
            INSERT INTO `room`.`%s_qa` (`q_id`, `answer`, `code`, `ans_writer`, `time`, `check`) 
            VALUES (%s, %s, %s, 'ai', now(), 0);
        """
        db_cursor.execute_sql(sql, data)

        return True


crud_chatGPT = CrudChatGPT()




