import os
import json
from io import StringIO
from typing import List, Dict, Tuple, Optional

import requests
try:
    import pandas as pd
except ImportError as e:
    raise ImportError("pandas가 설치되어 있지 않습니다. backend 디렉토리에서 'pip install -r requirements.txt' 실행 후 재시도하세요.") from e
try:
    from bs4 import BeautifulSoup
except ImportError as e:
    raise ImportError("beautifulsoup4가 설치되어 있지 않습니다. backend 디렉토리에서 'pip install -r requirements.txt' 실행 후 재시도하세요.") from e


class NaverFinancialCrawler:
    def __init__(self, save_dir: str = "temp") -> None:
        """네이버 증권 크롤러 초기화

        Args:
            save_dir: 임시 파일 저장 디렉토리
        """
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        # 마지막 오류 메시지 (최근 실패 원인 저장)
        self.last_error: Optional[str] = None

    async def fetch_financials(self, stock_code: str, compare_periods: List[str]) -> Tuple[Optional[str], Optional[List[Dict]]]:
        """
        네이버 증권에서 특정 기업의 재무제표를 가져와 CSV로 저장하고 JSON 형식으로 출력
        stock_code: 네이버 증권 종목 코드 (예: 삼성전자 005930)
        compare_periods: 비교할 기간 리스트 (예: ["2024.06", "2025.06"])
        """
        url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
        
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            # 재무제표 테이블 선택
            finance_html = soup.select_one("div.section.cop_analysis div.sub_section")
            if finance_html is None:
                raise ValueError("재무제표 영역을 찾을 수 없습니다 (페이지 구조 변경 가능성).")
            dfs = pd.read_html(StringIO(str(finance_html)), header=0)
        except Exception as e:
            self.last_error = str(e)
            print(f"[Error] 재무제표 추출 실패: {e}")
            return None, None

        # 데이터프레임 저장
        financial_df = dfs[0].dropna(axis=1, how="all")
        filename = os.path.join(self.save_dir, f"{stock_code}_financials.csv")
        financial_df.to_csv(filename, index=False, encoding="utf-8-sig")

        # JSON 형식으로 데이터 변환
        if compare_periods:
            json_result = self._convert_to_json_by_period(financial_df, compare_periods)
            return filename, json_result
        
        return filename, None

    def _convert_to_json_by_period(self, df: pd.DataFrame, compare_periods: List[str]) -> List[Dict]:
        """
        데이터프레임을 JSON 형식으로 변환
        df: 재무제표 데이터프레임
        compare_periods: 비교할 기간 리스트
        """
        result = []
        
        if len(df) < 1:
            print("[Error] 데이터가 충분하지 않습니다.")
            return []
        
        period_row = df.iloc[0]
        
        # 요청한 기간과 일치하는 컬럼 찾기
        matching_columns = []
        for period in compare_periods:
            for col_idx, col_value in enumerate(period_row):
                if str(col_value) == str(period):
                    col_name = df.columns[col_idx]
                    matching_columns.append((period, col_name))
                    break
            else:
                print(f"[Warning] 요청한 기간 '{period}'을 찾을 수 없습니다.")
        
        if not matching_columns:
            print(f"[Warning] 요청한 기간들이 데이터에 없습니다.")
            if len(df.columns) > 2:
                matching_columns = [
                    (period_row.iloc[1], df.columns[1]),
                    (period_row.iloc[2], df.columns[2])
                ]
        
        # 각 매칭된 컬럼에 대해 JSON 데이터 생성
        for i, (period_value, col_name) in enumerate(matching_columns):
            period_data = {}
            original_period = compare_periods[i] if i < len(compare_periods) else str(period_value)
            
            for index in range(2, len(df)):
                row = df.iloc[index]
                if pd.notna(row.iloc[0]) and pd.notna(row[col_name]):
                    key = f"{original_period} - {row.iloc[0]}"
                    try:
                        value_str = str(row[col_name]).replace(',', '').replace('원', '').replace('%', '').replace('억', '').strip()
                        try:
                            value = float(value_str) if '.' in value_str else int(float(value_str))
                            period_data[key] = int(value) if isinstance(value, float) and value.is_integer() else float(value)
                        except (ValueError, TypeError):
                            period_data[key] = str(row[col_name])
                    except Exception:
                        period_data[key] = str(row[col_name])
            
            if period_data:
                result.append(period_data)
        
        return result

    def cleanup(self):
        """임시 파일 정리"""
        import shutil
        if os.path.exists(self.save_dir):
            shutil.rmtree(self.save_dir)
