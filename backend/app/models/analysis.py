from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class AnalysisRequest(BaseModel):
    stock_code: str = Field(..., description="네이버 증권 종목 코드")
    stock_name: str = Field(..., description="기업 이름")
    compare_periods: List[str] = Field(..., description="비교할 기간 리스트")
    api_key: str = Field(..., description="Perplexity API 키")
    model: Optional[str] = Field(None, description="Perplexity 모델명 (미지정 시 기본값)")
    market: Optional[str] = Field(None, description="시장 구분 (국내/해외)")
    market: Optional[str] = Field(
        "국내",
        description="분석 시장 구분: 국내 | 해외 (국내: KOSPI/KOSDAQ, 해외: 미국 등)"
    )

class AnalysisResponse(BaseModel):
    stock_code: str
    stock_name: str
    compare_periods: List[str]
    analysis: str
    financial_table: str
    citations: List[str]
    model: str
    usage: Dict
    created: int


class SaveMarkdownRequest(BaseModel):
    content: str
    filename: Optional[str] = None
