# SNS Content Tracker 📊

블로그, 뉴스레터, SNS 콘텐츠 발행 빈도를 추적하는 자동화 시스템

## 📁 프로젝트 구조

```
sns-content-tracker/
├── .github/workflows/
│   └── daily_update.yml      # GitHub Actions 자동화
├── scrapers/
│   ├── __init__.py
│   ├── tistory.py           # 티스토리 RSS 크롤러
│   └── (추후 추가: naver_blog.py, wordpress.py 등)
├── notion_handler.py         # Notion API 처리
├── main.py                   # 메인 실행 파일
├── app.py                    # Streamlit 히트맵 앱
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 설치 및 실행

### 1. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env.example`을 복사해서 `.env` 파일 생성:
```bash
cp .env.example .env
```

`.env` 파일에 실제 값 입력:
```
NOTION_API_KEY=secret_xxxxx
DATABASE_ID=xxxxx
```

### 3. 로컬에서 실행
```bash
python main.py
```

### 4. 히트맵 보기
```bash
streamlit run app.py
```

## 📊 Notion 데이터베이스 구조

다음 속성들이 필요합니다:
- **Title** (제목) - Text
- **URL** (링크) - URL
- **Published Date** (작성일) - Date
- **Platform** (플랫폼) - Select
- **Created Time** (등록일) - Created Time (자동)

## 🤖 자동화

GitHub Actions를 통해 매일 자동으로 실행됩니다.

## 📝 플랫폼 추가하기

`scrapers/` 폴더에 새로운 크롤러 파일을 추가하면 됩니다.
