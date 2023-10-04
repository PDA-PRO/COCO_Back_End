FROM python:3.10

WORKDIR /home

# TODO : worker에 필요한 라이브러리, 파일들만 복사해서 이미지 경량화 필요
COPY requirements.txt /home/app/requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /home/app/requirements.txt

#isolate 설치
RUN apt-get update && apt-get install libcap-dev -y
RUN git clone https://github.com/ioi/isolate.git && cd isolate && make install

COPY ./app /home/app

# 초기화, 시작 스크립트 복사
ADD celery_start.sh .
ADD celery_ready.py .

# 컨테이너가 시작될때마다 시작 스크립트 실행
ENTRYPOINT ["./celery_start.sh"]