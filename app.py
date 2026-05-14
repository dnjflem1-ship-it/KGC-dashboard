import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="KGC 마케팅 실시간 대시보드",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main { background-color: #f4f7f9; }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #c62828;
        transition: transform 0.2s;
    }
    
    /* Header Styling */
    .report-header {
        background: linear-gradient(135deg, #b71c1c 0%, #ef5350 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 20px rgba(198, 40, 40, 0.2);
    }
    
    .section-title {
        border-left: 5px solid #c62828;
        padding-left: 15px;
        margin: 30px 0 15px 0;
        font-weight: 700;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ 시스템 설정")
default_url = "https://docs.google.com/spreadsheets/d/1GDlaHxGJtu84gCHzaSdCWNq89ufnJ0mMDyMvRW2uxmQ/edit#gid=0"

sheet_url = st.sidebar.text_input(
    "구글 스프레드시트 URL",
    value=default_url,
    help="분석할 구글 시트의 URL을 입력하세요."
)

if st.sidebar.button("🔄 데이터 강제 새로고침"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=600)
def load_data(url):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        data = conn.read(spreadsheet=url)
        # 컬럼명 앞뒤 공백 제거 (KeyError 방지 핵심)
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except Exception as e:
        return e

data_load_success = False
df = pd.DataFrame()

if sheet_url:
    result = load_data(sheet_url)
    if isinstance(result, Exception):
        st.error(f"⚠️ 데이터 연결 실패: {result}")
    else:
        df = result
        # 필수 컬럼 존재 여부 확인
        required_cols = ['Type', 'Name', 'Value']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if not missing_cols:
            data_load_success = True
        else:
            st.error(f"⚠️ 시트 형식 오류: '{', '.join(missing_cols)}' 컬럼을 찾을 수 없습니다.")
            st.info("💡 구글 시트의 첫 번째 줄(헤더)에 **Type, Name, Value, Delta, Content, Sentiment** 컬럼이 있는지 확인해주세요.")
            with st.expander("현재 로드된 컬럼 보기"):
                st.write(list(df.columns))

st.markdown("""
    <div class="report-header">
        <p style="font-weight: 300; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.2em;">KGC GINSENG CORP. REAL-TIME INSIGHT</p>
        <h1 style="color: white; margin: 0; font-size: 2.8rem; font-weight: 700;">정관장 에브리타임 밸런스 마케팅 대시보드</h1>
    </div>
    """, unsafe_allow_html=True)

if data_load_success:
    # 1. KPI 섹션
    kpi_df = df[df['Type'] == 'KPI']
    col1, col2, col3 = st.columns(3)
    
    def get_val(name, target_col='Value'):
        try:
            val = kpi_df[kpi_df['Name'] == name][target_col].values[0]
            return val
        except:
            return None

    with col1:
        val = get_val('수도권성장')
        delta = get_val('수도권성장', 'Delta')
        st.metric(label="📈 수도권 판매 성장률", value=f"+{val}%" if val else "N/A", delta=delta)

    with col2:
        val = get_val('2030비중')
        st.metric(label="👥 2030 구매 고객 비중", value=f"{val}%" if val else "N/A", delta="핵심 타겟")

    with col3:
        val = get_val('아웃도어')
        st.metric(label="🏔️ 아웃도어 키워드 언급", value=f"+{val}%" if val else "N/A", delta="급증세")

    # 2. 차트 섹션
    st.markdown("<br>", unsafe_allow_html=True)
    row2_left, row2_right = st.columns(2)
    
    with row2_left:
        st.markdown('<h3 class="section-title">📍 지역별 판매 현황 (YoY)</h3>', unsafe_allow_html=True)
        region_df = df[df['Type'] == 'Region']
        if not region_df.empty:
            fig_sales = px.bar(region_df, x='Name', y='Value', color='Value',
                             color_continuous_scale=['#ffcdd2', '#c62828'])
            fig_sales.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=380)
            st.plotly_chart(fig_sales, use_container_width=True)
            
    with row2_right:
        st.markdown('<h3 class="section-title">📊 연령대별 고객 분포</h3>', unsafe_allow_html=True)
        age_df = df[df['Type'] == 'Age']
        if not age_df.empty:
            fig_age = px.pie(age_df, values='Value', names='Name', hole=0.6,
                           color_discrete_sequence=['#c62828', '#e0e0e0', '#ff8a80', '#b0bec5'])
            fig_age.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_age, use_container_width=True)

    # 3. VOC 섹션
    st.markdown('<h3 class="section-title">💬 실시간 고객의 소리 (VOC)</h3>', unsafe_allow_html=True)
    voc_df = df[df['Type'] == 'VOC'].copy()
    if not voc_df.empty:
        # 필요한 컬럼만 추출하여 표시
        display_cols = [c for c in ['Content', 'Sentiment'] if c in voc_df.columns]
        st.dataframe(voc_df[display_cols], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption(f"최근 업데이트: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | KGC Marketing Intelligence Team")
else:
    st.info("💡 데이터 로드를 대기 중이거나 시트 설정이 올바르지 않습니다.")
