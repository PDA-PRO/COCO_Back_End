from fastapi.responses import FileResponse
from core import security
from crud.task import task_crud
from fastapi import APIRouter, Depends, Form, HTTPException
from schemas.task import *

router = APIRouter(prefix="/task")

@router.post('/', tags=['task'])
async def create_task(description:str=Form(...),task: Task = Depends(), token: dict = Depends(security.check_token)):
    """ 
    새로운 문제를 생성

    - description: 문제 메인 설명
    - task : 문제의 요소들
        - title: 문제 제목
        - inputDescription: 입력 예제 설명
        - inputEx1: 입력 예제 1
        - inputEx2: 입략 예제 2
        - outputDescription: 출력 예제 설명
        - outputEx1: 출력 예제 1
        - outputEx2: 출력 예제 2
        - testCase: 테스트 케이스 zip파일
        - diff: 난이도
        - timeLimit: 시간제한
        - memLimit: 메모리제한
        - category: 문제 카테고리 ','로 구분된 문자열
    - token : 사용자 인증
    """
    return {
        "result":  task_crud.create_task(description,task)
    }

@router.get('/', tags=['task'], response_model=TaskList)
async def read_task(query:ReadTask=Depends()):
    """
    문제 리스트에서 쿼리에 맞는 문제들의 정보만 리턴
    keyword, diff, category는 AND 로 결합
    
    - query : 문제 쿼리 정보
        - keyword: 검색할 id 혹은 title 정보
        - diff: 문제 난이도 | 1~5의 정수 값이 ','로 구분된 문자열 다중값 가능
        - category: 문제 카테고리 | ','로 구분된 문자열 다중값 가능
        - rateSort: 정답률 기준 정렬 | 0 - 기본 정렬 1 - 오름차순 2 - 내림차순 
        - size: 한페이지의 크기
        - page: 페이지 번호
    """
    return task_crud.read_task(query)

@router.get('/{task_id}/', tags=['task'],response_model=TaskDetail)
async def task_detail(task_id: int):
    """
    원하는 문제의 상세한 정보 조회

    task_id: 문제 id
    """
    response=task_crud.task_detail(task_id)
    if response:
        return response
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@router.put('/', tags=['task'])
async def update_task(task_id:int,description:str=Form(...),task: Task = Depends(), token: dict = Depends(security.check_token)):
    """ 
    문제 수정

    - task_id : 문제 id
    - description: 문제 메인 설명
    - task : 문제의 요소들
        - title: 문제 제목
        - inputDescription: 입력 예제 설명
        - inputEx1: 입력 예제 1
        - inputEx2: 입략 예제 2
        - outputDescription: 출력 예제 설명
        - outputEx1: 출력 예제 1
        - outputEx2: 출력 예제 2
        - testCase: 테스트 케이스 zip파일
        - diff: 난이도
        - timeLimit: 시간제한
        - memLimit: 메모리제한
        - category: 문제 카테고리 ','로 구분된 문자열
    - token : 사용자 인증
    """
    return {
        "result":  task_crud.update_task(task_id,description,task)
    }
    
@router.delete('/', tags=['task'])
async def delete_task(task_id:int, token: dict = Depends(security.check_token)):
    """
    문제 삭제
    db에서 문제 데이터 삭제 및 로컬 스토리지에서 문제 데이터 삭제

    - task_id : 문제 id
    - token : 사용자 인증
    """
    return task_crud.delete_task(task_id)

@router.post('/category', tags=['task'])
async def create_category(category:str, token: dict = Depends(security.check_token)):
    """
    문제 카테고리 생성

    - category : 카테고리
    - token : 사용자 인증
    """
    return task_crud.create_category(category)

@router.get('/category', tags=['task'],response_model=list[str])
async def read_category():
    """
    문제 카테고리 조회

    - token : 사용자 인증
    """
    return task_crud.read_category()

@router.delete('/category', tags=['task'])
async def delete_category(category:str, token: dict = Depends(security.check_token)):
    """
    해당 카테고리를 가지는 문제가 존재하지 않는다면 삭제

    - category : 카테고리
    - token : 사용자 인증
    """
    return task_crud.delete_category(category)

@router.get('/testcase/{task_id}', tags=['task'])
async def get_testcase(task_id:int):
    """
    문제에 대한 테스트 케이스 조회

    - task_id : 문제 id
    """
    return FileResponse(task_crud.get_testcase(task_id),media_type="application/x-zip-compressed")