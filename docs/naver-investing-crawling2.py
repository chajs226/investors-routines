import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import json
from io import StringIO

def fetch_naver_financials(stock_code: str, compare_periods: list = None, save_dir: str = "."):
    """
    네이버 증권에서 특정 기업의 재무제표를 가져와 CSV로 저장하고 JSON 형식으로 출력
    stock_code: 네이버 증권 종목 코드 (예: 삼성전자 005930)
    compare_periods: 비교할 기간 리스트 (예: ["2024.06", "2025.06"]) - 두 번째 행의 값 기준
    save_dir: CSV 저장 폴더
    """
    url = f"https://finance.naver.com/item/main.nhn?code={stock_code}"
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # 재무제표 테이블 선택
    try:
        finance_html = soup.select_one("div.section.cop_analysis div.sub_section")
        dfs = pd.read_html(StringIO(str(finance_html)), header=0)
    except Exception as e:
        print(f"[Error] 재무제표 추출 실패: {e}")
        return None, None

    # 데이터프레임 저장
    financial_df = dfs[0].dropna(axis=1, how="all")
    filename = os.path.join(save_dir, f"{stock_code}_financials.csv")
    financial_df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"[Info] 재무제표 CSV 저장 완료: {filename}")
    
    # JSON 형식으로 데이터 변환 (두 번째 행 기준으로 컬럼 매칭)
    if compare_periods:
        json_result = convert_to_json_by_period(financial_df, compare_periods)
        return filename, json_result
    
    return filename, None

def convert_to_json_by_period(df, compare_periods):
    """
    데이터프레임을 JSON 형식으로 변환 (첫 번째 행의 기간 정보 기준)
    df: 재무제표 데이터프레임
    compare_periods: 비교할 기간 리스트 (첫 번째 행의 값 기준)
    """
    result = []
    
    # 첫 번째 행(index=0)에서 기간 정보 가져오기
    if len(df) < 1:
        print("[Error] 데이터가 충분하지 않습니다.")
        return []
    
    period_row = df.iloc[0]  # 첫 번째 행
    print(f"[Info] 사용 가능한 기간: {list(period_row)}")
    
    # 요청한 기간과 일치하는 컬럼 찾기
    matching_columns = []
    for period in compare_periods:
        for col_idx, col_value in enumerate(period_row):
            if str(col_value) == str(period):
                col_name = df.columns[col_idx]
                matching_columns.append((period, col_name))
                print(f"[Info] 기간 '{period}'이 컬럼 '{col_name}'과 매칭됨")
                break
        else:
            print(f"[Warning] 요청한 기간 '{period}'을 찾을 수 없습니다.")
    
    if not matching_columns:
        print(f"[Warning] 요청한 기간들이 데이터에 없습니다.")
        # 기본값으로 첫 번째와 두 번째 데이터 컬럼 사용 (첫 번째 컬럼은 항목명이므로 제외)
        if len(df.columns) > 2:
            matching_columns = [
                (period_row.iloc[1], df.columns[1]),
                (period_row.iloc[2], df.columns[2])
            ]
    
    # 각 매칭된 컬럼에 대해 JSON 데이터 생성
    for i, (period_value, col_name) in enumerate(matching_columns):
        period_data = {}
        
        # 입력값에서 해당하는 원래 요청 기간 찾기
        original_period = compare_periods[i] if i < len(compare_periods) else str(period_value)
        
        # 세 번째 행부터 실제 재무 데이터 시작 (첫 번째: 기간, 두 번째: IFRS연결, 세 번째: 매출액 등)
        for index in range(2, len(df)):  # 세 번째 행부터 (매출액, 영업이익 등)
            row = df.iloc[index]
            if pd.notna(row.iloc[0]) and pd.notna(row[col_name]):  # 항목명과 값이 모두 존재하는 경우
                key = f"{original_period} - {row.iloc[0]}"  # "2025.06 - 매출액" 형식 (입력값 사용)
                try:
                    # 숫자 값으로 변환 시도
                    value_str = str(row[col_name]).replace(',', '').replace('원', '').replace('%', '').replace('억', '').strip()
                    try:
                        # int나 float로 변환 가능한지 확인
                        value = float(value_str) if '.' in value_str else int(float(value_str))
                        # JSON 직렬화를 위해 Python native 타입으로 변환
                        period_data[key] = int(value) if isinstance(value, float) and value.is_integer() else float(value)
                    except (ValueError, TypeError):
                        # 숫자로 변환할 수 없으면 문자열로 저장
                        period_data[key] = str(row[col_name])
                except Exception:
                    period_data[key] = str(row[col_name])
        
        if period_data:  # 데이터가 있는 경우만 추가
            result.append(period_data)
    
    return result

