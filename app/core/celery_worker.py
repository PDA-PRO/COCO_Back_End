import time
import subprocess
import os
import glob
import traceback
import redis
from contextlib import contextmanager
from app.api.deps import get_cursor
from app.crud.base import Crudbase
from app.core.celery_app import celery_task

crud_base=Crudbase()
get_cursor=contextmanager(get_cursor)

class ScoringResult():
    """
        채점 결과
        - status_id : isolate 런타임 결과 1 - 런타임 오류, 2 - 시간 초과, 3 - 메모리 초과
        - stdout : 표준 출력값
        - stderr : 표준 에러값
        - exit_code : 채점시 런타임 종료 코드 0 - 정상종료, 1 - 런타임 오류
        - message : 채점 결과
        - number_of_runs : 테스트케이스 통과 개수
        - status : 채점 상태 1 - 대기, 2 - 채점중, 3 - 정답, 4 - 오답
    """
    def __init__(self,status_id:int=None,stdout:str=None,stderr:str=None,exit_code:int=None,message:str=None,number_of_runs:int=0,status:int=4,used_memory:int=None,used_time:float=None) -> None:
        self.status_id=status_id
        self.stdout=stdout
        self.stderr=stderr
        self.exit_code=exit_code
        self.message=message
        self.number_of_runs=number_of_runs
        self.status=status
        self.used_memory=used_memory
        self.used_time=used_time

    def to_dict(self):
        print(self.__dict__)
        return self.__dict__


def txt_to_dic(file_path):
    """
    txt 파일을 dic 자료형으로 변환 -> metafile의 내용을 메모리에 저장.

    - file_path : txt 파일 경로
    """
    
    convert={"RE":1,"TO":2,"SG":3}
    result={}
    with open(file_path) as file:
        for i in file.readlines():
            name,value=i.split(":")
            if name=="status":
                value=convert[value.rstrip()]
                result[name]=value
            else:
                result[name]=value.rstrip()
    return result

def ready_C(db_cursor,box_id,sub_id):
    """
    C언어 채점 준비 -> 소스코드 컴파일

    - code : c언어 코드
    - box_id : isolate box id
    - sub_id : 제출 id
    """
    #error data 저장공간
    error_path=os.getenv("SANDBOX_PATH")+str(box_id)+'/error/compile.txt'
    #meta data 저장공간
    meta_path=os.getenv("SANDBOX_PATH")+str(box_id)+'/meta/compile.txt'
    #output data 저장공간
    output_path=os.getenv("SANDBOX_PATH")+str(box_id)+'/out/compile.txt'
    
    subprocess.run('isolate --meta '+meta_path+' -E PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" -p5 -d /etc:noexec -b '+str(box_id)+' --run /usr/bin/gcc src.c > '+output_path+' 2> '+error_path,shell=True)

    #실행결과 분석
    exec_result=txt_to_dic(meta_path)
    if exec_result["exitcode"]=="0":#제출 코드 실행 결과가 정상적
        return True
        
    else:#컴파일 에러
        error_file=open(error_path,'r')
        error=error_file.readlines()
        print(error)
        scoring_res=ScoringResult(exec_result["status"],None,"".join(error),int(exec_result["exitcode"]),"컴파일 에러")
        crud_base.update(db_cursor,scoring_res.to_dict(),db='coco',table='submissions',id=sub_id)
        return False

@contextmanager
def get_isolate(timelimit:int)->int|None:
    """
    현재 사용가능한 isolate box id context를 폴링으로 획득 및 isolate box 초기화
    사용 종료 시 isolate box 삭제 및 box id 를 사용가능으로 변경

    redis는 기본적으로 싱글 쓰레드로 동작하기 때문에 해당 사용중인 box id를 redis에 저장해두고 해당 id가 존재하는지 확인함으로써
    사용중인 isolate box를 다른 celery worker가 공유하지 않도록 구현

    params
    - timelimit : 최대 polling 시간
    -----------------------------------------------------
    return
    - 사용가능한 isolate box id 리턴
    - timelimit 동안 획득 실패시 None 리턴
    """
    box_id=1
    timeover=0
    with redis.StrictRedis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB')) as conn:
        try:
            while timeover<timelimit:#폴링으로 box가 사용가능한지 계속 확인
                if conn.set(str(box_id),1,nx=True):
                    #isolate box 초기화
                    subprocess.run(['isolate', '-b',str(box_id),'--init'],capture_output=True,text=True)
                    time.sleep(0.2)#격리 공간 생기는 거 기다리기
                    yield box_id
                    break
                
                box_id=((box_id+1)%int(os.getenv("CELERY_CONCURRENCY"))+1)
                if box_id==0:
                    box_id=1
                time.sleep(0.1)
                timeover+=1
            else:
                box_id=None
                yield box_id
        finally:
            if box_id:
                #사용가능한 box id를 획득했다면 사용종료 후 isolate box 삭제
                subprocess.run(['isolate', '-b',str(box_id),'--cleanup'],capture_output=True)
            #isolate box id 사용가능으로 설정하기 위해 box id를 삭제
            conn.delete(str(box_id))

