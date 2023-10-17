from fastapi import APIRouter,Depends
import importlib
import os

router = APIRouter()

for i in os.getenv("PLUG_IN_LIST").split(','):
    module=importlib.import_module('app.plugin.'+i)
    plugin=module.Plugin
    plugin.creat_table()
    if plugin.test():
        router.add_api_route(plugin.router_path+'/main',endpoint=plugin.main,methods=['post'])
    # router.add_api_route(plugin.router_path,endpoint=plugin.test)
    
