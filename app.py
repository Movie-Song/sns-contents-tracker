import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
import os
from notion_handler import NotionHandler

# Streamlit Secrets를 환경 변수로 설정 (Streamlit Cloud용)
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
    .stPlotlyChart {
        display: flex;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 콘텐츠 활동 히트맵")
st.markdown("---")

@st.cache_data(ttl=3600)
def load_data():
    """Notion에서 데이터를 불러오고 처리합니다."""
    try:
        # 디버깅: Secrets 확인
        st.write("🔍 DEBUG: Secrets 확인 중...")
        st.write(f"API Key 존재: {'NOTION_API_KEY' in st.secrets}")
        st.write(f"DB ID 존재: {'DATABASE_ID' in st.secrets}")
        
        notion = NotionHandler()
        contents = notion.get_all_contents(days=365)
        
        # 디버깅: 가져온 데이터 수
        st.write(f"📊 DEBUG: 가져온 콘텐츠 수: {len(contents)}")
        
        if not contents:
            return pd.DataFrame()
        
        df = pd.DataFrame(contents)
        df['published_date'] = pd.to_datetime(df['published_date'])
        
        date_counts = df.groupby('published_date').size().reset_index(name='count')
        date_counts = date_counts.set_index('published_date')
        
        return date_counts
    except Exception as e:
        st.error(f"❌ 데이터 로드 실패: {str(e)}")
        # 상세 에러 출력
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()

def create_heatmap(df_counts):
    """GitHub 스타일의 히트맵을 생성합니다."""
    # 오늘 기준 지난 365일 날짜 범위 생성
    end_date = pd.to_datetime("today").normalize()
    start_date = end_date - pd.Timedelta(days=364)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    
    # 달력용 DataFrame 생성 (기본 Count = 0)
    df_calendar = pd.DataFrame(index=date_range)
    df_calendar["Count"] = 0
    
    # Notion 데이터의 Count를 달력 DataFrame에 반영
    for date_i, row in df_counts.iterrows():
        if date_i in df_calendar.index:
            df_calendar.loc[date_i, "Count"] = row["count"]
    
    # 요일(Weekday)와 주(WeekIndex) 계산
    df_calendar["Weekday"] = df_calendar.index.weekday  # 0: 월요일, 6: 일요일
    df_calendar["WeekIndex"] = ((df_calendar.index - start_date).days // 7).astype(int)
    
    # 피벗 테이블 생성 (행=요일, 열=주차, 값=Count)
    pivot = df_calendar.pivot(index="Weekday", columns="WeekIndex", values="Count")
    
    # Count 값이 5보다 크면 5로 클리핑
    pivot = pivot.clip(upper=5)
    
    # GitHub 스타일 색상 설정
    colors = ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39", "#0D4429"]
    cmap = mcolors.ListedColormap(colors)
    boundaries = [0, 1, 2, 3, 4, 5, 6]
    norm = mcolors.BoundaryNorm(boundaries, ncolors=cmap.N)
    
    # 히트맵 그리기
    fig, ax = plt.subplots(figsize=(20, 4))
    ax.pcolormesh(pivot, cmap=cmap, norm=norm, edgecolors="white", linewidth=2)
    
    # 축 제거
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("off")
    
    # 투명 배경
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    return fig, df_calendar

# 데이터 로드
with st.spinner("📡 데이터 불러오는 중..."):
    df_counts = load_data()

if df_counts.empty:
    st.warning("⚠️ 표시할 데이터가 없습니다. Notion 데이터베이스를 확인해주세요.")
    st.stop()

# 히트맵 생성 및 표시
fig, df_calendar = create_heatmap(df_counts)
st.pyplot(fig)

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
st.caption("💡 Notion 데이터베이스와 자동 동기화됩니다. (1시간 캐시)")
