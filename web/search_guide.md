# 네이버 Search Advisor SEO 가이드

> LawBot 사이트에 적용된 네이버 SEO 최적화 가이드

## 1. 기본 SEO 설정

### 1.1 HTML 마크업 구조

#### Title 태그
- 페이지당 고유한 title 필수
- 50자 이내 권장 (네이버 검색결과에서 잘림 방지)
- 핵심 키워드를 앞쪽에 배치
- 브랜드명은 뒤쪽에 배치

```html
<title>AI 법률 상담 | LawBot - 무료 AI 법률 정보 서비스</title>
```

#### Meta Description
- 페이지당 고유한 description 필수
- 80~160자 권장
- 핵심 키워드 포함
- 클릭을 유도하는 문구

```html
<meta name="description" content="24시간 무료 AI 법률 상담. 노동법, 임대차법, 소비자보호법, 교통사고 4대 분야 전문.">
```

#### Heading 구조
- h1 태그는 페이지당 1개만 사용
- h1 → h2 → h3 순서로 계층 구조 유지
- 핵심 키워드 포함

### 1.2 Open Graph 메타 태그

네이버, 카카오톡, 페이스북 공유 시 표시되는 정보

```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://lawbot-public.vercel.app/">
<meta property="og:title" content="LawBot | 4대 법률 분야 특화 AI 법률 정보 서비스">
<meta property="og:description" content="노동법, 임대차법, 소비자보호법, 교통사고 4대 분야에 특화된 AI 법률 정보 서비스.">
<meta property="og:image" content="https://lawbot-public.vercel.app/og-image.png">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="LawBot">
```

**og:image 권장사항:**
- 최소 200x200px
- 권장 1200x630px (1.91:1 비율)
- PNG 또는 JPG 형식
- 5MB 이하

---

## 2. robots.txt 설정

### 2.1 기본 구조

```
# 모든 검색엔진 허용
User-agent: *
Allow: /
Crawl-delay: 1

# 네이버 검색봇
User-agent: Yeti
Allow: /

# 사이트맵 위치
Sitemap: https://lawbot-public.vercel.app/sitemap.xml
```

### 2.2 네이버 검색봇 (Yeti)
- 네이버 검색봇 이름: `Yeti`
- Allow/Disallow로 크롤링 제어
- Crawl-delay로 크롤링 속도 조절 (초 단위)

### 2.3 주의사항
- 민감한 페이지는 Disallow
- API 엔드포인트는 크롤링 제외
- 이미지/CSS/JS는 크롤링 허용 (렌더링에 필요)

---

## 3. sitemap.xml 설정

### 3.1 기본 구조

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://lawbot-public.vercel.app/</loc>
        <lastmod>2026-01-30</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>
```

### 3.2 필수 요소
- `<loc>`: 페이지 URL (필수)
- `<lastmod>`: 마지막 수정일 (권장, YYYY-MM-DD 형식)
- `<changefreq>`: 변경 빈도 (always, hourly, daily, weekly, monthly, yearly, never)
- `<priority>`: 중요도 (0.0 ~ 1.0, 기본값 0.5)

### 3.3 권장사항
- 최대 50,000개 URL 또는 50MB
- 초과 시 sitemap index 파일 사용
- 동적 페이지도 포함
- 404 페이지는 제외

---

## 4. 구조화된 데이터 (JSON-LD)

### 4.1 네이버 지원 타입
- WebSite
- WebApplication
- FAQPage
- Article
- BreadcrumbList
- Organization
- LocalBusiness

### 4.2 WebApplication 예시

```json
{
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "LawBot",
    "description": "4대 법률 분야 특화 AI 법률 정보 서비스",
    "url": "https://lawbot-public.vercel.app",
    "applicationCategory": "LegalService",
    "operatingSystem": "Web Browser",
    "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "KRW"
    },
    "inLanguage": "ko"
}
```

### 4.3 FAQPage 예시

```json
{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "LawBot은 무료인가요?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "네, 완전 무료입니다."
            }
        }
    ]
}
```

### 4.4 BreadcrumbList 예시

```json
{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "홈",
            "item": "https://lawbot-public.vercel.app/"
        },
        {
            "@type": "ListItem",
            "position": 2,
            "name": "블로그",
            "item": "https://lawbot-public.vercel.app/blog/"
        }
    ]
}
```

---

## 5. IndexNow 설정

### 5.1 개요
- 콘텐츠 변경 시 검색엔진에 즉시 알림
- 네이버, Bing, Yandex 등 지원
- 크롤링 대기 시간 단축

### 5.2 API 키 설정

1. API 키 생성 (UUID 형식)
2. 키 파일 생성: `/{api-key}.txt`
3. 파일 내용: API 키 값만 입력

```
# /abc123-def456-ghi789.txt
abc123-def456-ghi789
```

### 5.3 IndexNow API 호출

```bash
# 단일 URL 제출
curl "https://searchadvisor.naver.com/indexnow?url=https://lawbot-public.vercel.app/blog/new-post&key=YOUR_API_KEY"

