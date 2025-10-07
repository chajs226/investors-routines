## 배포 가이드 (Frontend: Vercel/Netlify, Backend: Supabase)

이 문서는 프론트엔드(Next.js)를 Vercel 또는 Netlify에 배포하고, 백엔드를 Supabase(Edge Functions/Storage 등)로 운영하기 위한 체크리스트입니다. 현재 레포 상태는 `frontend`와 `backend`가 분리되어 있으며, 백엔드가 FastAPI로 구현되어 있습니다. Supabase로의 백엔드 이전은 Edge Functions(Typescript/Deno)로의 포팅이 필요합니다.

주의: 본 문서는 “해야 할 일 목록(체크리스트)”를 중심으로 구성되어 있습니다. 실제 구현/마이그레이션 중 코드 변경이 필요합니다.


### 공통 사전 준비
- [ ] **레포 상태 확인**: `feature-deploy` 브랜치 기준 최신 상태인지 확인
- [ ] **도메인 계획**: 최종 배포 도메인(예: Vercel `*.vercel.app` / Netlify `*.netlify.app`) 확정
- [ ] **환경 변수 표준화**: 프론트/백엔드 공통으로 아래 키 사용 계획 수립
  - **NEXT_PUBLIC_API_BASE_URL**: 프론트에서 호출할 백엔드(또는 Supabase Functions) 베이스 URL
  - **PERPLEXITY_MODEL**: 기본 분석 모델명(선택, 기본값 `sonar-pro`)
  - Supabase Functions용 시크릿: **PERPLEXITY_API_KEY**, **ENABLE_SERVER_SAVE** 등


## 1) 프론트엔드 배포 (Next.js)

#### 1-1. Vercel 배포 체크리스트
- [ ] Vercel 계정/팀 준비 및 GitHub 레포 Import
- [ ] Project Root를 `frontend`로 지정
- [ ] Build/Output 설정 확인
  - Build Command: 기본(next build)
  - Output: .next (기본)
- [ ] 환경 변수 추가
  - **NEXT_PUBLIC_API_BASE_URL**: Supabase Functions 엔드포인트 베이스(아래 3-3 참고)
- [ ] 이미지/정적 리소스 도메인 설정이 필요하면 `next.config.ts`의 `images.domains` 구성
- [ ] (선택) 프록시/리라이트 설정 반영
  - 개발용 설정은 현재 `frontend/next.config.ts`에 아래와 같이 되어 있음:
    ```ts
    // 개발 시: /api/backend/* -> http://localhost:8000/api/*
    async rewrites() {
      return [{ source: '/api/backend/:path*', destination: 'http://localhost:8000/api/:path*' }];
    }
    ```
  - 프로덕션에서는 환경 변수를 사용하도록 전환 권장:
    ```ts
    // 프로덕션 예시 (도입 시 코드 수정 필요)
    async rewrites() {
      return [
        {
          source: '/api/backend/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_BASE_URL}/:path*`,
        },
      ];
    }
    ```
- [ ] 배포 후 실제 도메인에서 API 호출이 정상 동작하는지 점검

#### 1-2. Netlify 배포 체크리스트
- [ ] Netlify 계정/팀 준비 및 GitHub 레포 연결
- [ ] Base Directory를 `frontend`로 지정, Build command/Publish directory 기본값 확인
- [ ] 환경 변수 추가
  - **NEXT_PUBLIC_API_BASE_URL**: Supabase Functions 베이스 URL
- [ ] (선택) 프록시/리다이렉트 설정은 `netlify.toml` 활용 가능
  ```toml
  # 예시: /api/backend/* -> ${NEXT_PUBLIC_API_BASE_URL}/*
  [[redirects]]
  from = "/api/backend/*"
  to = "${NEXT_PUBLIC_API_BASE_URL}/:splat"
  status = 200
  force = true
  ````
- [ ] 배포 후 실제 도메인에서 API 호출 점검


## 2) 백엔드 전환 전략 (FastAPI -> Supabase)

