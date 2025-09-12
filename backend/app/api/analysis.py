from fastapi import APIRouter, HTTPException
from typing import Optional
from ..models.analysis import AnalysisRequest, AnalysisResponse, SaveMarkdownRequest
from ..services.naver_crawler import NaverFinancialCrawler
from ..services.perplexity_service import PerplexityService
import pandas as pd
from pathlib import Path
import os

router = APIRouter()
crawler = NaverFinancialCrawler(save_dir="temp")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_investment(request: AnalysisRequest, model: Optional[str] = None):
    """
    기업 재무정보를 크롤링하고 Perplexity API를 통해 투자 분석 보고서 생성
    """
    # 1. 재무 데이터 크롤링 (시장 구분)
    market = (request.market or "국내").strip()
    if market == "국내":
        csv_path, financial_data = await crawler.fetch_financials(
            request.stock_code,
            request.compare_periods
        )
    else:
        # 해외 시장: 현재는 네이버 크롤러가 국내만 지원. 임시로 재무데이터 없이 진행.
        csv_path, financial_data = None, []

    if market == "국내" and not financial_data:
        # 상세 오류 파악 (예: lxml 미설치)
        last_error = getattr(crawler, "last_error", None)
        if last_error and "lxml" in last_error.lower():
            raise HTTPException(
                status_code=500,
                detail="lxml 라이브러리가 설치되어 있지 않습니다. backend 디렉토리에서 'pip install lxml' 실행 후 다시 시도하세요."
            )
        raise HTTPException(status_code=404, detail="재무 데이터를 찾을 수 없습니다.")

    # 2. Perplexity API를 통한 분석
    # 우선순위: 쿼리 파라미터 model > 요청 body model > 환경변수
    effective_model = model or request.model
    perplexity_service = PerplexityService(request.api_key, model=effective_model)
    try:
        api_response = await perplexity_service.generate_investment_analysis(
            request.stock_name,
            financial_data,
            request.compare_periods,
                stock_code=request.stock_code,
                market=request.market,
        )
    except ValueError as e:  # 잘못된 요청 (모델 등)
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:  # 인증 오류
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:  # 서버 / 네트워크 / rate limit 등
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:  # 기타 예외
        raise HTTPException(status_code=500, detail=f"예상치 못한 오류: {e}")

    # 3. 응답 정리
    formatted_response = perplexity_service.format_analysis_response(api_response)

    # 재무 데이터 표 생성 (Markdown)
    try:
        # financial_data 는 period별 dict 리스트 -> key: "기간 - 항목" 형식
        # 이를 기간/항목으로 재구조화
        rows = {}
        periods = set()
        for entry in financial_data:
            for k, v in entry.items():
                if ' - ' in k:
                    period, metric = k.split(' - ', 2)
                else:
                    # fallback
                    period, metric = '기간', k
                periods.add(period)
                rows.setdefault(metric, {})[period] = v
        periods = sorted(list(periods))
        df = pd.DataFrame.from_dict(rows, orient='index')[periods]
        df.index.name = '지표'
        financial_table_md = df.reset_index().to_markdown(index=False)
    except Exception:
        financial_table_md = "(재무 표 생성 실패)"

    return AnalysisResponse(
        stock_code=request.stock_code,
        stock_name=request.stock_name,
        compare_periods=request.compare_periods,
    analysis=formatted_response["analysis"],
    financial_table=financial_table_md,
        citations=formatted_response["citations"],
        model=formatted_response["model"],
        usage=formatted_response["usage"],
        created=formatted_response["created"]
    )


@router.post("/save_markdown")
async def save_markdown(payload: SaveMarkdownRequest):
    """프로젝트 루트 하위 outputs 디렉토리에 마크다운 저장"""
    try:
        # 서버 저장 활성 여부 (기본: 활성). 비활성화 시 저장하지 않고 안내만 반환
        save_enabled = os.getenv("ENABLE_SERVER_SAVE", "true").lower() in ("1", "true", "yes", "on")
        if not save_enabled:
            return {"saved": False, "path": None, "disabled": True, "message": "Server-side saving disabled by config."}

        # backend/app/api/analysis.py 기준으로 상위 3단계를 올라가 프로젝트 루트 추정
        project_root = Path(__file__).resolve().parents[3]
        outputs_dir = project_root / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)

        # 파일명 결정
        filename = payload.filename or "investment-report.md"
        # 간단한 파일명 보호
        safe_name = filename.replace("../", "").replace("..\\", "").strip()
        if not safe_name.endswith(".md"):
            safe_name += ".md"

        target = outputs_dir / safe_name
        target.write_text(payload.content, encoding="utf-8")
        rel = target.relative_to(project_root)
        return {"saved": True, "path": str(rel), "message": "Saved to outputs"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")
