from fastapi import APIRouter,Depends
import importlib
import os

router = APIRouter()

if os.getenv("PLUG_IN_LIST"):
    for i in os.getenv("PLUG_IN_LIST").split(','):
        try:
            module=importlib.import_module('app.plugin.'+i.strip())
        except:
            print(i.strip()+" 모듈이 존재하지 않습니다.")
        plugin=module.Plugin
        try:
            plugin.create_table()
        except:
            pass
        if plugin.test():
            router.add_api_route(plugin.router_path+'/main',endpoint=plugin.main,methods=['post'])
        # router.add_api_route(plugin.router_path,endpoint=plugin.test)
    
