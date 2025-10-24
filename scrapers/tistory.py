import feedparser
from datetime import datetime
from typing import List, Dict

class TistoryScraper:
    """티스토리 블로그의 RSS 피드를 파싱하는 클래스"""
    
    def __init__(self, blog_url: str, blog_name: str = "티스토리"):
        """
        Args:
            blog_url: 티스토리 블로그 URL (예: https://yourblog.tistory.com)
        """
        self.blog_url = blog_url.rstrip('/')
        # 티스토리 RSS 피드 URL
        self.rss_url = f"{self.blog_url}/rss"
        self.platform = blog_name
    
    def fetch_posts(self, limit: int = 50) -> List[Dict]:
        """
        RSS 피드에서 최신 포스트들을 가져옵니다.
        
        Args:
            limit: 가져올 최대 포스트 수 (기본 50개)
        
        Returns:
            List[Dict]: 포스트 정보 리스트
                - title: 제목
                - url: URL
                - published_date: 발행일 (YYYY-MM-DD 형식)
                - platform: 플랫폼 이름
        """
        print(f"🔍 {self.platform} 피드 확인 중: {self.rss_url}")
        
        try:
            # RSS 피드 파싱
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:  # 파싱 에러가 있는 경우
                print(f"⚠️  RSS 피드 파싱 오류: {feed.bozo_exception}")
                return []
            
            if not feed.entries:
                print(f"⚠️  피드에 포스트가 없습니다.")
                return []
            
            posts = []
            for entry in feed.entries[:limit]:
                # 제목
                title = entry.get('title', '제목 없음')
                
                # URL
                url = entry.get('link', '')
                
                # 발행일 파싱
                published_date = self._parse_date(entry)
                
                if url and published_date:
                    posts.append({
                        'title': title,
                        'url': url,
                        'published_date': published_date,
                        'platform': self.platform
                    })
            
            print(f"✅ {len(posts)}개의 포스트를 찾았습니다.")
            return posts
            
        except Exception as e:
            print(f"❌ RSS 피드 가져오기 실패: {str(e)}")
            return []
    
    def _parse_date(self, entry) -> str:
        """
        RSS 엔트리에서 날짜를 파싱하여 YYYY-MM-DD 형식으로 반환합니다.
        
        Args:
            entry: feedparser entry 객체
        
        Returns:
            str: YYYY-MM-DD 형식의 날짜 문자열
        """
        # published_parsed 또는 updated_parsed 사용
        date_tuple = entry.get('published_parsed') or entry.get('updated_parsed')
        
        if date_tuple:
            try:
                dt = datetime(*date_tuple[:6])
                return dt.strftime("%Y-%m-%d")
            except:
                pass
        
        # 파싱 실패 시 None 반환
        return None
    
    def get_recent_posts(self, days: int = 30) -> List[Dict]:
        """
        최근 N일 이내의 포스트만 필터링하여 반환합니다.
        
        Args:
            days: 조회할 일수 (기본 30일)
        
        Returns:
            List[Dict]: 최근 포스트 정보 리스트
        """
        from datetime import timedelta
        
        all_posts = self.fetch_posts()
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        recent_posts = [
            post for post in all_posts 
            if post['published_date'] >= cutoff_date
        ]
        
        print(f"📅 최근 {days}일 이내 포스트: {len(recent_posts)}개")
        return recent_posts


# 테스트 코드
if __name__ == "__main__":
    # 테스트용 블로그 URL
    test_blog_url = "https://pro-editor.tistory.com"
    
    print("=== 티스토리 스크래퍼 테스트 ===\n")
    
    scraper = TistoryScraper(test_blog_url)
    
    # 최근 10개 포스트 가져오기
    posts = scraper.fetch_posts(limit=10)
    
    if posts:
        print(f"\n📝 최근 포스트 목록:")
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title']}")
            print(f"   URL: {post['url']}")
            print(f"   날짜: {post['published_date']}\n")
    else:
        print("\n⚠️  포스트를 가져올 수 없습니다.")
