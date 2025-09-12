import pytest
import pandas as pd
from app.services.naver_crawler import NaverFinancialCrawler

class TestNaverFinancialCrawler:
    def test_init(self):
        """크롤러 초기화 테스트"""
        crawler = NaverFinancialCrawler(save_dir="test_temp")
        assert crawler.save_dir == "test_temp"

    def test_convert_to_json_by_period(self):
        """JSON 변환 테스트"""
        crawler = NaverFinancialCrawler()
        
        # 테스트용 데이터프레임 생성
        data = {
            '항목': ['기간', 'IFRS연결', '매출액', '영업이익'],
            '2024.06': ['2024.06', 'IFRS연결', '1000000', '100000'],
            '2025.06': ['2025.06', 'IFRS연결', '1100000', '110000']
        }
        df = pd.DataFrame(data)
        
        result = crawler._convert_to_json_by_period(df, ['2024.06', '2025.06'])
        
        assert len(result) == 2
        assert '2024.06 - 매출액' in result[0]
        assert '2025.06 - 매출액' in result[1]