현재 백엔드는 FastAPI(`backend/app`)로 구현되어 있으며, 다음 기능을 제공합니다:
- `/api/financial/crawl`: 네이버 증권 크롤링 후 재무 데이터 반환
- `/api/analysis/analyze`: 재무 데이터 + Perplexity API로 투자 분석 보고서 생성
- `/api/analysis/save_markdown`: 마크다운을 프로젝트 `outputs/`에 저장

Supabase로의 배포는 아래 2가지 경로 중 하나로 진행합니다.

#### 경로 A. 단기: FastAPI 호스팅 유지 + Supabase 일부 사용(선택)
- [ ] FastAPI를 별도 호스팅(Railway/Render/Fly/EC2 등)
- [ ] 프론트의 `NEXT_PUBLIC_API_BASE_URL`을 FastAPI 호스트로 설정
- [ ] CORS에서 프론트 도메인 허용(현재 FastAPI는 `*`로 열려있음, 운영 시 특정 도메인으로 제한 권장)
- [ ] (선택) 저장 기능을 Supabase Storage로 변경(아래 3-4 참고) 후 FastAPI에서 Supabase SDK 사용

#### 경로 B. 권장(완전 이전): Supabase Edge Functions로 포팅
- [ ] Supabase 프로젝트 생성 및 기본 설정(아래 3-1)
- [ ] Edge Functions(Typescript/Deno)로 아래 엔드포인트를 재구현
  - [ ] `financial` 함수: 네이버 증권 크롤링 로직 포팅
  - [ ] `analysis` 함수: Perplexity API 호출 및 응답 포맷팅
  - [ ] `save_markdown` 대체: Supabase Storage에 업로드하도록 변경
- [ ] 프론트의 `NEXT_PUBLIC_API_BASE_URL`을 Functions 베이스로 설정
- [ ] CORS/Rate Limit/시크릿 관리 설정

참고: Edge Functions는 Deno 런타임으로, 현재 Python 의존(`pandas`, `beautifulsoup4`, `lxml` 등)을 그대로 사용할 수 없습니다. TS/JS로의 포팅 또는 대체 라이브러리(dom parser 등) 채택이 필요합니다. 크롤링이 어려우면, 별도 크롤링 마이크로서비스를 유지하고 Functions에서 이를 중계하는 설계도 가능합니다.


## 3) Supabase 설정/배포 체크리스트

#### 3-1. 프로젝트/CLI
- [ ] Supabase 계정/프로젝트 생성
- [ ] 로컬에 CLI 설치: `npm i -g supabase`
- [ ] 레포 루트에서 초기화: `supabase init`

#### 3-2. Edge Functions 생성
- [ ] 함수 스켈레톤 생성
  - `supabase functions new financial`
  - `supabase functions new analysis`
- [ ] 각 함수에 CORS 헤더 추가(반드시 프론트 도메인 허용)
  - `Access-Control-Allow-Origin: https://<your-frontend-domain>`
  - `Access-Control-Allow-Methods: POST, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type, Authorization`

#### 3-3. 배포/엔드포인트 확인
- [ ] 로컬 실행: `supabase functions serve --env-file ./supabase/.env`
- [ ] 배포: `supabase functions deploy financial` / `supabase functions deploy analysis`
- [ ] 대시보드에서 각 함수 엔드포인트 확인
  - 일반적으로: `https://<project-ref>.functions.supabase.co/<function-name>`
  - 또는: `https://<project-ref>.supabase.co/functions/v1/<function-name>` (환경에 따라 표시)
- [ ] 프론트 `.env`에 베이스 URL 설정
  - `NEXT_PUBLIC_API_BASE_URL=https://<project-ref>.functions.supabase.co`
  - 프론트 요청: `/api/backend/analysis` -> `${NEXT_PUBLIC_API_BASE_URL}/analysis`로 리라이트

#### 3-4. 시크릿/환경 변수 관리
- [ ] Functions 시크릿 설정
  - `supabase secrets set PERPLEXITY_API_KEY=***`
  - `supabase secrets set PERPLEXITY_MODEL=sonar-pro` (선택)
  - `supabase secrets set ENABLE_SERVER_SAVE=true` (선택)
