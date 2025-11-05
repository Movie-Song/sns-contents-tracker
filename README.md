# 🚀 SNS Content Tracker

다양한 SNS 플랫폼의 콘텐츠를 자동으로 수집하여 Notion 데이터베이스에 저장하는 도구입니다.

## 📌 지원 플랫폼

- ✅ **티스토리 블로그** (RSS)
- ✅ **트위터/X** (Nitter RSS)
- 🔜 네이버 블로그 (예정)
- 🔜 워드프레스 (예정)
- 🔜 뉴스레터 (예정)

## 🎯 주요 기능

- **자동 수집**: GitHub Actions를 통한 스케줄 자동 실행
- **중복 방지**: URL 기반 중복 체크
- **무료**: API 키 불필요 (RSS 기반)
- **Notion 연동**: 수집한 콘텐츠를 자동으로 Notion에 저장

## 🛠️ 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/sns-content-tracker.git
cd sns-content-tracker
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

**GitHub Secrets 설정 (권장):**
- `NOTION_API_KEY` - Notion Integration 키
- `NOTION_DATABASE_ID` - Notion 데이터베이스 ID  
- `TISTORY_BLOGS` - 티스토리 블로그 URL (콤마로 구분)
- `TWITTER_USERNAME` - 트위터 계정명 (콤마로 구분, 선택)

**로컬 테스트용 `.env` 파일:**

```bash
# .env
NOTION_API_KEY=your_notion_integration_key
NOTION_DATABASE_ID=your_database_id
TISTORY_BLOGS=https://blog1.tistory.com,https://blog2.tistory.com
TWITTER_USERNAME=your_twitter_username
```

> 자세한 설정 방법은 **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** 참고

## 🔧 설정 가이드

### Notion 설정

1. [Notion Integrations](https://www.notion.so/my-integrations)에서 새 통합 생성
2. API 키 복사
3. Notion 데이터베이스에 통합 연결
4. 데이터베이스 ID 복사

### 티스토리 설정

자세한 설정 방법은 **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** 참고

**간단 요약:**
1. GitHub Repository → Settings → Secrets
2. `TISTORY_BLOGS` Secret 추가
   - 단일: `https://your-blog.tistory.com`
   - 여러 개: `https://blog1.tistory.com,https://blog2.tistory.com`
3. Workflow 파일에 환경변수 추가

### 트위터 설정

자세한 설정 방법은 **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** 참고

**간단 요약:**
1. GitHub Repository → Settings → Secrets
2. `TWITTER_USERNAME` Secret 추가 (@ 제외)
   - 단일: `your_username`
   - 여러 개: `account1,account2,account3`
3. Workflow 파일에 환경변수 추가

## 🚀 실행 방법

### 로컬 실행

```bash
python main.py
```

### GitHub Actions 자동 실행

1. `.github/workflows/scraper.yml` 파일 생성
2. GitHub Secrets에 환경변수 추가
3. Push 후 자동 실행 (또는 수동 실행)

**예시 workflow:**

```yaml
name: SNS Content Scraper

on:
  schedule:
    - cron: '0 15 * * *'  # 매일 밤 12시 (KST)
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - env:
        NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
        NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        TISTORY_BLOGS: ${{ secrets.TISTORY_BLOGS }}
        TWITTER_USERNAME: ${{ secrets.TWITTER_USERNAME }}
      run: python main.py
```

## 📊 Notion 데이터베이스 구조

필수 속성:
- `제목` (Title)
- `URL` (URL)
- `발행일` (Date)
- `플랫폼` (Select)

## 🐦 트위터 수집 방식

- **Nitter RSS** 활용 (무료, API 키 불필요)
- 공개 트윗만 수집 가능
- 기본 인스턴스: `nitter.poast.org`
- 다른 인스턴스 사용 가능 (설정 가이드 참고)

## 📝 사용 예시

```python
from scrapers import TwitterScraper

# 트위터 스크래퍼 초기화
twitter = TwitterScraper("elonmusk")

# 최근 50개 트윗 가져오기
tweets = twitter.fetch_posts(limit=50)

# 결과 출력
for tweet in tweets:
    print(f"{tweet['title']}")
    print(f"URL: {tweet['url']}")
    print(f"날짜: {tweet['published_date']}")
    print()
```

## 🔍 문제 해결

### 트윗이 수집되지 않을 때:
1. 트위터 계정명 확인 (@ 제외)
2. 계정이 public인지 확인
3. Nitter 인스턴스 변경 시도
4. 최근 트윗이 있는지 확인

### Notion 연동 오류:
1. API 키 확인
2. 데이터베이스 ID 확인
3. Integration 권한 확인

## 📂 프로젝트 구조

```
sns-content-tracker/
├── main.py                 # 메인 실행 파일
├── notion_handler.py       # Notion API 핸들러
├── scrapers/
│   ├── __init__.py
│   ├── tistory.py         # 티스토리 스크래퍼
│   └── twitter.py         # 트위터 스크래퍼
├── requirements.txt        # 의존성
├── README.md              # 프로젝트 설명
└── TWITTER_SETUP.md       # 트위터 설정 가이드
```

## 🤝 기여

이슈나 PR은 언제나 환영합니다!

## 📄 라이선스

MIT License

## 🙏 감사

- [Nitter](https://github.com/zedeus/nitter) - 트위터 RSS 제공
- [Notion API](https://developers.notion.com/) - Notion 연동
