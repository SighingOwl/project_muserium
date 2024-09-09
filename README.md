# project_muserium

A website development for a brand.

## 프로젝트 개요

`project_muserium`은 Django를 기반으로 한 웹사이트 개발 프로젝트입니다. 이 프로젝트는 사용자 인증, 질문 및 답변, 리뷰 작성 등의 기능을 포함하고 있습니다.

## 주요 기능

### 사용자 인증

- Django Allauth를 사용한 소셜 로그인 기능
- JWT를 사용한 인증 및 권한 관리

### 예약 기능
- 클래스 예약 날짜, 시간 조회
- 사용자 예약 추가, 수정, 삭제
- 예약 불가능 날짜, 시간 처리
정
### 구매 기능
- 추가 예정

### 질문 및 답변

- 질문 작성, 조회, 수정, 삭제 기능
- 답변 작성, 조회, 수정, 삭제 기능
- 질문 및 답변에 대한 페이징 처리

### 리뷰

- 리뷰 작성, 조회, 수정, 삭제 기능
- 리뷰에 대한 페이징 처리
- 리뷰 평점 기능

## 요구 사항

- Python 3.12
- Django 5.0.8
- django-extensions 3.2.3
- djangorestframework 3.15.2
- djangorestframework-simplejwt 5.3.1
- django-allauth 64.1.0
- dj-rest-auth 6.0.0
- django-cors-headers 4.4.0
- django-storages 1.14.4
- boto3 1.34.155
- uvicorn 0.30.5
- daphne 4.1.2
- channels 4.1.0
- werkzeug 3.0.3


## 기여 방법

기여를 원하시는 분은 이 저장소를 포크한 후 풀 리퀘스트를 보내주세요. 기여 가이드라인은 추후 업데이트될 예정입니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.