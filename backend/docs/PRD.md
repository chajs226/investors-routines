# 📄 PRD: 기업 재무분석 자동화 블로그 글 생성 서비스

## 1. 목표 (Goal)
개인 투자자가 **기업 재무정보와 최신 뉴스**를 기반으로 투자 의사결정을 돕는 블로그 글을 자동으로 작성할 수 있도록 한다.  
사용자는 **기업명/종목코드**, **비교할 분기**, **대상 분기**, **Perplexity API 키**만 입력하면:
1. 네이버 증권에서 해당 기업의 재무정보를 크롤링  
2. 크롤링한 데이터를 JSON으로 변환  
3. 해당 JSON을 프롬프트(`invest-by-perplexity-api2.md`)에 삽입  
4. Perplexity API 호출 → 투자 분석 보고서 & 블로그 초안 생성  
5. 결과를 **화면에 표시하고, 마크다운 파일(.md)로 다운로드** 가능  

---

## 2. 주요 사용자 시나리오 (User Stories)

### 2.1 투자자
- **입력**: 기업명/종목코드, 비교분기, 대상분기, Perplexity API 키  
- **출력**: 투자 분석 보고서 + 블로그 초안 (Markdown 파일 다운로드 가능)  
- **행동 플로우**:
  1. 웹 UI에서 기업명/종목코드 입력
  2. 분기 정보 입력
  3. API 키 입력
  4. [실행] 버튼 클릭
  5. 화면에 Perplexity 결과 확인
  6. [다운로드] 버튼으로 Markdown 파일 저장  

---

## 3. 기능 요구사항 (Functional Requirements)

### 3.1 입력 기능
- [ ] 기업명 또는 종목코드 입력 필드
- [ ] 비교 분기 입력 필드 (예: 2023-Q2)
- [ ] 대상 분기 입력 필드 (예: 2024-Q2)
- [ ] Perplexity API Key 입력 필드  

### 3.2 데이터 크롤링
- [ ] `naver-investing-crawling2.py` 활용
- [ ] 입력된 기업/종목코드 + 분기별 데이터를 크롤링
- [ ] 결과를 JSON 형태로 변환  

### 3.3 프롬프트 생성
- [ ] `invest-by-perplexity-api2.md`의 템플릿을 불러오기
- [ ] {financial-json} 위치에 크롤링 JSON 삽입
- [ ] 기업명, 날짜, 비교분기/대상분기를 반영하여 최종 프롬프트 구성  

### 3.4 Perplexity API 호출
- [ ] API 호출을 위한 프록시 서버 구성 (Node.js or FastAPI 권장)
- [ ] API 키는 사용자 입력값으로만 사용 (저장하지 않음)
- [ ] Perplexity 응답(JSON or text) 수신  

### 3.5 결과 출력 및 저장
- [ ] Perplexity 응답을 화면에 표시 (Markdown 렌더링 지원)
- [ ] [Markdown 파일 다운로드] 버튼 제공
- [ ] 파일명 규칙: `investment-report-[기업명]-[날짜].md`  

---

## 4. 비기능 요구사항 (Non-Functional Requirements)
- 로그인 불필요
- 데이터 저장 불필요 (stateless)
- API 키는 세션 내에서만 사용, 서버 저장 금지
- 빠른 응답속도 (5초 내 API 호출 완료)  

---

## 5. 시스템 아키텍처 (Architecture)

```mermaid
flowchart TD
    A[사용자 입력: 기업/분기/API 키] --> B[웹 UI]
    B --> C[백엔드 서버]
    C --> D[naver-investing-crawling2.py 실행]
    D --> E[재무데이터 JSON]
    E --> F[프롬프트 생성 (invest-by-perplexity-api2.md 기반)]
    F --> G[Perplexity API 호출 (프록시 서버)]
    G --> H[Perplexity 응답 수신]
    H --> I[화면 표시 (Markdown 렌더링)]
    I --> J[Markdown 파일 다운로드]
