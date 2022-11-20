from core.celery_app import celery_task
import time
import redis
import subprocess

@celery_task.task(ignore_result=True)
def process_sub(taskid,stdid,subtime,sourcecode,callbackurl,token ):
    i=1
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while i<9:
            data = conn.get(str(i))
            if int(data)==0:
                conn.set(str(i),1)
                break
            i+=1
        #todo
        # 데이터베이스 연결해서 문제id로 testcase, 제한사항 가져오기
        # 실행 결과 데이터베이스에 업데이트하기
        # callback url 활용 생각하기
        
        #isolate id별로 초기화
        subprocess.run(['isolate', '--cg', '-b',str(i),'--init'],capture_output=True)
        
        # 실행 파일 생성
        f1=open('/var/local/lib/isolate/'+str(i)+'/box/src.py','w')
        f1.write(sourcecode)
        f1.close()

        #테스트 케이스 input 폴더에 복사

        #meta data 저장공간
        meta_path='/home/sjw/COCO_Back_End/sandbox/'+str(i)+'/meta/meta.txt'
        #input data 저장공간
        # input_path='/home/sjw/COCO_Back_End/sandbox/'+str(i)+'/in/in.txt'
        input_path='/home/sjw/COCO_Back_End/tasks/'+str(taskid)+'/input/test1.in'
        #output data 저장공간
        output_path='/home/sjw/COCO_Back_End/sandbox/'+str(i)+'/out/out.txt'


        #isolate 환경에서 실행
        subprocess.run('isolate --meta '+meta_path+' --cg -t 2 -b '+str(i)+' --run /usr/bin/python3 src.py < '+input_path+' > '+output_path,shell=True)
        
        #isolate id 삭제
        subprocess.run(['isolate', '--cg', '-b',str(i),'--cleanup'],capture_output=True)

        time.sleep(5)
        conn.set(str(i),"0")