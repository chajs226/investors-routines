import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import requests

class PerplexityService:
    def __init__(self, api_key: str, model: Optional[str] = None):
        """Perplexity API 서비스 초기화

        Args:
            api_key: Perplexity API 키
            model: 사용할 모델명 (미지정 시 환경변수 PERPLEXITY_MODEL 또는 기본값)
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # 기본 온라인 접근 가능한 모델 (환경변수 PERPLEXITY_MODEL 로 재정의 가능)
        self.model = model or os.getenv("PERPLEXITY_MODEL", "sonar-pro")

    async def generate_investment_analysis(
        self,
        stock_name: str,
        financial_data: List[Dict],
        compare_periods: List[str],
        stock_code: Optional[str] = None,
        market: Optional[str] = None,
    ) -> Dict:
        """투자 분석 보고서 생성"""
        # 1. 템플릿 로드
        template_path = Path(__file__).parent.parent.parent.parent / "docs" / "invest-by-perplexity-api2.md"
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        # 2. 재무데이터 JSON 직렬화
        financial_json = json.dumps(financial_data, ensure_ascii=False, indent=2)

        # 3. 프롬프트 구성
        prompt = (
            template
            .replace("[company name]", stock_name)
            .replace("{financial-json}", financial_json)
            .replace("YYYY-MM-DD", datetime.now().strftime("%Y-%m-%d"))
        )

        # 시장/종목코드에 따른 모호성 제거 컨텍스트 추가
        market_hint = (market or "국내").strip()
        stock_code_hint = stock_code or ""
        prompt += (
            "\n\n[분석 컨텍스트]\n"
            f"시장: {market_hint}\n"
            f"종목코드: {stock_code_hint}\n"
            "회사명이 모호할 경우 다음 원칙을 따르세요:\n"
            "- 시장=국내: KOSPI/KOSDAQ 상장 한국 기업을 우선으로 식별하고 분석합니다.\n"
            "- 시장=해외: 미국 등 해외 증시의 기업을 대상으로 분석합니다.\n"
            "- 종목코드가 제공된 경우 해당 종목코드를 최우선으로 기업을 특정합니다.\n"
        )

        # 4. 전체 프롬프트 로그 (전체 길이 출력)
        print(f"[Prompt Log] ===== BEGIN PROMPT (length={len(prompt)}) =====")
        print(prompt)
        print("[Prompt Log] ===== END PROMPT =====")

        # 5. API 페이로드
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert investment analyst. Provide comprehensive, data-driven analysis with clear recommendations."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.2,
            "top_p": 0.9,
            "return_citations": True
        }

        # 6. 호출 & 예외 처리
        try:
            print(f"[Perplexity] Sending request to model={self.model}, timeout=300s...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=300  # extended to 300s (5 minutes)
            )
            print(f"[Perplexity] Received response: status={response.status_code} body={response.text[:500]}")
            try:
                data = response.json()
            except Exception:
                data = {"raw": response.text}
            if response.status_code == 400:
                message = data.get("error", {}).get("message") if isinstance(data, dict) else None
                raise ValueError(message or "잘못된 요청 (400)")
            if response.status_code == 401:
                raise PermissionError("Perplexity API 인증 실패 (401) - API 키를 확인하세요.")
            if response.status_code == 429:
                raise RuntimeError("Perplexity API rate limit 초과 (429) - 잠시 후 재시도")
            if response.status_code >= 500:
                raise RuntimeError(f"Perplexity 서버 오류 ({response.status_code})")
            return data
        except (ValueError, PermissionError, RuntimeError):
            raise
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Perplexity API 네트워크 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"Perplexity API 알 수 없는 오류: {e}")

    def format_analysis_response(self, api_response: Dict) -> Dict:
        """Perplexity API 응답을 단일 dict 형태로 정리"""
        try:
            # 응답 구조 방어적 파싱
            if "choices" not in api_response:
                # choices가 없으면 원본 응답 전체를 로그하고 오류 상세 전달
                print(f"[Perplexity Response Error] Missing 'choices' key. Full response: {json.dumps(api_response, ensure_ascii=False, indent=2)}")
                
                # error 필드가 있으면 명확한 메시지 반환
                if "error" in api_response:
                    error_info = api_response["error"]
                    error_msg = error_info.get("message", str(error_info))
                    raise ValueError(f"Perplexity API 오류: {error_msg}")
                
                # 그 외에는 응답 전체를 텍스트로 반환
                raise ValueError(f"Perplexity API 응답 형식 오류: 'choices' 키가 없습니다. 응답: {api_response}")
            
            content = api_response["choices"][0]["message"]["content"]
            citations = api_response.get("citations", [])
            return {
                "analysis": content,
                "citations": citations,
                "model": api_response.get("model", ""),
                "usage": api_response.get("usage", {}),
                "created": api_response.get("created", 0)
            }
        except (ValueError, KeyError) as e:
            # 이미 명확한 메시지가 있으면 그대로 전달
            if isinstance(e, ValueError):
                raise
            # KeyError는 상세 응답과 함께 ValueError로 변환
            print(f"[Response Parse Error] {e}. Response keys: {list(api_response.keys())}")
            raise ValueError(f"응답 파싱 실패: {e}. 받은 키: {list(api_response.keys())}")
        except Exception as e:
            raise Exception(f"응답 처리 중 알 수 없는 오류: {e}")
