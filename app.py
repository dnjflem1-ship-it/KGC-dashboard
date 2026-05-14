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
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
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
        margin: 30px 0 20px 0;
        font-weight: 700;
        color: #2c3e50;
    }
    
    /* Sidebar Styling */
    .stSidebar {
        background-color: #ffffff;
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

# 데이터 새로고침 버튼
if st.sidebar.button("🔄 데이터 강제 새로고침"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.info("💡 **팁**: 구글 시트에서 수치를 변경한 후 위 버튼을 누르면 실시간으로 반영됩니다.")

@st.cache_data(ttl=600)
def load_data(url):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        data = conn.read(spreadsheet=url)
        return data
    except Exception as e:
        return e

data_load_success = False
df = pd.DataFrame()

if sheet_url:
    result = load_data(sheet_url)
    if isinstance(result, Exception):
        st.error(f"⚠️ 데이터 연결 실패: {result}")
        st.info("💡 시트의 [공유] 설정이 '링크가 있는 모든 사용자(뷰어)'로 되어 있는지 확인해 주세요.")
    else:
        df = result
        if not df.empty:
            data_load_success = True
else:
    st.warning("⚠️ 왼쪽 사이드바에 구글 시트 URL을 입력해주세요.")

st.markdown("""
    <div class="report-header">
        <p style="font-weight: 300; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.2em;">KGC GINSENG CORP. REAL-TIME INSIGHT</p>
        <h1 style="color: white; margin: 0; font-size: 2.8rem; font-weight: 700;">정관장 에브리타임 밸런스 마케팅 대시보드</h1>
    </div>
    """, unsafe_allow_html=True)

if data_load_success:
    # KPI Section
    kpi_df = df[df['Type'] == 'KPI']
    
    col1, col2, col3 = st.columns(3)
    
    def get_kpi_value(name, col_name='Value'):
        try:
            return kpi_df[kpi_df['Name'] == name][col_name].values[0]
        except:
            return None

    with col1:
        val = get_kpi_value('수도권성장')
        delta = get_kpi_value('수도권성장', 'Delta')
        if val is not None:
            st.metric(label="📈 수도권 판매 성장률", value=f"+{val}%", delta=delta)
        else:
            st.info("수도권성장 데이터 없음")

    with col2:
        val = get_kpi_value('2030비중')
        if val is not None:
            st.metric(label="👥 2030 구매 고객 비중", value=f"{val}%", delta="목표치 달성 중")
        else:
            st.info("2030비중 데이터 없음")

    with col3:
        val = get_kpi_value('아웃도어')
        if val is not None:
            st.metric(label="🏔️ 아웃도어 키워드 언급", value=f"+{val}%", delta="급증세", delta_color="normal")
        else:
            st.info("아웃도어 데이터 없음")

    st.markdown("<br>", unsafe_allow_html=True)
    row2_left, row2_right = st.columns(2)
    
    with row2_left:
        st.markdown('<h3 class="section-title">📍 지역별 판매 현황 (YoY)</h3>', unsafe_allow_html=True)
        region_df = df[df['Type'] == 'Region']
        if not region_df.empty:
            fig_sales = px.bar(
                region_df, x='Name', y='Value',
                color='Value',
                color_continuous_scale=['#ffcdd2', '#c62828'],
                labels={'Value': '성장률(%)', 'Name': '지역'}
            )
            fig_sales.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400,
                xaxis_title="",
                yaxis_title="성장률 (%)"
            )
            st.plotly_chart(fig_sales, use_container_width=True)
        else:
            st.info("지역별 데이터를 찾을 수 없습니다.")
            
    with row2_right:
        st.markdown('<h3 class="section-title">📊 연령대별 고객 분포</h3>', unsafe_allow_html=True)
        age_df = df[df['Type'] == 'Age']
        if not age_df.empty:
            fig_age = px.pie(
                age_df, values='Value', names='Name',
                hole=0.6,
                color_discrete_sequence=['#c62828', '#e0e0e0', '#ff8a80', '#b0bec5']
            )
            fig_age.update_layout(
                height=400,
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("연령대 데이터를 찾을 수 없습니다.")

    st.markdown('<h3 class="section-title">💬 실시간 고객의 소리 (VOC)</h3>', unsafe_allow_html=True)
    voc_df = df[df['Type'] == 'VOC'].copy()
    if not voc_df.empty:
        # 데이터프레임 스타일링
        def color_sentiment(val):
            color = '#e8f5e9' if val == '긍정' else '#ffebee' if val == '부정' else '#ffffff'
            return f'background-color: {color}'

        display_voc = voc_df[['Content', 'Sentiment']].rename(columns={'Content': '의견 내용', 'Sentiment': '감성 분석'})
        st.dataframe(
            display_voc,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.write("표시할 VOC 데이터가 없습니다.")

    # 하단 풋터
    st.markdown("---")
    st.caption(f"최근 업데이트: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | KGC Marketing Intelligence Team")

else:
    if sheet_url:
        st.warning("⚠️ 데이터를 로드했지만 내용이 비어있습니다. 시트의 구성을 확인해주세요.")
