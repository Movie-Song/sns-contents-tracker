import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

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
        # 중복 체크
        if self.is_url_exists(url):
            print(f"⚠️  이미 존재하는 URL: {url}")
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
                    "url": url
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
            print(f"✅ 추가 완료: {title} ({platform})")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 추가 실패: {title}")
            print(f"   에러: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"   응답: {e.response.text}")
            return False
    
    def is_url_exists(self, url: str) -> bool:
        """
        URL이 이미 데이터베이스에 존재하는지 확인합니다.
        
        Args:
            url: 확인할 URL
        
        Returns:
            bool: 존재 여부
        """
        query_url = f"{self.base_url}/databases/{self.database_id}/query"
        payload = {
            "filter": {
                "property": "URL",
                "url": {
                    "equals": url
                }
            }
        }
        
        try:
            response = requests.post(query_url, headers=self.headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            return len(results) > 0
        except requests.exceptions.RequestException as e:
            print(f"⚠️  URL 중복 체크 실패: {str(e)}")
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
