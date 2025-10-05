#!/bin/bash
# 백엔드 서버 시작 스크립트 (타임아웃 설정 포함)

export ENABLE_SERVER_SAVE=true

cd backend
source venv/bin/activate || source .venv/bin/activate

# Uvicorn 옵션:
# --timeout-keep-alive: 유휴 연결 타임아웃 (초)
# --timeout-graceful-shutdown: 종료 대기 시간
# --reload: 코드 변경 시 자동 재시작 (개발용)
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --timeout-keep-alive 350 \
  --timeout-graceful-shutdown 30 \
  --reload
