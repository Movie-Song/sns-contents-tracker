# 🚀 SNS Content Tracker

티스토리 블로그의 콘텐츠를 자동으로 수집하여 Notion 데이터베이스에 저장하는 도구입니다.

## 📌 지원 플랫폼

- ✅ **티스토리 블로그** (RSS 기반)
- 🔜 네이버 블로그 (예정)
- 🔜 워드프레스 (예정)
- 🔜 미디엄 (예정)

## 🎯 주요 기능

- **자동 수집**: GitHub Actions를 통한 매일 자동 실행
- **여러 블로그 지원**: 여러 개의 티스토리 블로그를 동시에 수집
- **중복 방지**: URL 기반 자동 중복 체크
- **완전 무료**: API 키 불필요 (RSS 기반)
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

**GitHub Secrets 설정 (필수):**
- `NOTION_API_KEY` - Notion Integration 키
- `DATABASE_ID` - Notion 데이터베이스 ID  
- `TISTORY_BLOGS` - 티스토리 블로그 URL (콤마로 구분)

**로컬 테스트용 `.env` 파일:**

```bash
# .env
NOTION_API_KEY=your_notion_integration_key
DATABASE_ID=your_database_id
TISTORY_BLOGS=https://blog1.tistory.com,https://blog2.tistory.com
```

> 자세한 설정 방법은 **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** 참고

## 🔧 설정 가이드

### Notion 설정

1. [Notion Integrations](https://www.notion.so/my-integrations)에서 새 통합 생성
2. API 키 복사
3. Notion 데이터베이스에 통합 연결
4. 데이터베이스 ID 복사

### 티스토리 설정

**간단 요약:**
1. GitHub Repository → Settings → Secrets
2. `TISTORY_BLOGS` Secret 추가
   - 단일 블로그: `https://your-blog.tistory.com`
   - 여러 블로그: `https://blog1.tistory.com,https://blog2.tistory.com`
3. Workflow 파일에 환경변수 추가

자세한 내용은 **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** 참고

## 🚀 실행 방법

### 로컬 실행

```bash
python main.py
```

### GitHub Actions 자동 실행

1. `.github/workflows/daily_update.yml` 파일 설정
2. GitHub Secrets에 환경변수 추가
3. Push 후 자동 실행 (또는 수동 실행)

**Workflow 예시:**

```yaml
name: Daily Content Update

on:
  schedule:
    - cron: '10 15 * * *'  # 매일 한국시간 00:10
  workflow_dispatch:

jobs:
  update-content:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - env:
        NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
        DATABASE_ID: ${{ secrets.DATABASE_ID }}
        NOTION_DATABASE_ID: ${{ secrets.DATABASE_ID }}
        TISTORY_BLOGS: ${{ secrets.TISTORY_BLOGS }}
      run: python main.py
```

## 📊 Notion 데이터베이스 구조

필수 속성:
- `제목` (Title)
- `URL` (URL)
- `발행일` (Date)
- `플랫폼` (Select)

## 📝 사용 예시

```python
from scrapers import TistoryScraper

# 티스토리 스크래퍼 초기화
tistory = TistoryScraper("https://your-blog.tistory.com")

# 최근 50개 포스트 가져오기
posts = tistory.fetch_posts(limit=50)

# 결과 출력
for post in posts:
    print(f"{post['title']}")
    print(f"URL: {post['url']}")
    print(f"날짜: {post['published_date']}")
    print()
```

## 🔍 문제 해결

### 포스트가 수집되지 않을 때:
- ✅ 블로그 URL 확인 (https:// 포함)
- ✅ RSS 피드 접근 가능 여부 확인 (`블로그URL/rss`)
- ✅ 블로그에 게시된 글이 있는지 확인
- ✅ 블로그가 비공개 설정이 아닌지 확인

### Notion 연동 오류:
- ✅ API 키가 올바른지 확인
- ✅ 데이터베이스 ID가 올바른지 확인
- ✅ Integration이 데이터베이스에 연결되어 있는지 확인
- ✅ 데이터베이스 속성(Title, URL, Date, Select)이 있는지 확인

## 📂 프로젝트 구조

```
sns-content-tracker/
├── .github/
│   └── workflows/
│       └── daily_update.yml   # GitHub Actions 설정
├── scrapers/
│   ├── __init__.py
│   └── tistory.py            # 티스토리 스크래퍼
├── main.py                    # 메인 실행 파일
├── app.py                     # Streamlit 대시보드
├── notion_handler.py          # Notion API 핸들러
├── requirements.txt           # 의존성
├── README.md                  # 프로젝트 설명
└── SETUP_GUIDE.md            # 상세 설정 가이드
```

## 📊 Notion에서 블로그 구분하기

여러 블로그를 수집하면 플랫폼 필드에서 자동으로 구분됩니다:

- `Tistory (blog1)` - 첫 번째 블로그
- `Tistory (blog2)` - 두 번째 블로그
- `Tistory (blog3)` - 세 번째 블로그

### 필터 활용:

**특정 블로그만 보기:**
```
플랫폼 = "Tistory (blog1)"
```

**모든 티스토리 글 보기:**
```
플랫폼 contains "Tistory"
```

## 💡 팁

### 수집 빈도 변경:

```yaml
# 매 6시간마다
- cron: '0 */6 * * *'

# 주중 매일 (월~금)
- cron: '10 15 * * 1-5'

# 매주 월요일
- cron: '10 15 * * 1'
```

### 수집 개수 조절:

`main.py`에서 `limit` 값 수정:

```python
# 최근 50개만
posts = tistory.fetch_posts(limit=50)

# 최근 200개
posts = tistory.fetch_posts(limit=200)
```

## 🤝 기여

이슈나 PR은 언제나 환영합니다!

## 📄 라이선스

MIT License

---

## ✨ 특징

- 🎯 **간단한 설정**: 5분이면 완료
- 🔄 **자동화**: 매일 자동 수집
- 📊 **시각화**: Streamlit 대시보드 포함
- 🆓 **완전 무료**: API 비용 없음
- 🔒 **안전**: GitHub Secrets로 관리

---

**Made with ❤️ for content creators**
