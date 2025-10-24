import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from datetime import datetime, timedelta
import os
import pytz
from notion_handler import NotionHandler

# 서울 타임존 설정
SEOUL_TZ = pytz.timezone('Asia/Seoul')

# Streamlit Secrets를 환경 변수로 설정
if "NOTION_API_KEY" in st.secrets:
    os.environ["NOTION_API_KEY"] = st.secrets["NOTION_API_KEY"]
    os.environ["DATABASE_ID"] = st.secrets["DATABASE_ID"]

# 페이지 설정
st.set_page_config(
    page_title="콘텐츠 활동 히트맵",
    page_icon="📊",
    layout="wide"
)

# 스타일
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 콘텐츠 활동 히트맵")
st.markdown("---")

@st.cache_data(ttl=86400)  # 24시간 캐시
def load_data():
    """Notion에서 데이터를 불러옵니다."""
    try:
        notion = NotionHandler()
        contents = notion.get_all_contents(days=365)
        
        if not contents:
            return pd.DataFrame()
        
        # DataFrame 생성
        df = pd.DataFrame(contents)
        
        # 날짜 파싱
        df['published_date'] = df['published_date'].apply(
            lambda x: str(x).split('T')[0] if 'T' in str(x) else str(x)
        )
        df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')
        df = df.dropna(subset=['published_date'])
        
        # 날짜별 카운트
        date_counts = df.groupby('published_date').size().reset_index(name='count')
        date_counts = date_counts.set_index('published_date')
        
        return date_counts
    except Exception as e:
        st.error(f"❌ 데이터 로드 실패: {str(e)}")
        return pd.DataFrame()

