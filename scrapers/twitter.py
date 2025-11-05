import feedparser
from datetime import datetime
from typing import List, Dict

class TwitterScraper:
    """트위터(X)의 Nitter RSS 피드를 파싱하는 클래스"""
    
    # 작동 가능한 여러 Nitter 인스턴스 (자동 폴백)
    NITTER_INSTANCES = [
        "https://nitter.privacydev.net",
        "https://nitter.net",
        "https://nitter.poast.org",
        "https://nitter.unixfox.eu",
        "https://nitter.cz",
    ]
    
    def __init__(self, username: str, nitter_instance: str = None):
        """
        Args:
            username: 트위터 사용자명 (@ 제외)
            nitter_instance: Nitter 인스턴스 URL (기본: 자동 선택)
        """
        self.username = username.lstrip('@')
        
        # 특정 인스턴스가 지정되면 그것만 사용, 아니면 리스트에서 자동 선택
        if nitter_instance:
            self.nitter_instances = [nitter_instance.rstrip('/')]
        else:
            self.nitter_instances = self.NITTER_INSTANCES
        
        # 계정명을 포함한 플랫폼 이름으로 구분 가능하게 설정
        self.platform = f"Twitter (@{self.username})"
    
    def fetch_posts(self, limit: int = 50) -> List[Dict]:
        """
        RSS 피드에서 최신 트윗들을 가져옵니다.
        여러 Nitter 인스턴스를 순차적으로 시도합니다.
        
        Args:
            limit: 가져올 최대 트윗 수 (기본 50개)
        
        Returns:
            List[Dict]: 트윗 정보 리스트
                - title: 제목 (트윗 내용)
                - url: URL
                - published_date: 발행일 (YYYY-MM-DDTHH:MM:SS 형식)
                - platform: 플랫폼 이름
        """
        last_error = None
        
        # 여러 인스턴스를 순차적으로 시도
        for instance in self.nitter_instances:
            rss_url = f"{instance}/{self.username}/rss"
            print(f"🔍 {self.platform} 피드 확인 중: {rss_url}")
            
            try:
                # RSS 피드 파싱
                feed = feedparser.parse(rss_url)
                
                # 파싱 에러 체크
                if feed.bozo:
                    last_error = f"파싱 오류: {feed.bozo_exception}"
                    print(f"⚠️  이 인스턴스는 작동하지 않습니다: {last_error}")
                    continue
                
                # 엔트리가 없는 경우
                if not feed.entries:
                    last_error = "피드에 트윗이 없습니다"
                    print(f"⚠️  이 인스턴스에서 트윗을 찾을 수 없습니다.")
                    continue
                
                # 성공! 트윗 파싱
                posts = []
                for entry in feed.entries[:limit]:
                    # 제목 (트윗 내용)
                    title = entry.get('title', '내용 없음')
                    
                    # URL - Nitter URL을 Twitter URL로 변환
                    nitter_url = entry.get('link', '')
                    twitter_url = self._convert_to_twitter_url(nitter_url, instance)
                    
                    # 발행일 파싱
                    published_date = self._parse_date(entry)
                    
                    if twitter_url and published_date:
                        posts.append({
                            'title': title,
                            'url': twitter_url,
                            'published_date': published_date,
                            'platform': self.platform
                        })
                
                print(f"✅ {len(posts)}개의 트윗을 찾았습니다. (인스턴스: {instance})")
                return posts
                
            except Exception as e:
                last_error = str(e)
                print(f"⚠️  인스턴스 접속 실패: {last_error}")
                continue
        
        # 모든 인스턴스 실패
        print(f"❌ 모든 Nitter 인스턴스에서 트윗을 가져올 수 없습니다.")
        print(f"   마지막 오류: {last_error}")
        print(f"   시도한 인스턴스: {', '.join(self.nitter_instances)}")
        return []
    
    def _convert_to_twitter_url(self, nitter_url: str, instance: str) -> str:
        """
        Nitter URL을 공식 Twitter URL로 변환합니다.
        
        Args:
            nitter_url: Nitter URL
            instance: 사용된 Nitter 인스턴스
        
        Returns:
            str: Twitter URL
        """
        if not nitter_url:
            return ""
        
        try:
            # nitter.xxx/username/status/123 -> twitter.com/username/status/123
            parts = nitter_url.replace(instance, 'https://twitter.com')
            return parts
        except:
            return nitter_url
    
    def _parse_date(self, entry) -> str:
        """
        RSS 엔트리에서 날짜를 파싱하여 YYYY-MM-DDTHH:MM:SS 형식으로 반환합니다.
        
        Args:
            entry: feedparser entry 객체
        
        Returns:
            str: YYYY-MM-DDTHH:MM:SS 형식의 날짜 문자열
        """
        # published_parsed 또는 updated_parsed 사용
        date_tuple = entry.get('published_parsed') or entry.get('updated_parsed')
        
        if date_tuple:
            try:
                dt = datetime(*date_tuple[:6])
                return dt.strftime("%Y-%m-%dT%H:%M:%S")
            except:
                pass
        
        # 파싱 실패 시 None 반환
        return None
    
    def get_recent_posts(self, days: int = 30) -> List[Dict]:
        """
        최근 N일 이내의 트윗만 필터링하여 반환합니다.
        
        Args:
            days: 조회할 일수 (기본 30일)
        
        Returns:
            List[Dict]: 최근 트윗 정보 리스트
        """
        from datetime import timedelta
        
        all_posts = self.fetch_posts()
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        recent_posts = [
            post for post in all_posts 
            if post['published_date'] >= cutoff_date
        ]
        
        print(f"📅 최근 {days}일 이내 트윗: {len(recent_posts)}개")
        return recent_posts


# 테스트 코드
if __name__ == "__main__":
    import os
    
    # 환경변수에서 트위터 사용자명 가져오기
    test_username = os.getenv('TWITTER_USERNAME', 'elonmusk')
    
    print("=== 트위터 스크래퍼 테스트 ===\n")
    
    scraper = TwitterScraper(test_username)
    
    # 최근 10개 트윗 가져오기
    posts = scraper.fetch_posts(limit=10)
    
    if posts:
        print(f"\n📝 최근 트윗 목록:")
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title'][:80]}...")
            print(f"   URL: {post['url']}")
            print(f"   날짜: {post['published_date']}\n")
    else:
        print("\n⚠️  트윗을 가져올 수 없습니다.")
