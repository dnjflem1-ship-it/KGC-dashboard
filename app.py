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
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .main { background-color: #f4f7f9; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 6px solid #c62828;
    }
    .report-header {
        background: linear-gradient(135deg, #b71c1c 0%, #ef5350 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(198, 40, 40, 0.2);
    }
    .section-title {
        border-left: 5px solid #c62828;
        padding-left: 15px;
        margin: 30px 0 15px 0;
        font-weight: 700;
        color: #2c3e50;
    }
    .guide-box {
        background-color: #fff3f3;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffcdd2;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### ⚙️ 시스템 설정")
default_url = "https://docs.google.com/spreadsheets/d/1GDlaHxGJtu84gCHzaSdCWNq89ufnJ0mMDyMvRW2uxmQ/edit#gid=0"

sheet_url = st.sidebar.text_input(
    "구글 스프레드시트 URL",
    value=default_url,
    help="연결할 구글 시트 주소를 입력하세요."
)

if st.sidebar.button("🔄 데이터 즉시 새로고침"):
    st.cache_data.clear()
    st.rerun()

@st.cache_data(ttl=300)
def load_and_clean_data(url):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        data = conn.read(spreadsheet=url)
        # 모든 컬럼명에서 공백 제거 및 대문자화 하여 표준화
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except Exception as e:
        return e

def map_columns(df_cols):
    """한글/영어 헤더를 시스템 표준 헤더로 매핑"""
    mapping = {}
    col_map_rules = {
        'Type': ['Type', '구분', '타입', '유형', '종류'],
        'Name': ['Name', '항목', '지역', '연령', '이름'],
        'Value': ['Value', '값', '수치', '비율', '데이터'],
        'Delta': ['Delta', '변동', '증감', '비고'],
        'Content': ['Content', '내용', '텍스트', '의견', 'VOC'],
        'Sentiment': ['Sentiment', '감성', '반응', '점수']
    }
    
    for standard, aliases in col_map_rules.items():
        for col in df_cols:
            if col in aliases or col.lower() in [a.lower() for a in aliases]:
                mapping[standard] = col
                break
    return mapping

data_load_success = False
mapped_df = pd.DataFrame()

if sheet_url:
    df = load_and_clean_data(sheet_url)
    if isinstance(df, Exception):
        st.error(f"⚠️ 시트 연결 실패: {df}")
    else:
        col_map = map_columns(df.columns)
        required = ['Type', 'Name', 'Value']
        
        if all(k in col_map for k in required):
            # 표준 컬럼명으로 변경된 새 데이터프레임 생성
            mapped_df = df.rename(columns={v: k for k, v in col_map.items()})
            data_load_success = True
        else:
            # 에러 발생 시 가이드 출력
            st.markdown(f"""
            <div class="guide-box">
                <h4 style="color:#c62828; margin-top:0;">⚠️ 시트 형식 불일치 (해결 방법)</h4>
                <p>구글 시트의 첫 번째 줄(헤더)을 아래 예시 중 하나로 수정해주세요.</p>
                <table style="width:100%; border-collapse: collapse;">
                    <tr style="background:#fce4ec;">
                        <th style="border:1px solid #ffcdd2; padding:8px;">표준 헤더 (추천)</th>
                        <td style="border:1px solid #ffcdd2; padding:8px;">Type, Name, Value, Delta, Content, Sentiment</td>
                    </tr>
                    <tr>
                        <th style="border:1px solid #ffcdd2; padding:8px;">한글 헤더 (허용)</th>
                        <td style="border:1px solid #ffcdd2; padding:8px;">구분, 항목, 값, 변동, 내용, 반응</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("🔍 현재 시트에서 인식된 컬럼 보기"):
                st.write(list(df.columns))

st.markdown("""
    <div class="report-header">
        <p style="font-weight: 300; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.2em;">KGC GINSENG CORP. REAL-TIME INSIGHT</p>
        <h1 style="color: white; margin: 0; font-size: 2.8rem; font-weight: 700;">정관장 에브리타임 밸런스 마케팅 대시보드</h1>
    </div>
    """, unsafe_allow_html=True)

if data_load_success:
    # KPI 요약 섹션
    kpi_data = mapped_df[mapped_df['Type'].str.contains('KPI', na=False)]
    c1, c2, c3 = st.columns(3)
    
    def get_safe_val(name, col='Value'):
        try:
            row = kpi_data[kpi_data['Name'] == name]
            return row[col].values[0] if not row.empty else None
        except: return None

    with c1:
        v, d = get_safe_val('수도권성장'), get_safe_val('수도권성장', 'Delta')
        st.metric("📈 수도권 판매 성장률", f"+{v}%" if v else "데이터 없음", d)
    with c2:
        v = get_safe_val('2030비중')
        st.metric("👥 2030 구매 고객 비중", f"{v}%" if v else "데이터 없음", "핵심 타겟")
    with c3:
        v = get_safe_val('아웃도어')
        st.metric("🏔️ 아웃도어 키워드 언급", f"+{v}%" if v else "데이터 없음", "급증세")

    # 차트 섹션
    st.markdown("<br>", unsafe_allow_html=True)
    l_col, r_col = st.columns(2)
    
    with l_col:
        st.markdown('<h3 class="section-title">📍 지역별 판매 현황</h3>', unsafe_allow_html=True)
        reg_df = mapped_df[mapped_df['Type'].str.contains('Region|지역', na=False)]
        if not reg_df.empty:
            fig = px.bar(reg_df, x='Name', y='Value', color='Value', color_continuous_scale='Reds')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)

    with r_col:
        st.markdown('<h3 class="section-title">📊 연령대별 고객 분포</h3>', unsafe_allow_html=True)
        age_df = mapped_df[mapped_df['Type'].str.contains('Age|연령', na=False)]
        if not age_df.empty:
            fig = px.pie(age_df, values='Value', names='Name', hole=0.5, color_discrete_sequence=px.colors.sequential.Reds_r)
            fig.update_layout(height=350, margin=dict(t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

    # VOC 섹션
    st.markdown('<h3 class="section-title">💬 실시간 고객의 소리 (VOC)</h3>', unsafe_allow_html=True)
    voc_df = mapped_df[mapped_df['Type'].str.contains('VOC', na=False)]
    if not voc_df.empty:
        # 존재하는 컬럼만 표시
        cols_to_show = [c for c in ['Content', 'Sentiment'] if c in voc_df.columns]
        st.dataframe(voc_df[cols_to_show], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.caption(f"최근 동기화: {pd.Timestamp.now().strftime('%H:%M:%S')} | 데이터 출처: 연결된 구글 스프레드시트")
else:
    st.info("💡 데이터가 올바르게 로드되지 않았습니다. 상단의 가이드에 따라 시트 형식을 확인해주세요.")
