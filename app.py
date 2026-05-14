import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 페이지 레이아웃 설정
st.set_page_config(
    page_title="KGC 마케팅 통찰 보고서 | 에브리타임 밸런스",
    page_icon="🔴",
    layout="wide"
)

# 브랜드 컬러: Red(#c62828), Gray(#f8fafc)
st.markdown("""
    <style>
    /* 메인 배경색 및 폰트 설정 */
    .main {
        background-color: #f8fafc;
    }
    /* 메트릭 카드 스타일링 */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-left: 5px solid #c62828;
    }
    /* 헤더 섹션 디자인 */
    .report-header {
        background: linear-gradient(135deg, #c62828 0%, #ef5350 100%);
        padding: 2.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(198, 40, 40, 0.3);
    }
    /* 섹션 타이틀 스타일 */
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
        <p style="font-weight: 600; opacity: 0.9; margin-bottom: 0.5rem; letter-spacing: 0.1em;">2026 MARCH WEEK 4 | INTERNAL CONFIDENTIAL</p>
        <h1 style="color: white; margin-top: 0; font-size: 2.5rem;">에브리타임 밸런스 마케팅 통찰 대시보드</h1>
        <p style="font-size: 1.2rem; max-width: 900px; line-height: 1.6;">
            "수도권 2030 세대를 중심으로 리뉴얼 효과가 폭발하고 있습니다. <br>
            <b>아웃도어 키워드</b>의 성장을 기점으로 브랜드 포지셔닝을 확장할 골든타임입니다."
        </p>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="수도권 판매 성장 (CVS)", value="+15%", delta="전주 대비 강세")
with col2:
    st.metric(label="2030 구매 비중", value="45%", delta="핵심 타겟 안착", delta_color="normal")
with col3:
    st.metric(label="아웃도어 키워드 언급", value="+30%", delta="라이프스타일 확장")

st.markdown("<br>", unsafe_allow_html=True)

left_chart, right_chart = st.columns(2)

with left_chart:
    st.markdown('<h3 class="section-title">📍 지역별 판매 변동 (채널 양극화)</h3>', unsafe_allow_html=True)
    sales_data = pd.DataFrame({
        '지역': ['수도권 (CVS 강세)', '지방 (대형마트 정체)'],
        '증감률': [15, -2]
    })
    
    fig_sales = px.bar(
        sales_data, x='지역', y='증감률',
        color='증감률',
        color_continuous_scale=['#94a3b8', '#c62828'],
        text_auto='.1f'
    )
    fig_sales.update_layout(
        showlegend=False, 
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        yaxis_title="증감률 (%)",
        xaxis_title=""
    )
    st.plotly_chart(fig_sales, use_container_width=True)

with right_chart:
    st.markdown('<h3 class="section-title">👥 구매 고객 인구통계 비중</h3>', unsafe_allow_html=True)
    age_data = pd.DataFrame({
        '연령층': ['2030 사회초년생', '기타 연령층'],
        '비중': [45, 55]
    })
    
    fig_age = px.pie(
        age_data, values='비중', names='연령층',
        hole=0.6,
        color_discrete_sequence=['#fbc02d', '#f1f5f9']
    )
    fig_age.update_layout(
        height=400, 
        margin=dict(t=30, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_age, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<h3 class="section-title">💬 고객 리뷰 분석 (500건 표본)</h3>', unsafe_allow_html=True)

voc_col, info_col = st.columns([2, 1])

with voc_col:
    voc_data = pd.DataFrame({
        '키워드': ['세련된 패키지', '쓴맛 완화', '가격 인상 체감', '박스 개봉 불편'],
        '언급 빈도': [92, 85, 45, 38],
        '유형': ['긍정', '긍정', '리스크', '리스크']
    })
    
    fig_voc = px.bar(
        voc_data, y='키워드', x='언급 빈도', color='유형',
        orientation='h',
        color_discrete_map={'긍정': '#1a237e', '리스크': '#f57c00'}
    )
    fig_voc.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        height=350,
        xaxis_title="언급 빈도 (건)",
        yaxis_title="",
        showlegend=True
    )
    st.plotly_chart(fig_voc, use_container_width=True)

with info_col:
    st.info("""
    **🚀 Rising Trend: #ActiveLife**
    \n'등산', '테니스' 키워드가 전주 대비 **30% 증가**했습니다. 
    마케팅 자원을 **애슬레저 타겟**으로 집중해야 합니다.
    """)
    
    st.warning("""
    **⚠️ Risk Warning: UX Issue**
    \n'박스 개봉 불편' 리뷰가 지속 관측됩니다. 
    이는 **브랜드 신뢰도**와 직결되므로 공정 개선이 시급합니다.
    """)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<h3 class="section-title">🚀 팀장 전략 제언 (Action Items)</h3>', unsafe_allow_html=True)

act1, act2, act3 = st.columns(3)

with act1:
    with st.expander("1. 채널별 차별화 전략", expanded=True):
        st.markdown("""
        - CVS 전용 '아웃도어 에너지 팩' 기획
        - 수도권 성공 사례의 지방 확산 캠페인
        """)

with act2:
    with st.expander("2. 상품 UX 개선 (물리 품질)", expanded=True):
        st.markdown("""
        - 박스 이지-오픈(Easy-Open) 구조 점검
        - 가격 저항 완화용 소포장 SKU 확대
        """)

with act3:
    with st.expander("3. 브랜드 포지셔닝 확장", expanded=True):
        st.markdown("""
        - '오피스 에너지' → '액티브 에너지'
        - 테니스/등산 커뮤니티 협업 강화
        """)

# 푸터
st.markdown("""
    <div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 60px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
        © 2026 KGC Brand Strategy Team. Internal Confidential.
    </div>
    """, unsafe_allow_html=True)
