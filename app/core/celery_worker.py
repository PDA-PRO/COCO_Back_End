from core.celery_app import celery_task
import time
import redis
import subprocess
from contextlib import contextmanager
import os
import glob
from crud.task import CrudTask
from crud.submission import CrudSubmission
from crud.user import user_crud

redis_client = redis.Redis(host='127.0.0.1', port=6379)

SANDBOX_PATH="/home/sjw/COCO_Back_End/sandbox/"
TASK_PATH="/home/sjw/COCO_Back_End/tasks/"

def txt_to_dic(file_path): #txt 파일을 dic 자료형으로 변환 -> metafile의 내용을 메모리에 저장.
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


@contextmanager
def redis_lock(lock_name):
    """Yield 1 if specified lock_name is not already set in redis. Otherwise returns 0.

    Enables sort of lock functionality.
    """
    #키값이 존재하지 않을때만 키를 만든다.
    #만들수 있다면 1을 출력 없다면 0을 출력
    #레디스는 자체적으로 한시점에서 한가지의 명령만 수행하기 때문에 이를 이용하여 뮤텍스 구현
    status = redis_client.set(lock_name, 'lock', nx=True)
    try:
        yield status
    finally:
        redis_client.delete(lock_name)

def ready_C(code,box_id,sub_id):#C언어 채점 준비 -> 소스코드 컴파일
    submit=CrudSubmission()
    with open('/var/local/lib/isolate/'+str(box_id)+'/box/src.c','w') as code_file:
        code_file.write(code)
    #error data 저장공간
    error_path=SANDBOX_PATH+str(box_id)+'/error/compile.txt'
    #meta data 저장공간
    meta_path=SANDBOX_PATH+str(box_id)+'/meta/compile.txt'
    #output data 저장공간
    output_path=SANDBOX_PATH+str(box_id)+'/out/compile.txt'
    
    subprocess.run('isolate --meta '+meta_path+' -E PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" -p5 --cg -d /etc:noexec -b '+str(box_id)+' --run /usr/bin/gcc src.c > '+output_path+' 2> '+error_path,shell=True)

    #실행결과 분석
    exec_result=txt_to_dic(meta_path)
    if exec_result["exitcode"]=="0":#제출 코드 실행 결과가 정상적
        return True
        
    else:#컴파일 에러
        error_file=open(error_path,'r')
        error=error_file.readlines()
        print(error)
        submit.update(sub_id,int(exec_result["exitcode"]),message="컴파일 에러",status_id=exec_result["status"],stderr="".join(error),status=4)
        return False