def create_heatmap(df_counts):
    """GitHub 스타일의 히트맵을 생성합니다 (오늘이 가장 끝에 오도록)."""
    # 서울 시간 기준 오늘
    seoul_now = datetime.now(SEOUL_TZ)
    end_date = pd.Timestamp(year=seoul_now.year, month=seoul_now.month, day=seoul_now.day)
    
    # 오늘 기준으로 정확히 1년 전 (365일)
    start_date = end_date - pd.Timedelta(days=364)
    
    # 시작일을 가장 가까운 일요일로 조정 (거슬러 올라가기)
    # Python: 월요일=0, 일요일=6
    start_weekday = start_date.weekday()
    days_to_sunday = (start_weekday + 1) % 7  # 가장 가까운 일요일까지 거슬러 올라가기
    if days_to_sunday > 0:
        start_date = start_date - pd.Timedelta(days=days_to_sunday)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    # 달력 DataFrame
    df_calendar = pd.DataFrame(index=date_range)
    df_calendar["Count"] = 0
    
    # Notion 데이터 반영 (날짜를 정규화하여 매칭)
    for date_i, row in df_counts.iterrows():
        # 날짜를 시간 정보 없이 정규화
        date_normalized = pd.Timestamp(year=date_i.year, month=date_i.month, day=date_i.day)
        if date_normalized in df_calendar.index:
            df_calendar.loc[date_normalized, "Count"] = row["count"]
    
    # 깃허브 스타일 요일 계산 (일요일=0, 월요일=1, ..., 토요일=6)
    df_calendar["Weekday"] = (df_calendar.index.weekday + 1) % 7
    
    # 주 계산 (일요일 기준)
    df_calendar["WeekIndex"] = ((df_calendar.index - start_date).days // 7).astype(int)
    
    # 피벗 테이블 (행=요일, 열=주차)
    pivot = df_calendar.pivot(index="Weekday", columns="WeekIndex", values="Count")
    
    # 클리핑
    pivot = pivot.fillna(0)
    pivot = pivot.clip(upper=5)
    
    # GitHub 스타일 색상
    colors = ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39", "#0D4429"]
    cmap = mcolors.ListedColormap(colors)
    boundaries = [0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5]
    norm = mcolors.BoundaryNorm(boundaries, ncolors=cmap.N)
    
    # 작은 셀 크기로 히트맵 그리기
    fig, ax = plt.subplots(figsize=(16, 2.5))
    
    # 히트맵
    mesh = ax.pcolormesh(pivot, cmap=cmap, norm=norm, edgecolors="white", linewidth=1)
    
    # 정사각형 셀
    ax.set_aspect('equal')
    
    # 요일 레이블 (왼쪽) - 깃허브 스타일: Sun, Mon, Tue, Wed, Thu, Fri, Sat
    weekday_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
    ax.set_yticklabels(weekday_labels, fontsize=8, ha='right')
    ax.tick_params(left=False, bottom=False)
    
    # 월 레이블 (상단)
    month_positions = []
    month_labels = []
    prev_month = None
    
    for week_idx in range(len(pivot.columns)):
        week_dates = df_calendar[df_calendar["WeekIndex"] == week_idx]
        if not week_dates.empty:
            first_date = week_dates.index[0]
            current_month = first_date.month
            
            if current_month != prev_month:
                month_positions.append(week_idx + 0.5)
                month_labels.append(first_date.strftime('%b'))
                prev_month = current_month
    
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(month_positions)
    ax2.set_xticklabels(month_labels, fontsize=8)
    ax2.tick_params(top=False)
    
    # 하단 x축 제거
    ax.set_xticks([])
    
    # 테두리 제거
    for spine in ax.spines.values():
        spine.set_visible(False)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    
    # 투명 배경
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    plt.tight_layout()
    
    return fig, df_calendar

# 데이터 로드
with st.spinner("📡 데이터 불러오는 중..."):
    df_counts = load_data()

if df_counts.empty:
    st.warning("⚠️ 표시할 데이터가 없습니다. Notion 데이터베이스를 확인해주세요.")
    st.stop()

# 히트맵 생성 및 표시
fig, df_calendar = create_heatmap(df_counts)
st.pyplot(fig, use_container_width=False)

# 하단 캡션
st.markdown("""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>
        <span style='font-size: 11px; color: #586069; margin-right: 5px;'>Less</span>
        <span style='display: inline-block; width: 10px; height: 10px; background-color: #EBEDF0; margin: 0 2px; border: 1px solid #d1d5da;'></span>
        <span style='display: inline-block; width: 10px; height: 10px; background-color: #9BE9A8; margin: 0 2px; border: 1px solid #d1d5da;'></span>
        <span style='display: inline-block; width: 10px; height: 10px; background-color: #40C463; margin: 0 2px; border: 1px solid #d1d5da;'></span>
        <span style='display: inline-block; width: 10px; height: 10px; background-color: #30A14E; margin: 0 2px; border: 1px solid #d1d5da;'></span>
        <span style='display: inline-block; width: 10px; height: 10px; background-color: #216E39; margin: 0 2px; border: 1px solid #d1d5da;'></span>
        <span style='display: inline-block; width: 10px; height: 10px; background-color: #0D4429; margin: 0 2px; border: 1px solid #d1d5da;'></span>
        <span style='font-size: 11px; color: #586069; margin-left: 5px;'>More</span>
    </div>
""", unsafe_allow_html=True)

# 통계 정보
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

total_posts = int(df_calendar["Count"].sum())
active_days = int((df_calendar["Count"] > 0).sum())
max_posts_day = int(df_calendar["Count"].max())
avg_posts_week = round(df_calendar["Count"].sum() / 52, 1)

with col1:
    st.metric("📝 총 콘텐츠", f"{total_posts}개")

with col2:
    st.metric("📅 활동 일수", f"{active_days}일")

with col3:
    st.metric("🔥 최대 (하루)", f"{max_posts_day}개")

with col4:
    st.metric("📊 주평균", f"{avg_posts_week}개")

# 최근 활동
st.markdown("---")
st.subheader("📋 최근 활동")

recent = df_calendar[df_calendar["Count"] > 0].tail(10)
if not recent.empty:
    for date_idx in reversed(recent.index):
        count = int(recent.loc[date_idx, "Count"])
        date_str = date_idx.strftime("%Y-%m-%d")
        st.write(f"✏️ **{date_str}**: {count}개 콘텐츠 발행")
else:
    st.info("최근 활동이 없습니다.")

# 새로고침 버튼
st.markdown("---")
if st.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

# 푸터
st.markdown("---")
seoul_now = datetime.now(SEOUL_TZ)
st.caption(f"💡 Notion 데이터베이스와 자동 동기화됩니다. (24시간 캐시) | 🕐 서울 기준: {seoul_now.strftime('%Y-%m-%d %H:%M')}")