# 다중 URL 제출 (POST)
curl -X POST "https://searchadvisor.naver.com/indexnow" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "lawbot-public.vercel.app",
    "key": "YOUR_API_KEY",
    "urlList": [
      "https://lawbot-public.vercel.app/blog/post1",
      "https://lawbot-public.vercel.app/blog/post2"
    ]
  }'
```

---

## 6. 모바일 최적화

### 6.1 반응형 웹 (권장)
- 하나의 URL로 모든 기기 대응
- CSS 미디어 쿼리 사용
- viewport 메타 태그 필수

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### 6.2 모바일 친화적 체크리스트
- [ ] 터치 타겟 크기 최소 48x48px
- [ ] 글꼴 크기 최소 16px
- [ ] 가로 스크롤 없음
- [ ] 콘텐츠가 화면에 맞게 조절

---

## 7. 페이지 속도 최적화

### 7.1 권장사항
- LCP (Largest Contentful Paint): 2.5초 이내
- FID (First Input Delay): 100ms 이내
- CLS (Cumulative Layout Shift): 0.1 이내

### 7.2 최적화 방법
- 이미지 최적화 (WebP, 적절한 크기)
- CSS/JS 압축 및 최소화
- 폰트 preload
- 캐싱 활용

```html
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="preload" href="fonts/font.woff2" as="font" type="font/woff2" crossorigin>
```

---

## 8. 콘텐츠 가이드라인

### 8.1 품질 콘텐츠
- 독창적이고 유용한 콘텐츠
- 키워드 남용 금지
- 중복 콘텐츠 피하기
- 정기적인 업데이트

### 8.2 금지 사항
- 키워드 스터핑
- 숨겨진 텍스트/링크
- 클로킹 (검색엔진과 사용자에게 다른 콘텐츠 제공)
- 자동 생성 콘텐츠 남용
- 링크 스팸

---

## 9. LawBot 적용 현황

### 9.1 완료 항목
- [x] 네이버 사이트 인증 (메타 태그)
- [x] robots.txt 설정 (Yeti 포함)
- [x] sitemap.xml 생성
- [x] Open Graph 메타 태그
- [x] JSON-LD 구조화 데이터 (WebApplication, FAQPage)
- [x] 반응형 웹 디자인
- [x] viewport 메타 태그
- [x] canonical URL 설정

### 9.2 추가 적용 예정
- [ ] IndexNow API 키 설정
- [ ] BreadcrumbList 구조화 데이터
- [ ] 블로그 글별 Article 구조화 데이터
- [ ] 이미지 alt 태그 최적화
- [ ] 페이지 속도 개선

---

## 10. 참고 링크

- [네이버 Search Advisor](https://searchadvisor.naver.com/)
- [Schema.org](https://schema.org/)
- [Google Search Central](https://developers.google.com/search)
- [IndexNow](https://www.indexnow.org/)