- [ ] 프론트 환경 변수 설정
  - `NEXT_PUBLIC_API_BASE_URL`
  - (필요 시) `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` 등

#### 3-5. Storage(파일 저장) 전환
- [ ] `save_markdown` 기능을 Supabase Storage로 대체
  - 버킷 생성: 예) `reports`
  - 함수에서 업로드: `PUT /storage/v1/object/reports/<filename>.md`
  - 공개/권한 정책 설정(공개 링크 필요 시 Public, 아니면 RLS 정책 작성)
- [ ] 업로드 결과를 프론트로 반환(경로/퍼블릭 URL)

#### 3-6. 보안/운영
- [ ] CORS: 프론트 도메인만 허용(와일드카드 금지)
- [ ] Rate Limit/캐시: Functions 수준에서 제한 고려(악성 트래픽 방지)
- [ ] 로깅/모니터링: Supabase 로그 뷰, 알림 설정
- [ ] 비용 관리: Perplexity API 호출 수/토큰 비용 모니터링


## 4) API 계약 및 요청/응답 정리

현재 FastAPI 기준 계약을 Supabase Functions에도 유지하는 것을 권장합니다. 단, 보안 강화를 위해 `api_key`를 클라이언트로부터 받지 않고 서버 시크릿으로만 사용하도록 변경을 권장합니다.

- `/financial/crawl` (POST)
  - 요청: `{ stock_code: string, stock_name?: string, compare_periods: string[], market?: string }`
  - 응답: `financial_data: Array<Record<string, number|string>>`, `csv_path`(Functions에서는 미제공 또는 Storage 경로)

- `/analysis/analyze` (POST)
  - 요청: `{ stock_code, stock_name, compare_periods, market?, model? }`
  - 서버: `PERPLEXITY_API_KEY`를 시크릿에서 로드해 사용, `PERPLEXITY_MODEL` 우선순위는 `query > body > env`
  - 응답: `analysis, financial_table, citations, model, usage, created`

- `/analysis/save_markdown` (POST) → Storage 업로드로 대체
  - 요청: `{ filename: string, content: string }`
  - 응답: `{ saved: boolean, path: string, url?: string }`


## 5) 프론트엔드 연동 점검 리스트
- [ ] `.env`에 `NEXT_PUBLIC_API_BASE_URL` 설정 및 빌드 재시작
- [ ] `next.config.ts`의 rewrites가 프로덕션에서도 동작하도록 환경 변수 기반으로 전환
- [ ] CORS 에러 확인 시 Functions의 응답 헤더 점검
- [ ] 결과 마크다운 저장 동작 확인(Storage 업로드 후 URL 반환)
- [ ] 로딩/에러 UX 최종 점검


## 6) 테스트/런북
- [ ] 로컬 E2E: 프론트(개발 서버) → Functions(serve) → Perplexity(실호출) 흐름 확인
- [ ] 스테이징: Vercel/Netlify Preview 환경 도메인으로 CORS 허용 후 점검
- [ ] 운영 배포 승인 플로우 수립(체크리스트 완료 시에만 배포)
- [ ] 롤백 계획: Functions 이전 버전으로 재배포, 프론트 환경 변수 롤백


## 부록 A. 환경 변수/시크릿 요약
- **프론트**
  - `NEXT_PUBLIC_API_BASE_URL`
  - (선택) `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`

- **Supabase Functions 시크릿**
  - `PERPLEXITY_API_KEY` (필수)
  - `PERPLEXITY_MODEL` (선택, 기본 `sonar-pro`)
  - `ENABLE_SERVER_SAVE` (선택, Storage 업로드 기능 사용 시 의미 축소)

## 부록 B. 알려진 차이/주의사항
- Edge Functions는 Deno이며 Python 패키지를 사용할 수 없습니다. 네이버 크롤링 로직은 TS/JS로 재작성하거나, 외부 크롤링 서비스로 위임해야 합니다.
- 기존 `outputs/` 로컬 저장은 Functions 환경에서 동작하지 않습니다. Supabase Storage를 사용하세요.
- CORS는 운영 도메인만 화이트리스트로 허용하세요.


