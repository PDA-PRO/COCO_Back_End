from core.celery_app import celery_task
import time
import redis
import subprocess
from contextlib import contextmanager
import os
import glob
from crud.task import CrudTask
from crud.submission import CrudSubmission

redis_client = redis.Redis(host='127.0.0.1', port=6379)

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

@celery_task.task(ignore_result=True)
def process_sub(taskid,sourcecode,callbackurl,token,sub_id):
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
        #todo
        # callback url 활용 생각하기

        # 데이터베이스 연결해서 문제id로 제한사항 가져오기
        task=CrudTask()
        result=task.select_task(taskid)

        #sub 테이블 접근에 필요한 객체
        submit=CrudSubmission()
        submit.status_update(sub_id,2)
        #isolate id별로 초기화
        init_result= subprocess.run(['isolate', '--cg', '-b',str(box_id),'--init'],capture_output=True,text=True)
        time.sleep(0.2)#격리 공간 생기는 거 기다리기

        # 실행 파일 생성
        with open('/var/local/lib/isolate/'+str(box_id)+'/box/src.py','w') as code_file:
            code_file.write(sourcecode)

        #채점
        #TC data 저장공간
        task_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/input/'
        TC_list=os.listdir(task_path)

        task_result=1#1이 정답 0이 오답
        for TC_num in range(len(TC_list)):
            #error data 저장공간
            error_path='/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/error/'+str(TC_num)+'.txt'
            #meta data 저장공간
            meta_path='/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/meta/'+str(TC_num)+'.txt'
            #제출 코드 실행 output data 저장공간
            output_path='/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/out/'+str(TC_num)+'.txt'
            #test case input data 저장공간
            input_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/input/'+TC_list[TC_num]
            #test case output data 저장공간
            answer_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/output/'+TC_list[TC_num]
            #isolate 환경에서 실행
            subprocess.run('isolate --meta '+meta_path+' --cg -t '+str(result[6])+' -d /etc:noexec --cg-mem='+str(result[5]*1000)+' -b '+str(box_id)+' --run /usr/bin/python3 src.py < '+input_path+' > '+output_path+' 2> '+error_path,shell=True)
            
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
        
        #폴더 초기화
        for i in glob.glob('/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/error/*'):
            os.remove(i)
        for i in glob.glob('/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/meta/*'):
            os.remove(i)
        for i in glob.glob('/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/out/*'):
            os.remove(i)
        
    
        #isolate id 삭제
        clean_result=subprocess.run(['isolate', '--cg', '-b',str(box_id),'--cleanup'],capture_output=True)
        conn.set(str(box_id),"0")
