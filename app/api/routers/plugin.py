from fastapi import APIRouter, Depends, security, Form
from app.core import security
from app.api.deps import get_cursor,DBCursor
import importlib
import os
from pydantic import BaseModel

router = APIRouter(tags=['plugin'])

if os.getenv("PLUGIN_PATH"):
    for i in os.listdir(os.getenv("PLUGIN_PATH")):
        if i == "__pycache__" or os.path.isfile(os.path.join(os.getenv("PLUGIN_PATH"),i)):
            continue
        print(i+"플러그인 불러오기 시도")
        module=importlib.import_module(f'app.plugin.{i}.main')
        plugin=module.Plugin
        
        if plugin.test():
            print(i+"플러그인 테스트 성공")
            plugin.ready_db()
            print(i+"플러그인 DB 최초 생성")
            for method in dir(plugin):
                method_split=method.split("_")
                if method_split[0]=='endpoint':
                    print(i+"플러그인 엔드포인트 추가 : "+plugin.router_path+'/'+method_split[1])
                    router.add_api_route(plugin.router_path+'/'+method_split[1],endpoint=getattr(plugin,method),methods=['post'])
        else:
            print(i+"플러그인 테스트 실패")

class AiStatus(BaseModel):
    plugin: str
    status: int

@router.get("/plugin/status")
def ai_status(db_cursor:DBCursor=Depends(get_cursor)):
    '''
    ai 플러그인 on/off 여부 확인
    '''
    return db_cursor.select_sql("select * from `plugin`.`status`")

@router.put("/plugin/status")
def update_status(info: AiStatus, db_cursor:DBCursor=Depends(get_cursor)):
    '''
    - info: ai plugin on/off 설정
        - plugin: ai 종류
        - status: on/off 여부
    '''
    data = (info.status,info.plugin)
    sql="UPDATE `plugin`.`status` SET `is_active` = %s where `plugin`=%s"
    db_cursor.execute_sql(sql,data)
    
