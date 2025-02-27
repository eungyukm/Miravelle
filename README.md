# Miravelle
Miravelle → Miracle(기적) + Belle(아름다움)

## 프로젝트 개요

### 1. 프로젝트 이름
Meshy AI 기반 3D 생성 플랫폼

### 2. 목적
본 프로젝트는 Meshy AI의 API를 활용하여 3D 오브젝트를 자동 생성하고, Django 기반의 웹 애플리케이션을 통해 이를 관리 및 제공하는 플랫폼을 개발하는 것을 목표로 한다.

### 3. 주요 기능
- 사용자 로그인 및 인증 (JWT 활용)
- Meshy AI API를 통한 3D 모델 생성
- 생성된 3D 모델 저장 및 관리
- 생성된 3D 모델의 미리보기 및 다운로드 기능
- 관리자 대시보드를 통한 모델 검토 및 승인

## 기술 스택
| 구성 요소        | 기술 |
|----------------|------|
| 백엔드         | Django, Django REST Framework |
| 데이터베이스   | PostgreSQL |
| 메시징 큐      | Celery + Redis (비동기 작업 처리) |
| 프론트엔드     | React (선택사항) |
| 3D 뷰어       | Three.js (WebGL) |
| API 연동      | Meshy AI API |
| 배포 및 운영   | Azure (App Service) |

## 시스템 아키텍처
```
사용자 → Django API → Meshy AI API → 3D 모델 생성 → 저장 및 제공
```

## 데이터 흐름
1. 사용자가 Django 웹 애플리케이션에 로그인
2. 3D 모델 생성 요청을 API로 전송
3. Django 백엔드에서 Meshy AI API 호출
4. Meshy AI에서 3D 모델을 생성 후 반환
5. 생성된 3D 모델을 데이터베이스에 저장하고 파일 서버에 업로드
6. 사용자는 3D 뷰어를 통해 모델 확인 후 다운로드 가능

## API 엔드포인트
- `POST /api/auth/register/` : 사용자 회원가입
- `POST /api/auth/login/` : 로그인 및 JWT 발급
- `GET /api/auth/profile/` : 사용자 정보 조회
- `POST /api/models/create/` : Meshy AI API를 호출하여 모델 생성
- `GET /api/models/{id}/` : 생성된 모델 조회
- `DELETE /api/models/{id}/` : 모델 삭제

## 설치 및 실행 방법
```bash
git clone https://github.com/your-repo/meshy-ai-3d-platform.git
cd meshy-ai-3d-platform
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## 기여 방법
기여를 원하시면 이슈를 생성하고 PR을 제출해 주세요. 

## 라이선스
MIT 라이선스

