# Investor Routiner

기업 재무분석 자동화 블로그 글 생성 서비스

## 소개

이 프로젝트는 개인 투자자가 기업 재무정보와 최신 뉴스를 기반으로 투자 의사결정을 돕는 블로그 글을 자동으로 작성할 수 있도록 도와주는 서비스입니다.

## 주요 기능

- 기업 재무정보 자동 크롤링 (네이버 증권)
- 분기별 재무데이터 비교 분석
- Perplexity API를 활용한 투자 분석 보고서 생성
- 마크다운 형식의 블로그 글 자동 생성

## 기술 스택

- Frontend: Next.js
- Backend: FastAPI
- 크롤링: Python (BeautifulSoup4)
- API: Perplexity API

## 시작하기

### 백엔드 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
uv pip install -r requirements.txt
uvicorn main:app --reload
```

### 프론트엔드 설정

```bash
cd frontend
npm install
npm run dev
```

## 환경 변수

프로젝트 실행을 위해 다음 환경 변수가 필요합니다:

- `PERPLEXITY_API_KEY`: Perplexity API 키 (사용자 입력)

## 라이선스

MIT License