def generate_perplexity_prompt(stock_name: str, csv_filename: str, rulebook_name: str = "rulebook.txt"):
    """
    Perplexity에 업로드할 프롬프트 템플릿 생성
    stock_name: 기업 이름 (예: 삼성전자)
    csv_filename: 수집한 CSV 파일 이름
    rulebook_name: 룰북 파일 이름
    """
    prompt = f"""
업로드한 파일 {csv_filename} 는 {stock_name}의 네이버 증권 재무제표 데이터를 기준으로 합니다.
업로드한 룰북 {rulebook_name}에 정의된 출력 포맷과 규칙을 반드시 준수하세요.

1. {stock_name}의 최근 3년간 매출, 영업이익, 순이익, 주요 투자 지표(PER, PBR, ROE 등)를 분석하고 요약합니다.
2. 최신 뉴스, 산업 동향 및 리스크/기회를 Perplexity 검색을 통해 조사하여 출처를 명확히 포함합니다.
3. 재무 데이터와 뉴스/리서치를 종합하여 투자 관점에서 분석 내용을 작성합니다.
4. 룰북에 정의된 출력 포맷을 벗어나지 않도록 주의합니다.

출력은 반드시 Markdown 또는 CSV/표 형식으로 구조화하여 작성합니다.
"""
    print(f"[Info] Perplexity용 프롬프트 생성 완료")
    return prompt.strip()

def update_md_template_with_json(json_data, stock_name: str, template_file: str = "invest-by-perplexity-api2.md"):
    """MD 템플릿에 재무 JSON 삽입.

    우선순위:
    1) {financial-json} 플레이스홀더가 있으면 교체
    2) 없으면 '4.'로 시작하고 '핵심 재무 및 시장 지표' 문자열이 포함된 제목 바로 아래에 삽입
    3) 그래도 못 찾으면 파일 끝에 '## 재무 지표' 섹션을 새로 만들어 삽입
    """
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            template_content = f.read()

        print(f"[Debug] 템플릿 로드 (length={len(template_content)})")

        json_block = "```json\n" + json.dumps(json_data, ensure_ascii=False, indent=2) + "\n```"

        updated_content = template_content
        inserted = False

        # 1) 플레이스홀더 직접 교체
        if "{financial-json}" in updated_content:
            updated_content = updated_content.replace("{financial-json}", json_block)
            print("[Info] {financial-json} 플레이스홀더 교체 완료")
            inserted = True
        else:
            print("[Warn] {financial-json} 플레이스홀더 없음. 섹션 제목 기반 삽입 시도")
            # 2) 섹션 4 제목 찾기
            lines = updated_content.splitlines()
            for i, line in enumerate(lines):
                normalized = line.replace(" ", "")
                if line.strip().startswith("4.") and "핵심 재무" in line:
                    # 제목 바로 다음 빈 줄 위치 찾기
                    insert_index = i + 1
                    # 연속된 제목/공백 지나가며 실제 삽입 위치 결정
                    while insert_index < len(lines) and lines[insert_index].strip() == "":
                        insert_index += 1
                    # JSON 블록 삽입 (제목 바로 아래 공백 한 줄 포함)
                    lines.insert(insert_index, json_block)
                    updated_content = "\n".join(lines)
                    print(f"[Info] 섹션 4 제목 아래 JSON 삽입 (line {i})")
                    inserted = True
                    break

        # 3) 모든 시도 실패 시 파일 끝에 새 섹션 추가
        if not inserted:
            print("[Warn] 섹션 4 제목도 찾지 못함. 파일 끝에 새 섹션 추가")
            updated_content += "\n\n## 재무 지표 (자동 삽입)\n" + json_block + "\n"

        # 회사명 치환
        updated_content = updated_content.replace("[company name]", stock_name)

        output_filename = f"{stock_name}_investment_analysis_prompt.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"[Info] 업데이트된 MD 파일 저장 완료: {output_filename}")
        return output_filename
    except FileNotFoundError:
        print(f"[Error] 템플릿 파일을 찾을 수 없습니다: {template_file}")
        return None
    except Exception as e:
        print(f"[Error] MD 템플릿 업데이트 실패: {e}")
        return None

# -------------------------------
# 사용 예시
# -------------------------------
if __name__ == "__main__":
    # 1. 분석할 기업 정보
    stock_code = "034730"  # SK 종목코드
    stock_name = "SK"
    rulebook_file = "rulebook.txt"
    
    # 2. 비교할 기간 입력 (두 번째 행의 값 기준)
    compare_periods = ["2024.06", "2025.06"]  # 예시: 2024년 6월과 2025년 6월 비교
    
    print(f"[Info] 비교 대상 기간: {compare_periods}")

    # 3. 재무제표 크롤링 및 CSV 생성
    csv_file, json_result = fetch_naver_financials(stock_code, compare_periods)

    if csv_file:
        # 4. JSON 결과 출력
        if json_result:
            print("\n[Info] JSON 형식 결과:")
            print(json.dumps(json_result, ensure_ascii=False, indent=2))
            
            # JSON 파일로도 저장
            with open(f"{stock_code}_financial_comparison.json", "w", encoding="utf-8") as f:
                json.dump(json_result, f, ensure_ascii=False, indent=2)
            print(f"[Info] JSON 파일 저장 완료: {stock_code}_financial_comparison.json")
            
            # MD 템플릿에 JSON 데이터 삽입
            updated_md_file = update_md_template_with_json(json_result, stock_name)
        
        # 5. Perplexity 프롬프트 생성
        prompt_text = generate_perplexity_prompt(stock_name, csv_file, rulebook_file)

        # 6. 파일과 함께 Perplexity UI에 업로드 & 프롬프트 붙여 넣기
        # (자동 업로드는 현재 지원되지 않음)
        with open("perplexity_prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt_text)
        print("[Info] perplexity_prompt.txt 생성 완료. Perplexity에 업로드 후 사용하세요.")
