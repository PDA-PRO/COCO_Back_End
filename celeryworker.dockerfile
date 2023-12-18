FROM python:3.10.13-slim

WORKDIR /home

COPY celeryworker_requirments.txt /home/app/celeryworker_requirments.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /home/app/celeryworker_requirments.txt

#isolate 및 필요한 패키지 설치
RUN apt-get update && apt-get install libcap-dev -y && apt-get install git -y && apt-get install make -y && apt-get install gcc -y
RUN git clone https://github.com/ioi/isolate.git && cd isolate && make install
#g++, java 언어 채점 지원
RUN apt-get install g++ -y && apt-get install openjdk-17-jdk

#필요한 파일만 복사
COPY ./app/api/deps.py /home/app/api/deps.py
COPY ./app/crud/base.py /home/app/crud/base.py
COPY ./app/core/celery_worker.py /home/app/core/celery_worker.py
COPY ./app/core/celery_app.py /home/app/core/celery_app.py
COPY ./app/db/ /home/app/db/

# 초기화, 시작 스크립트 복사
ADD celery_start.sh .
ADD celery_ready.py .
RUN sed -i 's/\r$//' ./celery_start.sh

# 컨테이너가 시작될때마다 시작 스크립트 실행
ENTRYPOINT ["./celery_start.sh"]