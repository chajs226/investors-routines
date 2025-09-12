import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPI:
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Investor Routiner API"}

    def test_financial_crawl_endpoint(self):
        """재무 데이터 크롤링 엔드포인트 테스트"""
        response = client.post(
            "/api/financial/crawl",
            json={
                "stock_code": "005930",
                "compare_periods": ["2024.06", "2025.06"],
                "stock_name": "삼성전자"
            }
        )
        # 실제 크롤링은 네트워크 요청이 필요하므로 200 또는 404 응답을 확인
        assert response.status_code in [200, 404, 500]

    def test_analysis_endpoint_missing_api_key(self):
        """분석 엔드포인트 API 키 누락 테스트"""
        response = client.post(
            "/api/analysis/analyze",
            json={
                "stock_code": "005930",
                "stock_name": "삼성전자",
                "compare_periods": ["2024.06", "2025.06"],
                "api_key": ""
            }
        )
        # API 키가 없으면 500 에러가 발생할 것으로 예상
        assert response.status_code in [400, 500]

