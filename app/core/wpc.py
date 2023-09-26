import os

is_active=False
if os.path.exists("/".join(__file__.split("/")[:-1])+"/COCO_AI/"):
    from app.core.COCO_AI.reference.wpc import WPC
    is_active=True

def process_wpc(code:str,wpc_desc_id:str):
    if is_active:
        wpc=WPC()
        return wpc.process(code,wpc_desc_id)
    else:
        print("모듈 없음")