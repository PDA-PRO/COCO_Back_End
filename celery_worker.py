from celery_app import celery_task
import time
import redis

@celery_task.task(ignore_result=True)
def divide(x, y):

    i=1
    with redis.StrictRedis(host='127.0.0.1', port=6379, db=0) as conn:
        while i<9:
            data = conn.get(str(i))
            if int(data)==0:
                conn.set(str(i),1)
                break
            i+=1
        #isolate가 실행될 곳
        time.sleep(30)
        conn.set(str(i),"0")
    return x / y