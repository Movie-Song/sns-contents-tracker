#!/usr/bin/env python3
"""
SNS Content Tracker - 메인 실행 파일

모든 플랫폼에서 콘텐츠를 수집하고 Notion 데이터베이스에 저장합니다.
"""

import os
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
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return
    
    # 통계 변수
    total_new = 0
    total_existing = 0
    total_errors = 0
    
    # ===========================================
    # 티스토리 블로그 크롤링
    # ===========================================
    print("📘 티스토리 블로그 수집 중...")
    print("-" * 60)
    
    # GitHub Secrets에서 티스토리 블로그 URL들 가져오기 (여러 블로그 지원)
    tistory_blogs_str = os.getenv('TISTORY_BLOGS')
    
    if not tistory_blogs_str:
        print("⚠️  TISTORY_BLOGS 환경변수가 설정되지 않았습니다.")
        print("   - GitHub Repository Settings → Secrets → Actions에서")
        print("   - TISTORY_BLOGS 변수를 추가해주세요")
        print("   - 여러 블로그는 콤마로 구분: https://blog1.tistory.com,https://blog2.tistory.com\n")
    else:
        # 콤마로 구분된 블로그 URL들을 리스트로 변환 (공백 제거)
        tistory_urls = [url.strip() for url in tistory_blogs_str.split(',')]
        
        print(f"📋 총 {len(tistory_urls)}개의 티스토리 블로그 수집 예정")
        print(f"   블로그 목록: {', '.join(tistory_urls)}\n")
        
        # 각 티스토리 블로그별로 처리
        for blog_idx, tistory_url in enumerate(tistory_urls, 1):
            print(f"📘 [{blog_idx}/{len(tistory_urls)}] {tistory_url} 처리 중...")
            print("-" * 40)
            
            try:
                tistory = TistoryScraper(tistory_url)
                
                # 최근 100개 포스트 가져오기
                print(f"🔍 RSS 피드 수집 중... ({tistory_url}/rss)")
                posts = tistory.fetch_posts(limit=100)
                print(f"📝 RSS에서 {len(posts)}개 포스트 발견\n")
                
                if not posts:
                    print("⚠️  수집된 포스트가 없습니다.")
                    print("   - RSS 피드 URL이 올바른지 확인해주세요")
                    print("   - 블로그에 게시된 글이 있는지 확인해주세요\n")
                
                # 각 포스트 처리
                for i, post in enumerate(posts, 1):
                    print(f"[{i}/{len(posts)}] 처리 중: {post['title'][:40]}...")
                    
                    try:
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
                            
                    except Exception as e:
                        print(f"   ❌ 처리 중 오류: {str(e)}")
                        total_errors += 1
                
                print(f"✅ {tistory_url} 처리 완료\n")
                
            except Exception as e:
                print(f"❌ {tistory_url} 스크래핑 실패: {e}")
                print("   - 블로그 URL이 올바른지 확인해주세요")
                print("   - 네트워크 연결을 확인해주세요\n")
                total_errors += 1
    
    # ===========================================
    # 향후 추가할 플랫폼들
    # ===========================================
    # 
    # print("📗 [3/5] 네이버 블로그 수집 중...")
    # naver = NaverBlogScraper("your-blog-id")
    # ...
    # 
    # print("📙 [4/5] 워드프레스 수집 중...")
    # wordpress = WordPressScraper("https://yourblog.com")
    # ...
    # 
    # print("📰 [5/5] 뉴스레터 수집 중...")
    # newsletter = NewsletterScraper("your-substack-url")
    # ...
    
    # ===========================================
    # 최종 결과 출력
    # ===========================================
    print("=" * 60)
    print("📊 수집 완료!")
    print(f"   ✅ 새로 추가: {total_new}개")
    print(f"   ⏭️  이미 존재: {total_existing}개")
    
    if total_errors > 0:
        print(f"   ❌ 오류 발생: {total_errors}개")
    
    print(f"   📝 총 처리: {total_new + total_existing + total_errors}개")
    print("=" * 60)
    print()
    
    # 최근 데이터 확인
    if total_new > 0 or total_existing > 0:
        print("📋 최근 5개 콘텐츠:")
        print("-" * 60)
        try:
            recent_contents = notion.get_all_contents(days=30)
            
            if recent_contents:
                for i, content in enumerate(recent_contents[:5], 1):
                    print(f"{i}. [{content['platform']}] {content['title'][:50]}")
                    print(f"   📅 {content['published_date']} | 🔗 {content['url'][:50]}...")
                    print()
            else:
                print("   (조회된 콘텐츠가 없습니다)\n")
                
        except Exception as e:
            print(f"   ⚠️  최근 콘텐츠 조회 실패: {e}\n")
    
    print("✨ 완료!")
    
    # 다음 실행 시간 안내
    print(f"\n💡 다음 자동 실행은 GitHub Actions에 설정된 스케줄에 따라 진행됩니다.")

if __name__ == "__main__":
    main()
