현재 React 컴포넌트를 shadcn/ui 디자인 시스템을 사용해서 전면 개편해주세요.

## 요구사항

### 1. 사용할 shadcn/ui 컴포넌트들
- Card, CardHeader, CardContent, CardTitle
- Label, Input
- Button
- lucide-react 아이콘 (TrendingUp, Building2, Calendar, Settings, Play)

### 2. 레이아웃 구조
전체를 Card 컴포넌트로 감싸고, CardHeader와 CardContent로 구분해주세요:

<Card className="w-full max-w-4xl mx-auto">
  <CardHeader>
    <CardTitle>제목 영역</CardTitle>
    <p>설명 텍스트</p>
  </CardHeader>
  <CardContent className="space-y-6">
    {/* 각 섹션을 공간으로 구분 */}
  </CardContent>
</Card>

### 3. 구체적인 개선 사항

**헤더 영역:**
- TrendingUp 아이콘 + 제목을 flex로 배치
- text-2xl font-bold 적용
- 부제목은 text-muted-foreground 색상

**시장 구분 섹션:**
- Label + Input 조합
- Building2 아이콘 추가
- 설명 텍스트를 text-sm text-muted-foreground로

**종목 정보 (2열 그리드):**
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div className="space-y-2">
    <Label htmlFor="stock-code">종목코드</Label>
    <Input id="stock-code" placeholder="005930" />
  </div>
  <div className="space-y-2">
    <Label htmlFor="company">기업명</Label>
    <Input id="company" placeholder="삼성전자" />
  </div>
</div>

**날짜 섹션 (2열 그리드):**
- Calendar 아이콘 포함
- From/To 날짜를 2열로 배치
- Label과 Input 조합

**API 설정:**
- Settings 아이콘 추가
- 보안 관련 섹션임을 시각적으로 표현

**실행 버튼:**
<Button className="w-full" size="lg">
  <Play className="mr-2 h-4 w-4" />
  분석 시작
</Button>

### 4. 스타일링 가이드라인
- 전체 max-width: 4xl (896px)
- 섹션 간 간격: space-y-6
- 입력 필드 간격: space-y-2
- 그리드 breakpoint: md (768px)
- 색상: 기본 shadcn color palette 사용

### 5. 접근성
- 모든 Input에 적절한 Label 연결
- htmlFor와 id 속성 매칭
- 시맨틱한 HTML 구조 유지

### 6. 추가 요청사항
- 각 섹션별로 아이콘을 포함한 제목 표시
- 반응형 디자인 적용 (모바일에서는 1열, 데스크탑에서는 2열)
- shadcn/ui의 기본 색상과 간격 시스템 사용
- 기존 기능은 유지하되 UI만 완전히 교체

위 가이드라인에 따라 전체 컴포넌트를 재작성해주세요.