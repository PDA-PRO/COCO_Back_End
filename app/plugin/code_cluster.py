from fastapi import Depends
import requests
from app.api.deps import get_cursor
from app.core import security
from app.db.base import DBCursor
from app.plugin.interface import AbstractPlugin
from app.crud.submission import submission_crud
from app.crud.task import task_crud

class Plugin(AbstractPlugin):
    router_path='/code-cluster'
        
    @staticmethod
    def test():
        res=None
        try:
            res= requests.get('http://localhost:2323/hello')
        except:
            return False
        
        return 1
        
    @staticmethod
    def main(task_id:int,code:str,db_cursor:DBCursor=Depends(get_cursor)):
        result=[]
        try:
            result=requests.post('http://localhost:2323/process',params={"task_id":task_id},json={"code":code})
            result=result.json()
        except:
            pass
        return result