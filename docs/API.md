# API 문서

## 개요
투자 분석 자동화 서비스의 API 엔드포인트에 대한 문서입니다.

## 기본 정보
- Base URL: `http://localhost:8000`
- API 버전: 1.0.0
- 인증: API 키 기반 (Perplexity API)

## 엔드포인트

### 1. 루트 엔드포인트
```
GET /
```
서비스 상태를 확인합니다.

**응답:**
```json
{
  "message": "Investor Routiner API"
}
```

### 2. 재무 데이터 크롤링
```
POST /api/financial/crawl
```
네이버 증권에서 기업의 재무 데이터를 크롤링합니다.

**요청 본문:**
```json
{
  "stock_code": "005930",
  "compare_periods": ["2024.06", "2025.06"],
  "stock_name": "삼성전자"
}
```

**응답:**
```json
{
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "compare_periods": ["2024.06", "2025.06"],
  "financial_data": [
    {
      "2024.06 - 매출액": 1000000,
      "2024.06 - 영업이익": 100000
    },
    {
      "2025.06 - 매출액": 1100000,
      "2025.06 - 영업이익": 110000
    }
  ],
  "csv_path": "temp/005930_financials.csv"
}
```

### 3. 투자 분석 보고서 생성
```
POST /api/analysis/analyze
```
재무 데이터를 기반으로 Perplexity API를 통해 투자 분석 보고서를 생성합니다.

**요청 본문:**
```json
{
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "compare_periods": ["2024.06", "2025.06"],
  "api_key": "YOUR_PERPLEXITY_API_KEY"
}
```

**응답:**
```json
{
  "stock_code": "005930",
  "stock_name": "삼성전자",
  "compare_periods": ["2024.06", "2025.06"],
  "analysis": "# 투자 분석 보고서\n\n## 개요\n...",
  "citations": [
    "https://example.com/news1",
    "https://example.com/news2"
  ],
  "model": "llama-3.1-sonar-small-128k-online",
  "usage": {
    "prompt_tokens": 1000,
    "completion_tokens": 2000,
    "total_tokens": 3000
  },
  "created": 1640995200
}
```

## 에러 응답

### 400 Bad Request
```json
{
  "detail": "요청 데이터가 올바르지 않습니다."
}
```

### 404 Not Found
```json
{
  "detail": "재무 데이터를 찾을 수 없습니다."
}
```

### 500 Internal Server Error
```json
{
  "detail": "서버 내부 오류가 발생했습니다."
}
```

## 사용 예시

### cURL 예시
```bash
# 재무 데이터 크롤링
curl -X POST "http://localhost:8000/api/financial/crawl" \
     -H "Content-Type: application/json" \
     -d '{
       "stock_code": "005930",
       "compare_periods": ["2024.06", "2025.06"],
       "stock_name": "삼성전자"
     }'

# 투자 분석 보고서 생성
curl -X POST "http://localhost:8000/api/analysis/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "stock_code": "005930",
       "stock_name": "삼성전자",
       "compare_periods": ["2024.06", "2025.06"],
       "api_key": "YOUR_API_KEY"
     }'
```

### Python 예시
```python
import requests

# 재무 데이터 크롤링
response = requests.post(
    "http://localhost:8000/api/financial/crawl",
    json={
        "stock_code": "005930",
        "compare_periods": ["2024.06", "2025.06"],
        "stock_name": "삼성전자"
    }
)
data = response.json()

# 투자 분석 보고서 생성
response = requests.post(
    "http://localhost:8000/api/analysis/analyze",
    json={
        "stock_code": "005930",
        "stock_name": "삼성전자",
        "compare_periods": ["2024.06", "2025.06"],
        "api_key": "YOUR_API_KEY"
    }
)
analysis = response.json()
```

## 주의사항
1. API 키는 절대 서버에 저장되지 않습니다.
2. 모든 요청은 stateless로 처리됩니다.
3. 크롤링 결과는 임시 파일로 저장되며, 요청 완료 후 자동으로 정리됩니다.
4. Perplexity API 사용량에 따라 비용이 발생할 수 있습니다.
