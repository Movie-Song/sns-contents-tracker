# 🔧 SNS Content Tracker 설정 가이드

## 📋 목차
1. [GitHub Secrets 설정](#1️⃣-github-secrets-설정)
2. [GitHub Actions Workflow 설정](#2️⃣-github-actions-workflow-설정)
3. [테스트 방법](#3️⃣-테스트-방법)
4. [문제 해결](#4️⃣-문제-해결)

---

## 1️⃣ GitHub Secrets 설정

### 단계별 설정 방법:

1. **GitHub 저장소로 이동**
   - 본인의 프로젝트 저장소 페이지로 이동

2. **Settings 메뉴 클릭**
   - 저장소 상단의 `Settings` 탭 클릭

3. **Secrets and variables 설정**
   - 왼쪽 사이드바에서 `Secrets and variables` → `Actions` 클릭

4. **New repository secret 추가**

아래 3개의 Secret을 차례대로 추가해주세요:

### 📘 Secret 1: TISTORY_BLOGS (필수)

- **Name**: `TISTORY_BLOGS`
- **Secret**: 티스토리 블로그 URL 입력

**단일 블로그:**
```
https://your-blog.tistory.com
```

**여러 블로그 (콤마로 구분):**
```
https://blog1.tistory.com,https://blog2.tistory.com,https://blog3.tistory.com
```

**예시:**
```
https://pro-editor.tistory.com,https://tech-blog.tistory.com
```

> ⚠️ 주의: 
> - 반드시 `https://` 포함
> - 티스토리가 아닌 커스텀 도메인도 가능
> - 여러 블로그는 콤마로 구분

---

### ~🐦 Secret 2: TWITTER_USERNAME (선택)~ 트위터는 안 되서 포기

- ~**Name**: `TWITTER_USERNAME`~
- ~**Secret**: 트위터 계정명 입력~

~**단일 계정:**~
```
~your_username~
```

~**여러 계정 (콤마로 구분):**~
```
~account1,account2,account3~
```

~**예시:**~
```
~elonmusk,BillGates,nasa~
```

> ~⚠️ 주의: @ 기호는 제외하고 입력하세요!~

---

### 🔐 Secret 3: NOTION_API_KEY (필수)

- **Name**: `NOTION_API_KEY`
- **Secret**: Notion Integration API 키

**Notion API 키 발급 방법:**
1. [Notion Integrations](https://www.notion.so/my-integrations) 접속
2. `+ New integration` 클릭
3. Integration 이름 설정 (예: SNS Content Tracker)
4. `Submit` 클릭
5. `Internal Integration Token` 복사
6. GitHub Secret에 추가

---

### 📊 Secret 4: NOTION_DATABASE_ID (필수)

- **Name**: `NOTION_DATABASE_ID`
- **Secret**: Notion 데이터베이스 ID

**Notion 데이터베이스 ID 찾기:**
1. Notion에서 데이터베이스 페이지 열기
2. 우측 상단 `•••` 클릭 → `Copy link` 
3. URL에서 ID 추출:
```
https://www.notion.so/workspace/{database_id}?v=...
                                ^^^^^^^^^^^
                                이 부분이 Database ID
```

**데이터베이스 구조:**
- `제목` (Title) - 필수
- `URL` (URL) - 필수
- `발행일` (Date) - 필수
- `플랫폼` (Select) - 필수

---

## 2️⃣ GitHub Actions Workflow 설정

`.github/workflows/scraper.yml` 파일을 생성하거나 수정합니다.

### 📄 완성된 Workflow 예시:

```yaml
name: SNS Content Scraper

on:
  schedule:
    # 매일 밤 12시 (UTC 15:00 = KST 00:00)
    - cron: '0 15 * * *'
  workflow_dispatch:  # 수동 실행 가능

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: 코드 체크아웃
      uses: actions/checkout@v3
    
    - name: Python 설정
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: 의존성 설치
      run: |
        pip install -r requirements.txt
    
    - name: 스크래퍼 실행
      env:
        NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
        NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        TISTORY_BLOGS: ${{ secrets.TISTORY_BLOGS }}
        TWITTER_USERNAME: ${{ secrets.TWITTER_USERNAME }}
      run: |
        python main.py
```

### 🔑 중요 포인트:

**✅ 반드시 포함해야 할 환경변수:**
```yaml
env:
  NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
  NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
  TISTORY_BLOGS: ${{ secrets.TISTORY_BLOGS }}
  TWITTER_USERNAME: ${{ secrets.TWITTER_USERNAME }}  # 트위터 사용시
```

---

## 3️⃣ 테스트 방법

### 로컬 테스트:

**환경변수 설정:**
```bash
# 필수
export NOTION_API_KEY="your_notion_api_key"
export NOTION_DATABASE_ID="your_database_id"
export TISTORY_BLOGS="https://blog1.tistory.com,https://blog2.tistory.com"

# 선택 (트위터 사용시)
export TWITTER_USERNAME="account1,account2"

# 실행
python main.py
```

### GitHub Actions 수동 테스트:

1. GitHub 저장소의 `Actions` 탭 클릭
2. `SNS Content Scraper` workflow 선택
3. `Run workflow` 버튼 클릭
4. 실행 로그에서 결과 확인

---

## 4️⃣ 문제 해결

### 티스토리 관련:

**"수집된 포스트가 없습니다" 오류:**
- ✅ 블로그 URL 확인 (https:// 포함)
- ✅ RSS 피드 접근 가능 여부 확인 (`블로그URL/rss`)
- ✅ 블로그에 게시된 글이 있는지 확인

**"RSS 피드 파싱 오류":**
- ✅ URL이 올바른 티스토리 주소인지 확인
- ✅ 네트워크 연결 확인
- ✅ 블로그가 비공개 설정인지 확인

### ~트위터 관련:~

~**"수집된 트윗이 없습니다" 오류:**~
- ~✅ 트위터 계정명 확인 (@ 제외)~
- ~✅ 최근 트윗 여부 확인~
- ~✅ Nitter 인스턴스 상태 확인~
- ~✅ 계정이 private이 아닌지 확인~

~**Nitter 접속 오류:**~
- ~✅ 네트워크 연결 확인~
- ~✅ 다른 Nitter 인스턴스로 변경~
- ~✅ 잠시 후 다시 시도~

### Notion 관련:

**"Notion 연결 실패" 오류:**
- ✅ API 키가 올바른지 확인
- ✅ 데이터베이스 ID가 올바른지 확인
- ✅ Integration이 데이터베이스에 연결되어 있는지 확인
- ✅ 데이터베이스 속성(Title, URL, Date, Select)이 있는지 확인

### 여러 계정/블로그 관련:

**여러 계정이 제대로 인식되지 않을 때:**
- ✅ 콤마로 올바르게 구분했는지 확인
- ✅ 각 URL/계정명 앞뒤 공백 확인 (자동 제거됨)
- ✅ Secret 이름 오타 확인 (대소문자 구분)

**Notion에서 구분이 안 될 때:**
- ✅ 플랫폼 필드가 다음 형식으로 표시되는지 확인:
  - `Tistory (blog-name)`


---

## 📊 Notion에서 콘텐츠 구분하기

### 플랫폼 필드 표시 예시:

- `Tistory (pro-editor)` - 티스토리 pro-editor 블로그
- `Tistory (tech-blog)` - 티스토리 tech-blog 블로그


### 필터 활용:

**특정 블로그만 보기:**
```
플랫폼 = "Tistory (pro-editor)"
```

**모든 티스토리 글 보기:**
```
플랫폼 contains "Tistory"
```

---

## ✅ 설정 완료 체크리스트

- [ ] GitHub Secrets 3개 모두 추가
  - [ ] TISTORY_BLOGS
  - [ ] NOTION_API_KEY
  - [ ] NOTION_DATABASE_ID
- [ ] Notion Integration 생성 및 데이터베이스 연결
- [ ] Workflow 파일 생성/수정
- [ ] 로컬 또는 GitHub Actions에서 테스트 성공

---

## 🎉 완료!

이제 매일 자동으로 다음 콘텐츠가 Notion에 수집됩니다:
- ✅ 티스토리 블로그 글 (여러 블로그 지원)
- 🔜 향후 더 많은 플랫폼 추가 예정!

---

## 💡 팁

### 수집 빈도 변경:

매일이 아닌 다른 주기로 실행하고 싶다면 workflow의 cron 수정:

```yaml
# 매 6시간마다
- cron: '0 */6 * * *'

# 주중 매일 (월~금)
- cron: '0 15 * * 1-5'

# 매주 월요일
- cron: '0 15 * * 1'
```

### 수집 개수 조절:

`main.py`에서 `limit` 값 수정:

```python
# 티스토리: 최근 50개만
posts = tistory.fetch_posts(limit=50)
```

---

궁금한 점이 있으시면 언제든지 Issue를 남겨주세요! 🙌
