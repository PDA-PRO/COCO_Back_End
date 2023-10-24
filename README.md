# COCO_Back_End

[![Build Status](https://app.travis-ci.com/PDA-PRO/COCO_Back_End.svg?branch=develop)](https://app.travis-ci.com/PDA-PRO/COCO_Back_End)

## 개요

- FastAPI를 활용하여 빠른 응답이 가능합니다.
- Iolate와 Celery를 활용하여 격리된 공간에서 제출 코드의 다중 채점을 보장합니다.
- [플러그인](https://github.com/PDA-PRO/COCO-plugin) 으로 기능을 확장할 수 있습니다.
- 기본 문제 셋을 제공합니다.
- GUI 관리자 메뉴를 제공합니다.

## 빠른 시작

[Quick install](https://github.com/PDA-PRO/COCO-deploy)

## 개발 환경으로 시작

개발 환경으로 시작은 예기치 못한 오류가 발생 할 수 있습니다.

### 환경 준비

#### System: Ubuntu 20.04.6 LTS

1. 도커 설치

   ```bash
   sudo apt update
   sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt-get update
   sudo apt-get install docker-ce docker-ce-cli containerd.io
   sudo usermod -aG docker
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. 도커 컴포즈 설치

   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

   Other installation methods: [https://docs.docker.com/install/](https://docs.docker.com/install/)

#### System: Windows 10

1. 도커 데스크탑 설치  
   [도커 데스크탑 설치](https://docs.docker.com/desktop/install/windows-install/)

### 설치하기

1. 공간이 충분한 위치를 선택하고 다음 명령을 실행하세요

   ```bash
   git clone https://github.com/PDA-PRO/COCO_Back_End.git
   cd COCO_Back_End
   ```

2. 도커 이미지 빌드

   ```bash
   docker compose up -d --build
   ```

   데스크탑의 성능에 따라 모든 설정이 끝날떄까지 5~10분이 소요됩니다.

### 실행하기

http://localhost:1000 포트로 접속하여 API 문서를 조회할 수 있습니다.  
기본적으로 설정되어 있는 관리자의 계정은 아이디 `admin` 비밀번호 `admin1234!`입니다.  
`플러그인`을 추가하고 싶다면 https://github.com/PDA-PRO/COCO-plugin 를 방문해주세요

### 환경 설정

`env` 폴더의 환경변수 파일을 수정하여 DB 정보, JWT 만료 기간, 최초 어드민 계정을 수정할 수 있습니다.

## Q&A

## 라이선스
