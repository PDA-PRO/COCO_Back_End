# 파이썬 3.10 이미지 기반
FROM python:3.10

#이미지 내의 작업 디렉토리 설정
WORKDIR /home/app

#필요한 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

#코드 복사
COPY ./app /home/app

#8000포트 외부로 열기
EXPOSE 8000

#컨테이너가 시작될 때마다 실행될 명령
ENTRYPOINT ["./start.sh"]