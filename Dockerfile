# 파이썬 3.10 이미지 기반
FROM python:3.10.13-slim

#이미지 내의 작업 디렉토리 설정
WORKDIR /home

#필요한 라이브러리 설치
COPY requirements.prod.txt /home/app/requirements.prod.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /home/app/requirements.prod.txt

#코드 복사
COPY ./app /home/app

ADD ./base_task_set.zip /home/base_task_set.zip
ADD start.sh .
ADD ./profile/base.jpg /static/profile/base.jpg

COPY ./app/plugin /home/temp/plugin
#8000포트 외부로 열기
EXPOSE 8000

#컨테이너가 시작될 때마다 실행될 명령
ENTRYPOINT ["./start.sh"]