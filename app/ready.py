import json
import shutil
import zipfile
from app.api.deps import get_cursor
from contextlib import contextmanager
from app.core.security import get_password_hash
import os
from tenacity import retry, stop_after_attempt, wait_fixed
from app.crud.task import task_crud

@retry(wait=wait_fixed(5),stop=stop_after_attempt(10),)
def ready():
    #fastapi 시작
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
        raise e
        
    # 기본 문제 셋 추가
    try:
        print("기본 문제 Set 확인")
        with contextmanager(get_cursor)() as db_cursor:
            if len(task_crud.read(db_cursor,['id']))==0:
                print("기본 문제 Set 생성")
                zip_path='/home/base_task_set'

                #base_task_set.zip 압축해제
                with zipfile.ZipFile(zip_path+'.zip') as encrypt_zip:
                    encrypt_zip.extractall(
                        zip_path,
                        None
                    )

                #기본 문제 Set 카테고리 생성
                task_crud.create(db_cursor,{"category":'wpc'},table="task_category")
                task_crud.create(db_cursor,{"category":'기본 문제'},table="task_category")

                
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
                            ,'inputEx1': inEx1
                            ,'inputEx2': inEx2
                            ,'outputDescription': i[1]['output_desc']
                            ,'outputEx1': outEx1
                            ,'outputEx2': outEx2
                            ,'diff': diff
                            ,'timeLimit': int(i[1]['limit']['time'])//1000
                            ,'memLimit': int(i[1]['limit']['memory'])//1024
                            ,'category': 'wpc,기본 문제'
                        }
                        
                        #time_limit, diff는 한자리 숫자 task 테이블에 문제 먼저 삽입해서 id추출
                        sql="INSERT INTO `coco`.`task` ( `title`, `sample`,`mem_limit`, `time_limit`, `diff` ) VALUES ( %s, json_object('input', %s, 'output',%s), %s, %s, %s );"
                        data=(task['title'], f"[{task['inputEx1']}, {task['inputEx2']}]",f"[{task['outputEx1']}, {task['outputEx2']}]",task['memLimit'],task['timeLimit'],task['diff'])
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
        raise e

if __name__=="__main__":
    ready()

