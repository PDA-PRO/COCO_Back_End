from fastapi import Depends
import requests
from app.api.deps import get_cursor
from app.db.base import DBCursor
from app.plugin.interface import AbstractPlugin

class Plugin(AbstractPlugin):
    router_path='/code-cluster'
    wpc_docker_url='http://localhost:7555'
    feature_docs='문제 풀이가 맞은 코드에 대해, 해당 코드와 유사한 로직의 다른 코드들을 만들어 주는 AI'
    base='FAISS from facebook'

    @staticmethod
    def test():
        res=None
        try:
            res= requests.get(f'{Plugin.wpc_docker_url}/hello')
        except:
            return False
        
        return 1
        
    @staticmethod
    def endpoint_main(task_id:int,code:str,db_cursor:DBCursor=Depends(get_cursor)):
        result=[]
        try:
            result=requests.post(f'{Plugin.wpc_docker_url}/process',params={"task_id":task_id},json={"code":code})
            result=result.json()
        except:
            pass
        return result