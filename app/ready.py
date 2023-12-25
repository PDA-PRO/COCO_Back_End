from dotenv import load_dotenv
load_dotenv(verbose=True,override=True)
import json
import shutil
import zipfile
from app.api.deps import get_cursor
from contextlib import contextmanager
from app.core.security import get_password_hash
import os
from tenacity import retry, stop_after_attempt, wait_fixed
from app.crud.task import task_crud
import sys
import subprocess
import argparse
import traceback

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--prod", dest="prod", action="store_true")          # extra value
args = parser.parse_args()

@retry(wait=wait_fixed(10),stop=stop_after_attempt(20))
def ready(is_prod):

    # 채점 지원 언어 초기화
    try:
        print("채점 지원 언어 확인")
        languages=[
            [0, 'python', None, '/usr/local/bin/python3 src.py', 'src.py', 'python'],
            [1, 'c', '/usr/bin/gcc src.c', './a.out', 'src.c', 'c'],
            [2, 'c++', '/usr/bin/g++ src.cpp', './a.out', 'src.cpp', 'cpp'],
            [3, 'java', '/usr/bin/javac Main.java', '/usr/bin/java Main', 'Main.java', 'java']
        ]
        with contextmanager(get_cursor)() as cur:
            if cur.select_sql("select * from coco.lang"):
                pass
            else:
                for i in languages:
                    print("채점 지원 언어 추가")
                    sql = "INSERT INTO `coco`.`lang` VALUES (%s,%s,%s,%s,%s,%s)"
                    data=i
                    cur.execute_sql(sql,data)
    except Exception as e:
        print(traceback.format_exc())
        raise e
    
    # admin 계정이 없을 시 초기값으로 계정 생성
    try:
        print("admin 계정 확인")
        with contextmanager(get_cursor)() as cur:
            if cur.select_sql("select * from coco.user where id='admin'"):
                pass
            else:
                print("admin 계정 생성")
                sql = "INSERT INTO `coco`.`user` (`id`, `pw`, `name`, `role`, `email`) VALUES (%s,%s,%s,%s,%s)"
                data=(os.getenv("ADMIN_ID"), get_password_hash(os.getenv("ADMIN_PW")), 'admin', 1, 'admin@dot.com')
                cur.execute_sql(sql,data)
    except Exception as e:
        print(traceback.format_exc())
        raise e
    
    # 운영 환경에서만 실행
    if is_prod:
        #필수 디렉토리 검사
        try:
            print("백엔드 static 폴더 검증")
            if not os.path.exists(os.getenv("TASK_PATH")):
                os.mkdir(os.getenv("TASK_PATH"))
            if not os.path.exists(os.getenv("NOTICE_PATH")):
                os.mkdir(os.getenv("NOTICE_PATH"))
            if not os.path.exists(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt")):
                with open(os.path.join(os.getenv("NOTICE_PATH"),"notice.txt"),"w", encoding="UTF-8") as file:
                    file.write("")
            if not os.path.exists(os.getenv("BOARD_PATH")):
                os.mkdir(os.getenv("BOARD_PATH"))
            if not os.path.exists(os.getenv("PROFILE_PATH")):
                os.mkdir(os.getenv("PROFILE_PATH"))
            if not os.path.exists(os.getenv("ROADMAP_PATH")):
                os.mkdir(os.getenv("ROADMAP_PATH"))
            if not os.path.exists(os.getenv("LINT_PATH")):
                os.mkdir(os.getenv("LINT_PATH"))
        except Exception as e:
            print(traceback.format_exc())
            raise e
            
        # 기본 문제 셋 추가
        try:
            print("기본 문제 Set 확인")
            with contextmanager(get_cursor)() as db_cursor:
                if len(task_crud.read(db_cursor,['id']))==0:
                    print("기본 문제 Set 생성")
                    zip_path='/home/base_task_set'

                    #base_task_set.zip 압축해제
                    if not os.path.exists(zip_path):
                        with zipfile.ZipFile(zip_path+'.zip') as encrypt_zip:
                            encrypt_zip.extractall(
                                zip_path,
                                None
                            )

                    #기본 문제 Set 카테고리 생성
                    try:
                        task_crud.create(db_cursor,{"category":'wpc'},table="task_category")
                        task_crud.create(db_cursor,{"category":'기본 문제'},table="task_category")
                        task_crud.create(db_cursor,{"category":'ai'},table="task_category")
                    except:
                        pass

                    
                    with open(zip_path+'/task_detail.json','r',encoding='utf8') as file:
                        temp=json.load(file)
                        count=0
                        for i in temp.items():
                            count+=1
                            if count%50==0:
                                print(f"414개중 {count}개 생성완료")
                            description=i[1]['desc']+'\n\n'+i[1]['constraints']+'\n\n문제 출처 : '+i[1]['dataset']
                            inEx1='없음'
                            outEx1='없음'
                            inEx2='없음'
                            outEx2='없음'
                            try:
                                inEx1=i[1]['sample']['input'][0]
                                outEx1=i[1]['sample']['output'][0]
                                inEx2=i[1]['sample']['input'][1]
                                outEx2=i[1]['sample']['output'][1]
                            except:
                                pass
                            diff=1
                            if i[1]['score']=="100":
                                diff=2
                            elif i[1]['score']=="200":
                                diff=3
                            elif i[1]['score']=="300":
                                diff=4
                            task={
                                'title': i[1]['title']+"  wpc:"+i[0]
                                ,'inputDescription': i[1]['input_desc']
                                ,'outputDescription': i[1]['output_desc']
                                ,'diff': diff
                                ,'timeLimit': int(i[1]['limit']['time'])//1000
                                ,'memLimit': int(i[1]['limit']['memory'])//1024
                                ,'category': 'wpc,기본 문제'
                            }
                            sample={'input':[inEx1,inEx2],'output':[outEx1,outEx2]}
                            sample_str=json.dumps(sample)
                            #time_limit, diff는 한자리 숫자 task 테이블에 문제 먼저 삽입해서 id추출
                            sql="INSERT INTO `coco`.`task` ( `title`, `sample`,`mem_limit`, `time_limit`, `diff` ) VALUES ( %s, %s, %s, %s, %s );"
                            data=(task['title'], sample_str,task['memLimit'],task['timeLimit'],task['diff'])
                            task_id=db_cursor.insert_last_id(sql,data)
                            
                            #카테고리 연결
                            for j in map(lambda a:a.strip(),task['category'].split(",")):
                                sql="INSERT INTO `coco`.`task_ids` (`task_id`, `category`) VALUES (%s, %s);"
                                data=(task_id,j)
                                db_cursor.execute_sql(sql,data)

                            #desc 및 테스트케이스 저장
                            sql="insert into coco.descriptions values (%s,%s,%s,%s);"
                            data=(task_id,description,task['inputDescription'],task['outputDescription'])
                            db_cursor.execute_sql(sql,data)

                            try:
                                zip_file_path = os.path.join(os.getenv("TASK_PATH"),str(task_id))
                                with zipfile.ZipFile(zip_path+'/TC/'+i[0]+'.zip') as encrypt_zip:
                                    encrypt_zip.extractall(
                                        zip_file_path,
                                        None
                                    )
                                shutil.move(zip_path+'/TC/'+i[0]+'.zip', zip_file_path+'/testcase'+str(task_id)+".zip")
                            except:
                                print(i[0]+" TC 존재")
        except Exception as e:
            print(traceback.format_exc())
            raise e
        
        if os.getenv("PLUGIN_PATH"):
            if not os.path.exists(os.path.join(os.getenv("PLUGIN_PATH"),'interface.py')):
                shutil.move('/home/temp/plugin/interface.py',os.path.join(os.getenv("PLUGIN_PATH"),'interface.py'))
            for i in os.listdir(os.getenv("PLUGIN_PATH")):
                if i == "__pycache__" or os.path.isfile(os.path.join(os.getenv("PLUGIN_PATH"),i)):
                    continue
                # implement pip as a subprocess:
                is_new=False

                # 종속성 패키지 추출
                reqs=[]
                with open(os.path.join(os.getenv("PLUGIN_PATH"),i,'requirements.txt'),"r") as req_file:
                    for j in req_file.readlines():
                        reqs.append(j.split("=")[0])
                reqs.sort()

                # .cache 파일 존재 확인 및 패키지 비교
                if os.path.exists(os.path.join(os.getenv("PLUGIN_PATH"),i,'.cache')):
                    with open(os.path.join(os.getenv("PLUGIN_PATH"),i,'.cache'),"r") as cache_file:
                        for j,v in enumerate(cache_file.readlines()):
                            try:
                                if reqs[j].strip()!=v.strip():
                                    is_new=True
                                    break
                            except:
                                pass
                else:
                    is_new=True

                # 새로운 플러그인이라면 종속 패키지 설치
                if is_new:
                    print("======================================================================")
                    print(i+" 종속 패키지 설치")
                    print("======================================================================")
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r',os.path.join(os.getenv("PLUGIN_PATH"),i,'requirements.txt')])
                        with open(os.path.join(os.getenv("PLUGIN_PATH"),i,'.cache'),"w") as cache_file:
                            for j in reqs:
                                if j.strip()!="":
                                    cache_file.write(j+"\n")
                    except:
                        pass

if __name__=="__main__":
    ready(args.prod)