def run_pylint(py_file_path, sub_id):     
    json_path = os.path.join(os.getenv("LINT_PATH"),f"{sub_id}.json")
    os.system(f'pylint {py_file_path} --disable=W,C --output-format=json:{json_path}')   

@celery_task.task(ignore_result=True)
def process_sub(taskid,sourcecode,callbackurl,token,sub_id,lang,user_id):
    """
    유저가 제출한 코드를 컴파일, 실행하고 해당 문제의 테스트 케이스를 넣고 출력값을 비교하여 알맞은 코드인지 확인
    db에 저장된 submission 값을 수정하며 채점 정보 저장
    status값은 1 = 대기, 2 = 채점중, 3 = 정답, 4 = 오답
    
    - taskid : 문제 id
    - sourcecode : 제출 code
    - callbackurl : 콜백 url
    - token : 콜백 url에 필요한 토큰
    - sub_id : 제출 id
    - lang : 파이썬 0 | c언어 1
    - user_id : 제출한 유저의 id
    """
    with get_isolate(600) as box_id,get_cursor() as db_cursor:
        if not box_id:
            return
                
        #문제의 제한사항 조회
        result=crud_base.read(db_cursor,db='coco',table='task',id=taskid)[0]
        
        #제출 현재 상태를 2("채점중")으로 변경
        crud_base.update(db_cursor,{"status":2},db='coco',table='submissions',id=sub_id)

        #TC data 저장공간
        task_path=os.getenv("TASK_PATH")+str(taskid)+'/input/'
        code_file_path='/var/local/lib/isolate/'+str(box_id)+'/box/'
        TC_list=os.listdir(task_path)
        compile_res=False
        scoring_res=ScoringResult(exit_code=0,message="정답!",number_of_runs=len(TC_list),status=3)

        
        if lang==1:#C언어 컴파일
            code_file_path+="src.c"
            with open(code_file_path,'w') as code_file:
                code_file.write(sourcecode)
            compile_res=ready_C(box_id,sub_id)
        else:#파이썬이라면 실행파일만 생성
            code_file_path+="src.py"
            with open(code_file_path,'w') as code_file:
                code_file.write(sourcecode)
            compile_res=True

        if compile_res:#컴파일이 성공했다면 채점 시작
            try:
                task_result=1#1이 정답 0이 오답
                for TC_num in range(len(TC_list)):
                    #error data 저장공간
                    error_path=os.getenv("SANDBOX_PATH")+str(box_id)+'/error/'+str(TC_num)+'.txt'
                    #meta data 저장공간
                    meta_path=os.getenv("SANDBOX_PATH")+str(box_id)+'/meta/'+str(TC_num)+'.txt'
                    #제출 코드 실행 output data 저장공간
                    output_path=os.getenv("SANDBOX_PATH")+str(box_id)+'/out/'+str(TC_num)+'.txt'
                    #test case input data 저장공간
                    input_path=os.getenv("TASK_PATH")+str(taskid)+'/input/'+TC_list[TC_num]
                    #test case output data 저장공간
                    answer_path=os.getenv("TASK_PATH")+str(taskid)+'/output/'+TC_list[TC_num]

                    #isolate 환경에서 실행 C언어는 a.out 실행파일로 채점
                    #warning docker 환경에서는 /usr/local/bin/python3
                    if lang==1:
                        subprocess.run('isolate -M '+meta_path+' -t '+str(result["time_limit"])+' -d /etc:noexec -m '+str(result["mem_limit"]*1500)+' -b '+str(box_id)+' --run ./a.out < '+input_path+' > '+output_path+' 2> '+error_path,shell=True)
                    else:
                        subprocess.run('isolate -M '+meta_path+' -t '+str(result["time_limit"])+' -d /etc:noexec -m '+str(result["mem_limit"]*1500)+' -b '+str(box_id)+' --run /usr/local/bin/python3 src.py < '+input_path+' > '+output_path+' 2> '+error_path,shell=True)
                    
                    #실행결과 분석
                    exec_result=txt_to_dic(meta_path)
                    if exec_result.get("exitcode")==None:#샌드박스에 의해서 종료됨 -> 문제의 제한사항에 걸려서 종료됨
                        scoring_res.status_id=exec_result["status"]
                        scoring_res.exit_code=2
                        scoring_res.message="제한사항에 걸림"
                        scoring_res.number_of_runs=TC_num
                        scoring_res.status=4
                        task_result=0
                        break
                    else:
                        if exec_result["exitcode"]=="0":#제출 코드 실행 결과가 정상적
                            with open(output_path,'r') as output_file,open(answer_path,'r') as answer_file:
                                output=output_file.readlines()
                                answer=answer_file.readlines()
                                scoring_res.status_id=None
                                max_len=max(len(output),len(answer))
                                for line_num in range(max_len):
                                    output_line=""
                                    answer_line=""
                                    if line_num<len(output):
                                        output_line=output[line_num].rstrip()
                                    if line_num<len(answer):
                                        answer_line=answer[line_num].rstrip()                                    
                                    if output_line!=answer_line:
                                        scoring_res.stdout="".join(output)
                                        task_result=0
                                        break
                                if task_result==0: #TC를 틀린 경우
                                    scoring_res.exit_code=int(exec_result["exitcode"])
                                    scoring_res.message="TC 실패"
                                    scoring_res.number_of_runs=TC_num
                                    scoring_res.status=4
                                    break
                            
                        else:#제출코드 실행 결과가 정상적이지 않다. -> 런타임 에러 등 
                            error_file=open(error_path,'r')
                            error=error_file.readlines()
                            scoring_res.status_id=exec_result["status"]
                            scoring_res.stderr="".join(error)
                            scoring_res.exit_code=int(exec_result["exitcode"])
                            scoring_res.message="런타임 에러"
                            scoring_res.number_of_runs=TC_num
                            scoring_res.status=4
                            task_result=0
                            break

                if task_result==1:#모든 TC를 통과했다면 정답처리
                    print('맞음')
                    scoring_res.used_time=float(exec_result["time"])
                    scoring_res.used_memory=int(exec_result["max-rss"])
                    crud_base.update(db_cursor,scoring_res.to_dict(),'coco','submissions',id=sub_id)
                    #유저의 경험치 업데이트
                    user_solved_list=crud_base.read(db_cursor,['task_id','diff'],'coco','user_problem',user_id=user_id,status=3)
                    new_exp=0
                    dupe=[]
                    for i in user_solved_list:
                        if i['task_id'] not in dupe:
                            dupe.append(i['task_id'])
                            new_exp+=i["diff"]*100
                    crud_base.update(db_cursor,{'exp':new_exp},'coco','user',id=user_id)
                else:
                    print('틀림')
                    crud_base.update(db_cursor,scoring_res.to_dict(),'coco','submissions',id=sub_id)
                    if lang==0:
                        run_pylint(code_file_path,sub_id)
            except:
                print(traceback.format_exc())
                print("채점 중 오류 발생")
        
        #폴더 초기화
        for i in glob.glob(os.getenv("SANDBOX_PATH")+str(box_id)+'/error/*'):
            if "keep" in i:
                continue
            os.remove(i)
        for i in glob.glob(os.getenv("SANDBOX_PATH")+str(box_id)+'/meta/*'):
            if "keep" in i:
                continue
            os.remove(i)
        for i in glob.glob(os.getenv("SANDBOX_PATH")+str(box_id)+'/out/*'):
            if "keep" in i:
                continue
            os.remove(i)

        #정답률 수정
        all_sub=crud_base.read(db_cursor,['status'],'coco','status_list',task_id=taskid)
        right_sub=0
        for i in all_sub:
            if i.get("status")==3:
                right_sub+=1
        rate=round(right_sub/len(all_sub)*100,1)
        crud_base.update(db_cursor,{"rate":rate},'coco','task',id=taskid)

        # 내 문제집 문제 풀이 여부 수정
        sql = "select i.task_id, i.sub_id from coco.sub_ids as i, coco.my_tasks as t where t.user_id = %s and t.user_id = i.user_id and t.task_num = i.task_id and i.task_id = %s order by i.sub_id desc;"
        data = (user_id, taskid)
        result = db_cursor.select_sql(sql, data)
        print('result', result)
        if not result:
            pass
        else:
            for value in result:
                print('result[0]', result)
                sql = "select status from coco.submissions where id = %s;"
                data = (value['sub_id'])
                status = db_cursor.select_sql(sql, data)
                status = status[0]['status']
                if status == 3:
                    sql = "UPDATE coco.my_tasks SET solved = 1 WHERE user_id = %s and task_num = %s;"
                    data = (user_id, taskid)
                    db_cursor.execute_sql(sql, data)
                    break
            else:
                sql = "UPDATE coco.my_tasks SET solved = -1 WHERE user_id = %s and task_num = %s;"
                data = (user_id, taskid)
                db_cursor.execute_sql(sql, data) 
