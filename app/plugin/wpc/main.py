from fastapi import Depends
import requests
from app.api.deps import get_cursor
from app.core import security
from app.db.base import DBCursor
from app.plugin.interface import AbstractPlugin
from app.crud.submission import submission_crud
from app.crud.task import task_crud

class Plugin(AbstractPlugin):
    router_path='/wpc'
    wpc_docker_url='http://localhost:7555'
    feature_docs='TC 판별 중 틀린 코드에 대해, 틀린 부분을 찾아 고쳐주는 AI'
    base='GraphCodeBERT기반 제작 WPC AI 모델'
    
    class TableModel(AbstractPlugin.AbstractTable):
        __key__='sub_id'
        __tablename__='wpc'
        sub_id:int
        status:int
        result:str
        raw_code:str
        
    @staticmethod
    def test():
        res=None
        try:
            res= requests.get(Plugin.wpc_docker_url+'/hello')
            print(res.content)
        except:
            return False
        
        return 1
        
    @staticmethod
    def endpoint_main(sub_id:int,task_id:int,token: dict = Depends(security.check_token),db_cursor:DBCursor=Depends(get_cursor)):
        """
        WPC:Wrong Part of Code 분석 결과 조회
        서버에 WPC 확장기능이 적용되어 있어야함.
        WPC 분석이 가능한 제출코드는 TC틀림으로 인한 오답, 512토큰 이하, 문제 제목에 wpc:p00000 형식의 wpc문제 코드가 존재해야함

        params
        - sub_id : 제출 id
        - task_id : 문제 id
        - token :jwt
        ------------------------------------
        returns
        - status : wpc 분석 결과 `1`분석 성공 `2`TC틀림 오답이 아님 `3`wpc 불가능 문제 `4`512토큰 초과
        """
        
        prev_result:Plugin.TableModel=Plugin.read(db_cursor,sub_id=sub_id)
        if prev_result:
            if prev_result.status==2: #TC 실패로 틀린 제출이 아님
                return {"status":2}
            elif prev_result.status==3: #wpc가 불가능한 문제
                return {"status":3}
            elif prev_result.status==4: #wpc의 제한사항(512토큰 이하)을 초과
                return {"status":4}
            else:
                return {"status":1,"wpc_result":prev_result.result,"bug_code":prev_result.raw_code}
        else:
            pass
            task_title=task_crud.read(db_cursor,["title"],id=task_id)
            if "wpc:" not in task_title[0]["title"]:
                new_wpc=Plugin.TableModel(sub_id=sub_id,status=3)
                Plugin.create(db_cursor,new_wpc)
                return {"status":3}

            sub_data=submission_crud.read(db_cursor,["code","message"],id=sub_id)
            if sub_data[0]["message"]!="TC 실패":
                new_wpc=Plugin.TableModel(sub_id=sub_id,status=2)
                Plugin.create(db_cursor,new_wpc)
                return {"status":2}
            
            wpc_desc_id=task_title[0]["title"].split("wpc:")[-1]
            wpc_result=None
            try: 
                wpc_result=requests.post(Plugin.wpc_docker_url+'/process',params={"p_id":wpc_desc_id},json={"code":sub_data[0]["code"]})
                wpc_result=wpc_result.json()
            except:
                wpc_result=None
            if wpc_result is None:
                new_wpc=Plugin.TableModel(sub_id=sub_id,status=4)
                Plugin.create(db_cursor,new_wpc)
                return {"status":4}
            new_wpc=Plugin.TableModel(sub_id=sub_id,status=1,result=wpc_result['fixed_code'],raw_code=wpc_result['bug_code'])
            Plugin.create(db_cursor,new_wpc)
            return {"status":1,"wpc_result":wpc_result['fixed_code'],"bug_code":wpc_result['bug_code']}