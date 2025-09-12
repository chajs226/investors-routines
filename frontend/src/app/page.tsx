'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

interface AnalysisResponse {
  stock_code: string;
  stock_name: string;
  compare_periods: string[];
  analysis: string;
  financial_table: string;
  citations: string[];
  model: string;
  usage: any;
  created: number;
}

export default function Home() {
  const [formData, setFormData] = useState({
    stockCode: '',
    stockName: '',
    comparePeriods: ['', ''],
    apiKey: '',
  market: '국내',
  model: 'sonar-reasoning-pro' // 기본값, 사용자가 수정 가능
  });
  const [isLoading, setIsLoading] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(id);
  }, [toast]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePeriodChange = (index: number, value: string) => {
    const newPeriods = [...formData.comparePeriods];
    newPeriods[index] = value;
    setFormData(prev => ({
      ...prev,
      comparePeriods: newPeriods
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setAnalysis(null);

  const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000); // 180초 타임아웃
    try {
      const query = formData.model ? `?model=${encodeURIComponent(formData.model)}` : '';
      const response = await axios.post(
        `http://localhost:8000/api/analysis/analyze${query}`,
        {
          stock_code: formData.stockCode,
          stock_name: formData.stockName,
          compare_periods: formData.comparePeriods.filter(p => p.trim() !== ''),
          market: formData.market,
          api_key: formData.apiKey
        },
        { signal: controller.signal }
      );
      setAnalysis(response.data);
    } catch (err: any) {
      if (axios.isCancel(err)) {
    setError('요청이 시간 초과되었습니다. (180초) 모델/기간을 조정하거나 다시 시도하세요.');
      } else if (err.name === 'AbortError') {
        setError('요청이 취소되었습니다.');
      } else {
        setError(err.response?.data?.detail || '분석 중 오류가 발생했습니다.');
      }
    } finally {
      clearTimeout(timeoutId);
      setIsLoading(false);
    }
  };

  const downloadMarkdown = async () => {
    if (!analysis) return;

    const content = `# ${analysis.stock_name} 투자 분석 보고서

## 분석 정보
- 종목코드: ${analysis.stock_code}
- 비교기간: ${analysis.compare_periods.join(', ')}
- 분석일시: ${new Date(analysis.created * 1000).toLocaleString()}

## 분석 내용

${analysis.analysis}

## 참고 자료
${analysis.citations.map(citation => `- ${citation}`).join('\n')}
`;

    // 서버에 저장 (프로젝트 루트 /outputs)
    try {
      const filename = `investment-report-${analysis.stock_name}-${new Date().toISOString().split('T')[0]}.md`;
      const res = await axios.post('http://localhost:8000/api/analysis/save_markdown', {
        content,
        filename
      });
      if (res.data?.saved) {
        setToast('서버에 저장 완료: ' + (res.data?.path || 'outputs/' + filename));
      } else if (res.data?.disabled) {
        setToast('서버 저장 비활성화 상태입니다. 로컬 다운로드만 수행합니다.');
      }
    } catch (e) {
      setToast('서버 저장 실패. 로컬 다운로드만 수행합니다.');
    }

    // 로컬 다운로드도 함께 수행
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `investment-report-${analysis.stock_name}-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
              기업 분석 지원 서비스
          </h1>
  model: 'sonar-deep-research' // 기본값, 사용자가 수정 가능
          <p className="text-lg text-gray-600">
            기업 재무정보와 최신 뉴스를 기반으로 투자 분석 보고서를 자동 생성합니다
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 시장 구분을 최상단으로 이동 */}
            <div>
              <label htmlFor="market" className="block text-sm font-medium text-gray-700 mb-2">
                시장 구분
              </label>
              <select
                id="market"
                name="market"
                value={formData.market}
                onChange={handleSelectChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              >
                <option value="국내">국내</option>
                <option value="해외">해외</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">국내 선택 시 KOSPI/KOSDAQ 상장 기업을 우선으로 분석합니다.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="stockCode" className="block text-sm font-medium text-gray-700 mb-2">
                  종목코드
                </label>
                <input
                  type="text"
                  id="stockCode"
                  name="stockCode"
                  value={formData.stockCode}
                  onChange={handleInputChange}
                  placeholder="예: 005930"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="stockName" className="block text-sm font-medium text-gray-700 mb-2">
                  기업명
                </label>
                <input
                  type="text"
                  id="stockName"
                  name="stockName"
                  value={formData.stockName}
                  onChange={handleInputChange}
                  placeholder="예: 삼성전자"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>

            

            <div>
              <h3 className="text-md font-semibold text-gray-900 mb-3">재무 데이터 비교</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="comparePeriod1" className="block text-sm font-medium text-gray-700 mb-2">
                  From:분기
                </label>
                <input
                  type="text"
                  id="comparePeriod1"
                  value={formData.comparePeriods[0]}
                  onChange={(e) => handlePeriodChange(0, e.target.value)}
                  placeholder="예: 2024.06"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label htmlFor="comparePeriod2" className="block text-sm font-medium text-gray-700 mb-2">
                  To:분기
                </label>
                <input
                  type="text"
                  id="comparePeriod2"
                  value={formData.comparePeriods[1]}
                  onChange={(e) => handlePeriodChange(1, e.target.value)}
                  placeholder="예: 2025.06"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              </div>
            </div>

            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
                Perplexity API 키
              </label>
              <input
                type="password"
                id="apiKey"
                name="apiKey"
                value={formData.apiKey}
                onChange={handleInputChange}
                placeholder="Perplexity API 키를 입력하세요"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-2">
                모델 (선택)
              </label>
              <input
                type="text"
                id="model"
                name="model"
                value={formData.model}
                onChange={handleInputChange}
                placeholder="예: llama-3.1-sonar-small-128k-online"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">빈칸이면 서버 기본 모델을 사용합니다.</p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '분석 중...' : '분석 시작'}
            </button>
          </form>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-8">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">오류 발생</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {toast && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-4 py-2 rounded shadow-lg z-50">
            {toast}
          </div>
        )}

        {analysis && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {analysis.stock_name} 투자 분석 보고서
              </h2>
              <button
                onClick={downloadMarkdown}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                마크다운 다운로드
              </button>
            </div>

            <div className="prose max-w-none space-y-8">
              <section>
                <h3 className="text-xl font-semibold mb-4">재무 지표 표</h3>
                <div className="overflow-auto border rounded-md bg-gray-50 p-3">
                  <ReactMarkdown>{'\n' + analysis.financial_table + '\n'}</ReactMarkdown>
                </div>
              </section>
              <section>
                <h3 className="text-xl font-semibold mb-4">분석 내용</h3>
                <ReactMarkdown>{analysis.analysis}</ReactMarkdown>
              </section>
            </div>

            {analysis.citations.length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-4">참고 자료</h3>
                <ul className="space-y-2">
                  {analysis.citations.map((citation, index) => (
                    <li key={index} className="text-sm text-gray-600">
                      {citation}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}