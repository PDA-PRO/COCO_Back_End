# 파이썬 3.10 이미지 기반
FROM python:3.10.13-slim

#이미지 내의 작업 디렉토리 설정
WORKDIR /home

RUN apt-get update && apt-get install zip -y

#isolate 및 필요한 패키지 설치
RUN apt-get update && apt-get install libcap-dev -y && apt-get install git -y && apt-get install make -y && apt-get install gcc -y && apt-get install redis-server -y
RUN git clone https://github.com/ioi/isolate.git && cd isolate && make install
#g++, java 언어 채점 지원
RUN apt-get install g++ -y && apt-get install openjdk-17-jdk -y

#필요한 라이브러리 설치
COPY requirements.prod.txt /home/app/requirements.prod.txt
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r /home/app/requirements.prod.txt

#8000포트 외부로 열기
EXPOSE 8000

#컨테이너가 시작될 때마다 실행될 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]