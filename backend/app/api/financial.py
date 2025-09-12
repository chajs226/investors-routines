from fastapi import APIRouter, HTTPException
from ..models.financial import FinancialRequest, FinancialResponse
from ..services.naver_crawler import NaverFinancialCrawler

router = APIRouter()
crawler = NaverFinancialCrawler(save_dir="temp")

@router.post("/crawl", response_model=FinancialResponse)
async def crawl_financial_data(request: FinancialRequest):
    """
    네이버 증권에서 기업 재무정보를 크롤링하여 반환
    """
    try:
        csv_path, financial_data = await crawler.fetch_financials(
            request.stock_code,
            request.compare_periods
        )
        
        if not financial_data:
            raise HTTPException(status_code=404, detail="재무 데이터를 찾을 수 없습니다.")
        
        return FinancialResponse(
            stock_code=request.stock_code,
            stock_name=request.stock_name,
            compare_periods=request.compare_periods,
            financial_data=financial_data,
            csv_path=csv_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
