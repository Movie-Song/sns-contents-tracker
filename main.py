#!/usr/bin/env python3
"""
SNS Content Tracker - 메인 실행 파일

모든 플랫폼에서 콘텐츠를 수집하고 Notion 데이터베이스에 저장합니다.
"""

from datetime import datetime
from notion_handler import NotionHandler
from scrapers import TistoryScraper

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 SNS Content Tracker 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Notion Handler 초기화
    try:
        notion = NotionHandler()
        print("✅ Notion 연결 성공\n")
    except ValueError as e:
        print(f"❌ Notion 연결 실패: {e}")
        return
    
    # 통계 변수
    total_new = 0
    total_existing = 0
    
    # ===========================================
    # 1. 티스토리 블로그 크롤링
    # ===========================================
    print("📘 [1/1] 티스토리 블로그 수집 중...")
    print("-" * 60)
    
    tistory_url = "https://pro-editor.tistory.com"
    tistory = TistoryScraper(tistory_url)
    
    # 최근 100개 포스트 가져오기 (중복 체크는 Notion Handler에서 처리)
    posts = tistory.fetch_posts(limit=100)
    
    for post in posts:
        success = notion.add_content(
            title=post['title'],
            url=post['url'],
            published_date=post['published_date'],
            platform=post['platform']
        )
        
        if success:
            total_new += 1
        else:
            total_existing += 1
    
    print()
    
    # ===========================================
    # 향후 추가할 플랫폼들
    # ===========================================
    # 
    # print("📗 [2/5] 네이버 블로그 수집 중...")
    # naver = NaverBlogScraper("your-blog-id")
    # ...
    # 
    # print("📙 [3/5] 워드프레스 수집 중...")
    # wordpress = WordPressScraper("https://yourblog.com")
    # ...
    # 
    # print("📰 [4/5] 뉴스레터 수집 중...")
    # newsletter = NewsletterScraper("your-substack-url")
    # ...
    # 
    # print("🐦 [5/5] 트위터 수집 중...")
    # twitter = TwitterScraper()
    # ...
    
    # ===========================================
    # 최종 결과 출력
    # ===========================================
    print("=" * 60)
    print("📊 수집 완료!")
    print(f"   ✅ 새로 추가된 콘텐츠: {total_new}개")
    print(f"   ⚠️  이미 존재하는 콘텐츠: {total_existing}개")
    print(f"   📝 총 처리: {total_new + total_existing}개")
    print("=" * 60)
    print()
    
    # 최근 데이터 확인
    print("📋 최근 5개 콘텐츠:")
    print("-" * 60)
    recent_contents = notion.get_all_contents(days=30)
    for i, content in enumerate(recent_contents[:5], 1):
        print(f"{i}. [{content['platform']}] {content['title']}")
        print(f"   📅 {content['published_date']}")
        print()
    
    print("✨ 완료!")

if __name__ == "__main__":
    main()
