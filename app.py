import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 페이지 기본 설정
st.set_page_config(
    page_title="KGC 마케팅 실시간 대시보드",
    page_icon="🔴",
    layout="wide"
)

st.sidebar.header("⚙️ 데이터 연동 설정")
# 제공해주신 ID를 포함한 전체 URL 생성
default_url = "https://docs.google.com/spreadsheets/d/1GDlaHxGJtu84gCHzaSdCWNq89ufnJ0mMDyMvRW2uxmQ/edit#gid=0"

sheet_url = st.sidebar.text_input(
    "구글 스프레드시트 URL",
    value=default_url,
    help="분석하고자 하는 구글 시트의 전체 URL을 입력하세요."
)

data_load_success = False
df = pd.DataFrame()

try:
    if sheet_url:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # 데이터 로드 (ttl=600: 10분간 캐시 유지)
        df = conn.read(spreadsheet=sheet_url, ttl=600)
        if not df.empty:
            data_load_success = True
    else:
        st.warning("⚠️ 왼쪽 사이드바에 구글 시트 URL을 입력해주세요.")
except Exception as e:
    st.error(f"⚠️ 데이터 연결 실패: {e}")
    st.info("💡 시트의 [공유] 설정이 '링크가 있는 모든 사용자(뷰어)'로 되어 있는지 확인해 주세요.")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-left: 5px solid #c62828;
    }
    .report-header {
        background: linear-gradient(135deg, #c62828 0%, #ef5350 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
    }
    .section-title {
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-weight: 800;
        color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="report-header">
        <p style="font-weight: 600; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.1em;">REAL-TIME MARKETING INSIGHT DASHBOARD</p>
        <h1 style="color: white; margin: 0; font-size: 2.2rem;">에브리타임 밸런스 실시간 마케팅 통찰</h1>
    </div>
    """, unsafe_allow_html=True)

if data_load_success:
    # 1. KPI 지표 요약
    # 데이터 구조: Type이 KPI인 행 필터링
    kpi_df = df[df['Type'] == 'KPI']
    
    col1, col2, col3 = st.columns(3)
    
    try:
        with col1:
            val = kpi_df[kpi_df['Name'] == '수도권성장']['Value'].values[0]
            delta = kpi_df[kpi_df['Name'] == '수도권성장']['Delta'].values[0]
            st.metric(label="수도권 판매 성장", value=f"+{val}%", delta=delta)
            
        with col2:
            val = kpi_df[kpi_df['Name'] == '2030비중']['Value'].values[0]
            st.metric(label="2030 구매 비중", value=f"{val}%", delta="핵심 타겟 안착")
            
        with col3:
            val = kpi_df[kpi_df['Name'] == '아웃도어']['Value'].values[0]
            st.metric(label="아웃도어 언급량", value=f"+{val}%", delta="급증세")
    except Exception:
        st.info("💡 KPI 데이터를 로드 중입니다. 시트의 컬럼명과 데이터를 확인해주세요.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. 지역 및 연령 분포 차트
    left, right = st.columns(2)
    
    with left:
        st.markdown('<h3 class="section-title">📍 지역별 판매 현황</h3>', unsafe_allow_html=True)
        region_df = df[df['Type'] == 'Region']
        if not region_df.empty:
            fig_sales = px.bar(region_df, x='Name', y='Value', 
                              color='Value', color_continuous_scale='Reds',
                              labels={'Value': '증감률(%)', 'Name': '지역'})
            fig_sales.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_sales, use_container_width=True)
        
    with right:
        st.markdown('<h3 class="section-title">👥 고객 인구통계 비중</h3>', unsafe_allow_html=True)
        age_df = df[df['Type'] == 'Age']
        if not age_df.empty:
            fig_age = px.pie(age_df, values='Value', names='Name',
                            hole=0.5, color_discrete_sequence=['#fbc02d', '#e2e8f0'])
            fig_age.update_layout(height=350, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_age, use_container_width=True)

    # 3. 고객 VOC 섹션
    st.markdown('<h3 class="section-title">💬 실시간 고객 VOC 요약</h3>', unsafe_allow_html=True)
    voc_df = df[df['Type'] == 'VOC'][['Content', 'Sentiment']]
    if not voc_df.empty:
        st.dataframe(voc_df, use_container_width=True, hide_index=True)

    st.info("💡 **팀장 가이드**: 구글 시트에서 수치를 변경한 후 앱을 새로고침(R)하면 대시보드에 즉시 반영됩니다.")

else:
    st.warning("⚠️ 데이터를 불러오지 못했습니다. 시트 주소를 확인하거나 공유 설정을 체크해주세요.")
