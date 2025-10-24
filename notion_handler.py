import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from urllib.parse import urlparse, urlunparse

# 환경 변수 로드
load_dotenv()

class NotionHandler:
    """Notion API를 통해 콘텐츠 트래킹 데이터를 관리하는 클래스"""
    
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY")
        self.database_id = os.getenv("DATABASE_ID")
        
        if not self.api_key or not self.database_id:
            raise ValueError("NOTION_API_KEY와 DATABASE_ID를 환경 변수에 설정해주세요.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
    
    def normalize_url(self, url: str) -> str:
        """
        URL을 정규화합니다 (중복 체크 정확도 향상)
        - 끝의 슬래시 제거
        - 소문자 변환
        - http/https 통일
        """
        if not url:
            return ""
        
        # URL 파싱
        parsed = urlparse(url.lower().strip())
        
        # path에서 끝의 슬래시 제거
        path = parsed.path.rstrip('/')
        
        # 재조립 (scheme, netloc, path만 사용)
        normalized = urlunparse((
            parsed.scheme or 'https',
            parsed.netloc,
            path,
            '',  # params
            '',  # query
            ''   # fragment
        ))
        
        return normalized
    
    def add_content(self, title: str, url: str, published_date: str, platform: str) -> bool:
        """
        Notion 데이터베이스에 새 콘텐츠를 추가합니다.
        
        Args:
            title: 콘텐츠 제목
            url: 콘텐츠 URL
            published_date: 발행일 (YYYY-MM-DD 형식)
            platform: 플랫폼 이름 (예: 티스토리, 네이버 블로그)
        
        Returns:
            bool: 성공 여부
        """
        # URL 정규화
        normalized_url = self.normalize_url(url)
        
        # 중복 체크 (URL 기반)
        if self.is_url_exists(normalized_url):
            print(f"⏭️  이미 존재: {title[:50]}...")
            return False
        
        # 추가 안전장치: 제목으로도 체크 (같은 날짜에 같은 제목이면 중복으로 간주)
        if self.is_title_exists(title, published_date):
            print(f"⏭️  중복 제목: {title[:50]}... ({published_date})")
            return False
        
        # Notion 페이지 생성
        create_url = f"{self.base_url}/pages"
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": title}}]
                },
                "URL": {
                    "url": url  # 원본 URL 저장
                },
                "Published Date": {
                    "date": {"start": published_date}
                },
                "Platform": {
                    "select": {"name": platform}
                }
            }
        }
        
        try:
            response = requests.post(create_url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"✅ 추가: {title[:50]}...")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 추가 실패: {title[:50]}...")
            print(f"   에러: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"   응답: {e.response.text[:200]}")
            return False
    
    def is_url_exists(self, url: str) -> bool:
        """
        URL이 이미 데이터베이스에 존재하는지 확인합니다.
        정규화된 URL로 체크하여 정확도를 높입니다.
        
        Args:
            url: 확인할 URL (정규화된)
        
        Returns:
            bool: 존재 여부
        """
        # 데이터베이스의 모든 페이지 가져오기 (필터 없이)
        query_url = f"{self.base_url}/databases/{self.database_id}/query"
        
        try:
            response = requests.post(query_url, headers=self.headers, json={})
            response.raise_for_status()
            results = response.json().get("results", [])
            
            # 각 결과의 URL을 정규화해서 비교
            for page in results:
                props = page.get("properties", {})
                existing_url = props.get("URL", {}).get("url", "")
                
                if existing_url:
                    normalized_existing = self.normalize_url(existing_url)
                    if normalized_existing == url:
                        return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  URL 중복 체크 실패: {str(e)}")
            # 에러 시 안전을 위해 True 반환 (중복으로 간주하여 추가 방지)
            return True
    
    def is_title_exists(self, title: str, published_date: str) -> bool:
        """
        같은 날짜에 같은 제목이 이미 존재하는지 확인합니다.
        
        Args:
            title: 확인할 제목
            published_date: 발행일
        
        Returns:
            bool: 존재 여부
        """
        query_url = f"{self.base_url}/databases/{self.database_id}/query"
        
        try:
            # 같은 날짜의 페이지 조회
            payload = {
                "filter": {
                    "property": "Published Date",
                    "date": {
                        "equals": published_date
                    }
                }
            }
            
            response = requests.post(query_url, headers=self.headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            # 각 결과의 제목 비교
            for page in results:
                props = page.get("properties", {})
                existing_title = ""
                if props.get("Title", {}).get("title"):
                    existing_title = props["Title"]["title"][0]["text"]["content"]
                
                if existing_title.strip().lower() == title.strip().lower():
                    return True
            
            return False
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  제목 중복 체크 실패: {str(e)}")
            return False
    
    def get_all_contents(self, days: int = 365) -> List[Dict]:
        """
        최근 N일간의 모든 콘텐츠를 가져옵니다.
        
        Args:
            days: 조회할 일수 (기본 365일)
        
        Returns:
            List[Dict]: 콘텐츠 목록
        """
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        query_url = f"{self.base_url}/databases/{self.database_id}/query"
        
        payload = {
            "filter": {
                "property": "Published Date",
                "date": {
                    "on_or_after": start_date
                }
            },
            "sorts": [
                {
                    "property": "Published Date",
                    "direction": "descending"
                }
            ]
        }
        
        try:
            response = requests.post(query_url, headers=self.headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            # 데이터 파싱
            contents = []
            for page in results:
                props = page.get("properties", {})
                
                # 각 속성 안전하게 추출
                title = ""
                if props.get("Title", {}).get("title"):
                    title = props["Title"]["title"][0]["text"]["content"]
                
                url = props.get("URL", {}).get("url", "")
                
                published_date = ""
                if props.get("Published Date", {}).get("date"):
                    published_date = props["Published Date"]["date"]["start"]
                
                platform = ""
                if props.get("Platform", {}).get("select"):
                    platform = props["Platform"]["select"]["name"]
                
                contents.append({
                    "title": title,
                    "url": url,
                    "published_date": published_date,
                    "platform": platform
                })
            
            print(f"📊 총 {len(contents)}개의 콘텐츠를 가져왔습니다.")
            return contents
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 데이터 조회 실패: {str(e)}")
            return []


# 테스트 코드
if __name__ == "__main__":
    handler = NotionHandler()
    
    # 테스트: 더미 데이터 추가
    test_title = "테스트 포스트"
    test_url = "https://test.com/test-post"
    test_date = datetime.now().strftime("%Y-%m-%d")
    test_platform = "테스트"
    
    print("=== Notion Handler 테스트 ===")
    success = handler.add_content(test_title, test_url, test_date, test_platform)
    
    if success:
        print("\n✅ 테스트 성공!")
    else:
        print("\n⚠️  이미 존재하거나 추가 실패")
    
    # 데이터 조회 테스트
    print("\n=== 최근 콘텐츠 조회 ===")
    contents = handler.get_all_contents(days=30)
    for content in contents[:5]:  # 최근 5개만 출력
        print(f"- {content['title']} ({content['platform']}) - {content['published_date']}")
