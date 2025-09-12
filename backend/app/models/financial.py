from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class FinancialRequest(BaseModel):
    stock_code: str = Field(..., description="네이버 증권 종목 코드 (예: 005930)")
    compare_periods: List[str] = Field(..., description="비교할 기간 리스트 (예: ['2024.06', '2025.06'])")
    stock_name: Optional[str] = Field(None, description="기업 이름 (예: 삼성전자)")

class FinancialResponse(BaseModel):
    stock_code: str
    stock_name: Optional[str]
    compare_periods: List[str]
    financial_data: List[Dict]
    csv_path: Optional[str]
