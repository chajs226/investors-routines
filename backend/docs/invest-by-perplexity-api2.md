## Perplexity 최적화 프롬프트 1: AI 기반 투자 분석 보고서 및 블로그 초안 생성

**Core Intent:** To leverage Perplexity's web-crawling and analysis capabilities to generate a comprehensive, data-driven investment analysis report on a specific company and its industry, incorporating the latest news, financial data, competitor movements, and key financial & market metrics from an investor's perspective.

**Prompt:**

[Request]
As an investment analyst, conduct a thorough investigation and generate a comprehensive investment analysis report for **[company name]** . Focus on the latest available information up to today, **YYYY-MM-DD**.

[Information Gathering & Analysis Requirements]

1.  **Latest Corporate & Industry Trends:**
    * 외부자료 및 웹 검색 결과를 기반으로 작성합니다.
    *   **Significant Corporate News (Last 14 Days):** Identify and summarize the most impactful corporate news for [company name]. Include details on public disclosures, earnings reports, major announcements, or new business ventures.
    *   **Key Industry Trends & Policy Changes:** What are the most recent and relevant trends, technological advancements, or regulatory/policy changes affecting [company name]'s industry (e.g., semiconductors, EV batteries, biotechnology)?

2.  **Impactful Issues Analysis:**
    * 외부자료 및 웹 검색 결과를 기반으로 작성합니다.
    *   **Short-term & Long-term Issues:** Detail the most significant short-term (next 3-6 months) and long-term (1-3 years) issues currently impacting [company name].
    *   **Financial Impact:** For each identified issue, explain its potential positive or negative influence on the company's revenue, profitability, and stock price. Quantify the impact where recent data is available.

3.  **Competitor Landscape & Impact:**
    * 외부자료 및 웹 검색 결과를 기반으로 작성합니다.
    *   **Key Competitor Updates (Up to 2):** Identify [company name]'s two main direct competitors. Summarize their most notable recent news, strategic initiatives, or performance changes.
    *   **Competitive Impact on [company name]:** Analyze how these competitor trends and actions are expected to impact [company name]'s market position, financial performance, and future outlook.

4.  **핵심 재무 및 시장 지표 (Key Financial & Market Metrics):**
{financial-json}
    * 단위 변환을 하지 말고 json 파일에 표기된 숫자를 그대로 사용하여 표로 작성합니다.
    * 각 지표의 현재 값과 추세가 투자 매력도에 미치는 의미를 간략히 설명합니다.
    *   **지표 분석:** 각 지표의 현재 값과 추세가 [company name]의 투자 매력도에 어떤 의미를 가지는지 간략하게 설명합니다.

5.  **Overall Investment Analysis & Recommendations:**
    *   **Concise Summary:** Provide a 1-2 sentence executive summary outlining the most critical findings and their overall positive or negative implications for [company name].
    *   **Positive & Negative Factors:** Clearly list and explain the top 3-5 positive factors suggesting potential for growth and the top 3-5 negative factors/risks that could negatively affect the company's value, **재무 지표 분석 결과도 함께 고려하여 포함합니다.**
    *   **Key Data-Driven Insights:** Extract and highlight specific, quantifiable metrics or trends from your findings (e.g., recent stock price movement, earnings per share (EPS) changes, market share shifts, **그리고 위에 분석된 재무 및 시장 지표들 중 핵심적인 것들을 포함**). If exact numbers aren't found, describe the *direction and magnitude* of the trend.
    *   **Investor Actionable Recommendations:** Based on this comprehensive analysis, what specific steps should an investor consider? What key indicators, future events (e.g., next earnings call, product launch), or macroeconomic factors, **그리고 핵심 재무 지표의 변화**를 모니터링해야 하는지 구체적으로 제시합니다.

[Information Gathering & Analysis Requirements's Output Format]

*   Present the report in a structured, professional format with clear headings and bullet points for readability.
*   **Crucially, cite all sources used at the end of each section or as footnotes/endnotes.** (Perplexity will do this automatically, but explicitly requesting it reinforces the need for traceable information).
*   Avoid verbose introductions; get straight to the analysis.

지시사항:
1) 모든 설명과 표, 제목을 자연스러운 한국어로 작성하세요.
2) 가독성을 위해 소제목을 활용하고, 문단이 끝나면 빈줄을 추가해서 구분해주세요.
3) 내용의 출처는 문장의 끝에 링크로 연결해주세요.