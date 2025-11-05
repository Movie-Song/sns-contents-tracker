# 🔧 SNS Content Tracker 설정 가이드

티스토리 블로그 자동 수집을 위한 완전한 설정 가이드입니다.

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

---

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
> - 여러 블로그는 콤마로 구분 (공백 있어도 자동 제거됨)

---

### 🔐 Secret 2: NOTION_API_KEY (필수)

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

### 📊 Secret 3: DATABASE_ID (필수)

- **Name**: `DATABASE_ID`
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

**데이터베이스 구조 (필수 속성):**
- `제목` (Title) - 필수
- `URL` (URL) - 필수
- `발행일` (Date) - 필수
- `플랫폼` (Select) - 필수

**Integration 연결하기:**
1. 데이터베이스 페이지 우측 상단 `•••` 클릭
2. `Connections` → `Connect to` 
3. 위에서 만든 Integration 선택

---

## 2️⃣ GitHub Actions Workflow 설정

`.github/workflows/daily_update.yml` 파일을 확인하거나 생성합니다.

### 📄 완성된 Workflow 예시:

```yaml
name: Daily Content Update

on:
  schedule:
    # 매일 한국 시간 오전 12시 10분 (UTC 15:10)에 실행
    - cron: "10 15 * * *"
  
  # 수동 실행 가능
  workflow_dispatch:

jobs:
  update-content:
    runs-on: ubuntu-latest
    
    steps:
      - name: 📥 코드 체크아웃
        uses: actions/checkout@v4
      
      - name: 🐍 Python 설정
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: 📦 의존성 설치
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: 🚀 콘텐츠 수집 실행
        run: python main.py
        env:
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          DATABASE_ID: ${{ secrets.DATABASE_ID }}
          NOTION_DATABASE_ID: ${{ secrets.DATABASE_ID }}
          TISTORY_BLOGS: ${{ secrets.TISTORY_BLOGS }}
      
      - name: ✅ 완료
        run: echo "콘텐츠 업데이트가 완료되었습니다!"
```

### 🔑 중요 포인트:

**✅ 반드시 포함해야 할 환경변수:**
```yaml
env:
  NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
  DATABASE_ID: ${{ secrets.DATABASE_ID }}
  NOTION_DATABASE_ID: ${{ secrets.DATABASE_ID }}
  TISTORY_BLOGS: ${{ secrets.TISTORY_BLOGS }}
```

---

## 3️⃣ 테스트 방법

### 로컬 테스트:

**환경변수 설정:**
```bash
# 필수
export NOTION_API_KEY="your_notion_api_key"
export DATABASE_ID="your_database_id"
export TISTORY_BLOGS="https://blog1.tistory.com,https://blog2.tistory.com"

# 실행
python main.py
```

### GitHub Actions 수동 테스트:

1. GitHub 저장소의 `Actions` 탭 클릭
2. `Daily Content Update` workflow 선택
3. `Run workflow` 버튼 클릭
4. 실행 로그에서 결과 확인

**예상 로그:**
```
📘 티스토리 블로그 수집 중...
------------------------------------------------------------
📋 총 2개의 티스토리 블로그 수집 예정
   블로그 목록: https://blog1.tistory.com, https://blog2.tistory.com

📘 [1/2] https://blog1.tistory.com 처리 중...
✅ 15개의 포스트를 찾았습니다.
✅ https://blog1.tistory.com 처리 완료

📊 수집 완료!
   ✅ 새로 추가: 15개
```

---

## 4️⃣ 문제 해결

### 티스토리 관련:

**"수집된 포스트가 없습니다" 오류:**
- ✅ 블로그 URL 확인 (https:// 포함)
- ✅ RSS 피드 접근 가능 여부 확인 (`블로그URL/rss`)
- ✅ 블로그에 게시된 글이 있는지 확인
- ✅ 블로그가 비공개 설정이 아닌지 확인

**"RSS 피드 파싱 오류":**
- ✅ URL이 올바른 티스토리 주소인지 확인
- ✅ 네트워크 연결 확인
- ✅ 잠시 후 다시 시도

**여러 블로그 중 일부만 작동:**
- ✅ 각 블로그 URL이 올바른지 개별 확인
- ✅ 콤마로 제대로 구분되었는지 확인
- ✅ 에러 로그에서 어떤 블로그가 실패했는지 확인

### Notion 관련:

**"Notion 연결 실패" 오류:**
- ✅ API 키가 올바른지 확인
- ✅ 데이터베이스 ID가 올바른지 확인
- ✅ Integration이 데이터베이스에 연결되어 있는지 확인
- ✅ 데이터베이스 속성(Title, URL, Date, Select)이 있는지 확인

**"데이터베이스에 권한이 없습니다" 오류:**
- ✅ 데이터베이스 설정에서 Integration 연결 확인
- ✅ Integration에 쓰기 권한이 있는지 확인

### GitHub Actions 관련:

**Workflow가 실행되지 않음:**
- ✅ `.github/workflows/` 폴더 경로 확인
- ✅ YAML 파일 문법 오류 확인 (들여쓰기 주의)
- ✅ Secrets 이름 오타 확인 (대소문자 구분)

**"환경변수가 설정되지 않았습니다" 오류:**
- ✅ GitHub Secrets 추가 확인
- ✅ Workflow 파일에 `env` 설정 추가 확인
- ✅ Secret 이름이 정확한지 확인

---

## 📊 Notion에서 콘텐츠 구분하기

### 플랫폼 필드 표시 예시:

- `Tistory (pro-editor)` - 티스토리 pro-editor 블로그
- `Tistory (tech-blog)` - 티스토리 tech-blog 블로그
- `Tistory (daily-log)` - 티스토리 daily-log 블로그

### 필터 활용:

**특정 블로그만 보기:**
```
플랫폼 = "Tistory (pro-editor)"
```

**모든 티스토리 글 보기:**
```
플랫폼 contains "Tistory"
```

**최근 30일 글만 보기:**
```
발행일 > 30 days ago
```

---

## ✅ 설정 완료 체크리스트

- [ ] GitHub Secrets 3개 모두 추가
  - [ ] TISTORY_BLOGS
  - [ ] NOTION_API_KEY
  - [ ] DATABASE_ID
- [ ] Notion Integration 생성 및 데이터베이스 연결
- [ ] Notion 데이터베이스 속성 확인 (Title, URL, Date, Select)
- [ ] Workflow 파일 생성/확인
- [ ] 로컬 또는 GitHub Actions에서 테스트 성공

---

## 🎉 완료!

이제 매일 자동으로 티스토리 블로그 글이 Notion에 수집됩니다!
- ✅ 매일 한국시간 00:10 자동 실행
- ✅ 여러 블로그 동시 수집
- ✅ 중복 자동 제거
- ✅ Notion에서 히트맵으로 시각화 가능

---

## 💡 추가 팁

### 수집 시간 변경:

```yaml
# 매일 아침 9시
- cron: "0 0 * * *"

# 매 6시간마다
- cron: "0 */6 * * *"

# 주중 매일 (월~금)
- cron: "10 15 * * 1-5"
```

### 수집 개수 조절:

`main.py`에서 `limit` 값 수정:

```python
# 더 많이 수집
posts = tistory.fetch_posts(limit=200)

# 적게 수집
posts = tistory.fetch_posts(limit=50)
```

### 여러 Notion 데이터베이스 사용:

각 블로그를 다른 데이터베이스에 저장하고 싶다면, 
`notion_handler.py`를 수정하거나 별도 스크립트를 만드세요.

---

궁금한 점이 있으시면 언제든지 Issue를 남겨주세요! 🙌
