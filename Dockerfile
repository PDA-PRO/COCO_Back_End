# # 파이썬 이미지에서부터 시작
# FROM python:3.10.8

# # 현재 실행 디렉토리 설정, requirement.txt. app 폴더가 있는 곳
# WORKDIR /COCO_Back_End/app

# # requirements.txt를 /COCO_Back_End 디렉토리에 복사
# COPY ./requirements.txt /COCO_Back_End/app/requirements.txt

# # requirements.txt내의 패키지 설치
# RUN pip install --no-cache-dir -r /COCO_Back_End/app/requirements.txt

# #  ./app 디렉토리를 /COCO_Back_End안으로 복사
# COPY ./app /COCO_Back_End/app

# # uvicorn 서버 실행 명령어
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# # "7000": uvicorn 포트


# 실행 방법
# 1. docker build -t {image 이름} .
# 2. docker run -d --name {container이름} -p {접속할 포트}:{uvicorn포트} {이미지 이름}
# or docker run -p {접속할 포트}:{uvicorn포트} myimage -> 자동으로 컨테이너 생성
# -> http://localhost:{접속할 포트}/ 접속

# FROM python:3.10

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# EXPOSE 8000
# CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]