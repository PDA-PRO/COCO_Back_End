from fastapi import APIRouter, HTTPException,UploadFile,Depends,Request,status
from fastapi.responses import FileResponse
from core import security
from core.image import image


router = APIRouter(prefix="/image")
    
@router.post("/upload-temp",tags=["image"],)
async def image_upload(request: Request,type:int,file:UploadFile,token: dict = Depends(security.check_token)):
    """
    텍스트 에디터 작성시 임시로 저장되는 사진을 type별로 저장하고 요청된 url로 사진url을 리턴
    JWT토큰 필요

    - request : 요청url
    - type : 1-공지글 2-게시판 3-문제글 4-프로필
    - file : 사진파일
    - token : jwt토큰
    """
    image_name=""
    if type==1:
        image_name=image.upload_temp(file,type)
        return str(request.base_url)+"image/download/"+str(type)+"/"+image_name
    elif type==2:
        image_name=image.upload_temp(file,type,token["id"])
        return str(request.base_url)+"image/download/"+str(type)+"/"+image_name+"/temp?id="+token["id"]
    elif type==3:
        image_name=image.upload_temp(file,type)
        return str(request.base_url)+"image/download/"+str(type)+"/"+image_name+"/temp"
    elif type==4:
        image_name=image.upload_temp(file,type,token["id"])
        return str(request.base_url)+"image/download/"+str(type)+"/"+image_name
    else:
        raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="요청 파라미터가 잘못되었습니다. type은 1-4의 정수값이어야합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("/download/{type}/{filename}",tags=["image"],)
async def image_download(filename:str,type:int,id:str=None,time:str=None):
    """
    실제로 저장된 사진을 리턴

    - filename : 요청하는 사진이름
    - type : 1-공지글 2-게시판 3-문제글 4-프로필
    - id : type별 id
    """
    image_path=""
    if type!=1:
        if id==None and type!=4:
            raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="요청 파라미터가 잘못되었습니다. type이 1이 아닌 경우 id가 필요합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
        else:
            image_path=image.download(filename,type,id)
    else:
        image_path=image.download(filename,type)

    if image_path==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="존재하지 않는 사진입니다.",
        headers={"WWW-Authenticate": "Bearer"},)
    
    return FileResponse(image_path)

@router.get("/download/{type}/{filename}/temp",tags=["image"])
async def image_download(filename:str,type:int,id:str=None):
    """
    텍스트 에디터 작성시 임시로 저장한 사진을 리턴

    - filename: 요청하는 사진이름    
    - type: 2-게시판 3-문제글  
    - id: type별 id
    """
    image_path=""
    if type==2:
        image_path=image.download_temp(filename,type,id)
    elif type==3:
        image_path=image.download_temp(filename,type)
    else:
        raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="요청 파라미터가 잘못되었습니다. type은 2-3의 정수값이어야합니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if image_path==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail="존재하지 않는 사진입니다.",
        headers={"WWW-Authenticate": "Bearer"},)
    
    return FileResponse(image_path)

@router.delete("/delete-image",tags=["image"])
async def delete_image(token: dict = Depends(security.check_token)):
    """
    서버에 저장된 프로필 이미지 삭제

    - token : JWT 토큰
    """
    image.delete_image("",token["id"])
    return 1