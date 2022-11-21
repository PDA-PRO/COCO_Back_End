from core.celery_app import celery_task
import time
import redis
import subprocess
from contextlib import contextmanager
import os

redis_client = redis.Redis(host='127.0.0.1', port=6379)

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
def process_sub(taskid,stdid,subtime,sourcecode,callbackurl,token):
    box_id=1
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while True:
            with redis_lock('lock') as acquired:
                if acquired:
                    data = conn.get(str(box_id))
                    if int(data)==0:
                        conn.set(str(box_id),1)
                        break
                    box_id=((box_id+1)%9)
                    if box_id==0:
                        box_id=1
                else:
                    time.sleep(0.1)
        #todo
        # 데이터베이스 연결해서 문제id로 testcase, 제한사항 가져오기
        # 실행 결과 데이터베이스에 업데이트하기
        # callback url 활용 생각하기

        #isolate id별로 초기화
        init_result= subprocess.run(['isolate', '--cg', '-b',str(box_id),'--init'],capture_output=True,text=True)
        time.sleep(0.2)

        # 실행 파일 생성
        with open('/var/local/lib/isolate/'+str(box_id)+'/box/src.py','w') as code_file:
            code_file.write(sourcecode)

        #채점
        #TC data 저장공간
        task_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/input/'
        task_result='collect'
        for TC_num in range(1,len(os.listdir(task_path))+1):
            #error data 저장공간
            error_path='/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/error/error'+str(TC_num)+'.txt'
            #meta data 저장공간
            meta_path='/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/meta/meta'+str(TC_num)+'.txt'
            #제출 코드 실행 output data 저장공간
            output_path='/home/sjw/COCO_Back_End/sandbox/'+str(box_id)+'/out/out'+str(TC_num)+'.txt'
            #test case input data 저장공간
            input_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/input/test'+str(TC_num)+'.in'
            #test case output data 저장공간
            answer_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/output/test'+str(TC_num)+'.out'
            #isolate 환경에서 실행
            subprocess.run('isolate --meta '+meta_path+' --cg -t 5 -d /etc:noexec --cg-mem='+str(128000)+' -b '+str(box_id)+' --stderr-to-stdout --run /usr/bin/python3 src.py < '+input_path+' > '+output_path+' 2> '+error_path,shell=True)
            
            with open(error_path,'r') as error_file:
                #제출 코드 실행 결과가 정상적이지 않다면 채점 종료
                if error_file.readline().split()[0]!='OK':
                    task_result=str(TC_num)+" error"
                    break
                else:
                    #결과가 정상적이다면 결과와 정답과 비교
                    output_file=open(output_path,'r')
                    answer_file=open(answer_path,'r')
                    if output_file.readline().rstrip()!=answer_file.readline().rstrip():
                        task_result=str(TC_num)+" incollect"
                        output_file.close()
                        answer_file.close()
                        break
        conn.set('sub'+str(taskid)+str(stdid),task_result)
    
        #isolate id 삭제
        clean_result=subprocess.run(['isolate', '--cg', '-b',str(box_id),'--cleanup'],capture_output=True)
        time.sleep(0.2)
        conn.set(str(box_id),"0")
