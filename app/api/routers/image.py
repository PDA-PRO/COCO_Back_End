from fastapi import APIRouter, HTTPException,UploadFile,Depends,Request,status
from fastapi.responses import FileResponse
from core import security
from core.image import image

router = APIRouter(prefix="/image")

exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="요청 파라미터가 잘못되었습니다. type이 1이 아닌 경우 id가 필요합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/upload",tags=["image"],)
async def image_upload(request: Request,type:int,file:UploadFile,id:str=None,token: dict = Depends(security.check_token)):
    """type 1 공지글 type 2 게시판 type 3문제글 type 4 프로필"""
    image_path=""
    if type!=1:
        if id==None:
            raise exception
        else:
            image_path=image.upload(type,id,file,token["role"])
            return str(request.base_url)+"image/download/"+str(type)+"/"+image_path+"?id="+str(id)
    else:
        image_path=image.upload(type,id,file,token["role"])
        return str(request.base_url)+"image/download/"+str(type)+"/"+image_path
    
@router.post("/upload-temp",tags=["image"],)
async def image_upload(request: Request,type:int,file:UploadFile,id:str=None):
    """type 1 공지글 type 2 게시판 type 3문제글 type 4 프로필"""
    image_path=""
    if type==1:
        image_path=image.upload_temp_notice(file)
    return str(request.base_url)+"image/download/"+str(type)+"/"+image_path

@router.get("/download/{type}/{filename}",tags=["image"],)
async def image_download(filename:str,type:int,id:str=None):

    image_path=""
    if type!=1:
        if id==None:
            raise exception
        else:
            image_path=image.download(filename,type,id)
    else:
        image_path=image.download(filename,type,id)
    return FileResponse(image_path)

