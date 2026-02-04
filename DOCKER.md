# Docker 배포 가이드

FastAPI + React 기반 자동매매 봇을 Docker로 배포하는 가이드입니다.

## 📋 사전 요구사항

- Docker Engine 20.10+
- Docker Compose 2.0+
- 최소 2GB RAM, 10GB 디스크 공간

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# .env 파일 생성 (필수!)
cp .env.example .env

# .env 파일 편집하여 API 키 입력
nano .env  # 또는 vi, code 등 사용
```

**.env 파일 필수 설정:**
```env
# Upbit API (또는 Bithumb)
UPBIT_ACCESS_KEY=your_access_key
UPBIT_SECRET_KEY=your_secret_key
EXCHANGE=upbit

# Trading Configuration
TRADE_AMOUNT=7000
TARGET_PROFIT=0.01
STOP_LOSS=0.004
```

### 2. Docker 컨테이너 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 접속

- **프론트엔드:** http://localhost:3000
- **백엔드 API:** http://localhost:8000
- **API 문서:** http://localhost:8000/docs

## 📦 상세 명령어

### 컨테이너 관리

```bash
# 시작
docker-compose up -d

# 중지
docker-compose stop

# 재시작
docker-compose restart

# 완전 삭제 (데이터 보존)
docker-compose down

# 완전 삭제 (데이터 포함)
docker-compose down -v
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs

# 실시간 로그 (follow)
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs frontend

# 최근 100줄만 보기
docker-compose logs --tail=100 backend
```

### 이미지 재빌드

```bash
# 코드 변경 후 이미지 재빌드
docker-compose build

# 캐시 없이 재빌드
docker-compose build --no-cache

# 특정 서비스만 재빌드
docker-compose build backend
docker-compose build frontend
```

### 컨테이너 내부 접속

```bash
# Backend 컨테이너 접속
docker exec -it trading-bot-backend /bin/bash

# Frontend 컨테이너 접속
docker exec -it trading-bot-frontend /bin/sh

# Python 인터프리터 실행
docker exec -it trading-bot-backend python
```

## 🔍 헬스체크

Docker Compose는 자동으로 헬스체크를 수행합니다:

```bash
# 컨테이너 상태 확인
docker ps

# 상세 헬스체크 정보
docker inspect trading-bot-backend | grep -A 10 Health
docker inspect trading-bot-frontend | grep -A 10 Health
```

**헬스체크 엔드포인트:**
- Backend: `http://localhost:8000/api/health`
- Frontend: `http://localhost:3000/`

## 💾 데이터 관리

### 볼륨 확인

```bash
# 볼륨 목록
docker volume ls

# 사용 중인 볼륨 상세 정보
docker volume inspect bitthumb_std_data
docker volume inspect bitthumb_std_models
docker volume inspect bitthumb_std_logs
```

### 백업

```bash
# 데이터 백업
docker run --rm -v bitthumb_std_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# 모델 백업
docker run --rm -v bitthumb_std_models:/models -v $(pwd):/backup alpine tar czf /backup/models-backup.tar.gz /models

# 로컬 디렉토리 백업 (권장)
tar czf backup-$(date +%Y%m%d).tar.gz data/ models/ logs/ .env
```

### 복원

```bash
# 백업 복원
docker run --rm -v bitthumb_std_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

## 🛠️ 트러블슈팅

### 포트 충돌

```bash
# 포트가 이미 사용 중인 경우
# docker-compose.yml에서 포트 변경:
ports:
  - "8080:8000"  # 8000 대신 8080 사용
  - "4000:80"    # 3000 대신 4000 사용
```

### 메모리 부족

```bash
# docker-compose.yml에 메모리 제한 추가:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### 로그 디스크 공간 부족

```bash
# 로그 크기 제한 (docker-compose.yml)
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 컨테이너가 시작되지 않을 때

```bash
# 상세 에러 확인
docker-compose logs backend
docker-compose logs frontend

# 이미지 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 네트워크 이슈

```bash
# 네트워크 재생성
docker-compose down
docker network prune -f
docker-compose up -d
```

## 🔐 보안 권장사항

### 1. .env 파일 보호

```bash
# .env 파일 권한 제한
chmod 600 .env

# .env 파일을 절대 Git에 커밋하지 마세요!
# (.gitignore에 이미 추가되어 있음)
```

### 2. 프로덕션 설정

```yaml
# docker-compose.prod.yml 생성
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG=false
    volumes:
      - ./.env:/app/.env:ro  # 읽기 전용
```

### 3. HTTPS 설정 (Nginx + Let's Encrypt)

프로덕션 환경에서는 리버스 프록시 사용 권장:
```bash
# nginx-proxy, traefik 등 사용 권장
```

## 📊 모니터링

### 리소스 사용량 확인

```bash
# 실시간 모니터링
docker stats

# 특정 컨테이너만
docker stats trading-bot-backend trading-bot-frontend
```

### 디스크 사용량

```bash
# Docker 전체 디스크 사용량
docker system df

# 상세 정보
docker system df -v
```

## 🧹 정리

### 미사용 리소스 제거

```bash
# 중지된 컨테이너 제거
docker container prune

# 미사용 이미지 제거
docker image prune

# 미사용 볼륨 제거 (주의!)
docker volume prune

# 전체 정리 (주의! 데이터 손실 가능)
docker system prune -a --volumes
```

## 🔄 업데이트

### 코드 업데이트 후 재배포

```bash
# Git에서 최신 코드 받기
git pull origin main

# 이미지 재빌드 및 재시작
docker-compose down
docker-compose build
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 📝 환경별 설정

### 개발 환경

```bash
# 코드 변경 시 자동 반영 (docker-compose.yml)
volumes:
  - ./backend:/app/backend  # 주석 해제
```

### 프로덕션 환경

```bash
# docker-compose.prod.yml 사용
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🆘 지원

문제가 발생하면:
1. 로그 확인: `docker-compose logs -f`
2. GitHub Issues: https://github.com/Cov4w/upbit-auto-trading-bot/issues
3. 헬스체크 확인: `docker ps`

## 📚 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [프로젝트 README](./README.md)
- [Windows 사용자 가이드](./README-WINDOWS.md)

---

**Last Updated:** 2026-02-04
**Docker Version:** Compatible with Docker Engine 20.10+