@celery_task.task(ignore_result=True)
def process_sub(taskid,sourcecode,callbackurl,token,sub_id,lang,user_id):
    box_id=1
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while True:#폴링으로 worker가 남았는지 계속 확인
            with redis_lock('lock') as acquired:
                if acquired:#남았으면 lock 잡고 채점
                    data = conn.get(str(box_id))
                    if int(data)==0:
                        conn.set(str(box_id),1)
                        break
                    box_id=((box_id+1)%9)
                    if box_id==0:
                        box_id=1
                else:#lock을 다른 worker가 잡고있으면 0.1초 후에 다시 확인
                    time.sleep(0.1)

        task=CrudTask()
        result=task.select_task(taskid)

        #sub 테이블 접근에 필요한 객체
        submit=CrudSubmission()
        submit.status_update(sub_id,2)
        #isolate id별로 초기화
        subprocess.run(['isolate', '--cg', '-b',str(box_id),'--init'],capture_output=True,text=True)
        time.sleep(0.2)#격리 공간 생기는 거 기다리기


        #채점
        #TC data 저장공간
        task_path=TASK_PATH+str(taskid)+'/input/'
        TC_list=os.listdir(task_path)
        compile_res=False

        #C언어 컴파일
        if lang==1:
            compile_res=ready_C(sourcecode,box_id,sub_id)
        else:#파이썬이라면 실행파일만 생성
            with open('/var/local/lib/isolate/'+str(box_id)+'/box/src.py','w') as code_file:
                code_file.write(sourcecode)
            compile_res=True

        if compile_res:#컴파일이 성공했다면 채점 시작
            try:
                task_result=1#1이 정답 0이 오답
                for TC_num in range(len(TC_list)):
                    #error data 저장공간
                    error_path=SANDBOX_PATH+str(box_id)+'/error/'+str(TC_num)+'.txt'
                    #meta data 저장공간
                    meta_path=SANDBOX_PATH+str(box_id)+'/meta/'+str(TC_num)+'.txt'
                    #제출 코드 실행 output data 저장공간
                    output_path=SANDBOX_PATH+str(box_id)+'/out/'+str(TC_num)+'.txt'
                    #test case input data 저장공간
                    input_path=TASK_PATH+str(taskid)+'/input/'+TC_list[TC_num]
                    #test case output data 저장공간
                    answer_path=TASK_PATH+str(taskid)+'/output/'+TC_list[TC_num]
                    #isolate 환경에서 실행 C언어는 a.out 실행파일로 채점
                    if lang==1:
                        subprocess.run('isolate --meta '+meta_path+' --cg -t '+str(result["time_limit"])+' -d /etc:noexec --cg-mem='+str(result["mem_limit"]*1000)+' -b '+str(box_id)+' --run ./a.out < '+input_path+' > '+output_path+' 2> '+error_path,shell=True)
                    else:
                        subprocess.run('isolate --meta '+meta_path+' --cg -t '+str(result["time_limit"])+' -d /etc:noexec --cg-mem='+str(result["mem_limit"]*1000)+' -b '+str(box_id)+' --run /usr/bin/python3 src.py < '+input_path+' > '+output_path+' 2> '+error_path,shell=True)
                    
                    #실행결과 분석
                    exec_result=txt_to_dic(meta_path)
                    if exec_result.get("exitcode")==None:#샌드박스에 의해서 종료됨 -> 문제의 제한사항에 걸려서 종료됨
                        submit.update(sub_id,2,message="제한사항에 걸림",status_id=exec_result["status"])
                        task_result=0
                        break
                    else:
                        if exec_result["exitcode"]=="0":#제출 코드 실행 결과가 정상적
                            output_file=open(output_path,'r')
                            output=output_file.readlines()
                            answer_file=open(answer_path,'r')
                            answer=answer_file.readlines()
                            print(output)
                            if len(output):
                                for line_num in range(len(answer)):
                                    if output[line_num].rstrip()!=answer[line_num].rstrip():
                                        submit.update(sub_id,int(exec_result["exitcode"]),stdout="".join(output),number_of_runs=TC_num,message="TC 실패")
                                        task_result=0
                                        output_file.close()
                                        answer_file.close()
                                        break
                            else:
                                submit.update(sub_id,int(exec_result["exitcode"]),number_of_runs=TC_num,message="TC 실패")
                                task_result=0
                                output_file.close()
                                answer_file.close()
                            if task_result==0:
                                break
                            
                        else:#제출코드 실행 결과가 정상적이지 않다. -> 런타임 에러 등 
                            error_file=open(error_path,'r')
                            
                            error=error_file.readlines()
                            print(error)
                            submit.update(sub_id,int(exec_result["exitcode"]),message="런타임 에러",number_of_runs=TC_num,status_id=exec_result["status"],stderr="".join(error))
                            task_result=0
                            break

                if task_result==1:#모든 TC를 통과했다면 정답처리
                    submit.update(sub_id,int(exec_result["exitcode"]),message="정답!",status=3)
                    user_crud.update_exp(user_id)
            except:
                print("채점 중 오류 발생")
        
        #폴더 초기화
        for i in glob.glob(SANDBOX_PATH+str(box_id)+'/error/*'):
            if "keep" in i:
                continue
            os.remove(i)
        for i in glob.glob(SANDBOX_PATH+str(box_id)+'/meta/*'):
            if "keep" in i:
                continue
            os.remove(i)
        for i in glob.glob(SANDBOX_PATH+str(box_id)+'/out/*'):
            if "keep" in i:
                continue
            os.remove(i)

        #정답률 수정
        rate=submit.calc_rate(taskid)
        task.update_rate(taskid,rate)
        
        #isolate id 삭제
        subprocess.run(['isolate', '--cg', '-b',str(box_id),'--cleanup'],capture_output=True)
        conn.set(str(box_id),"0")
