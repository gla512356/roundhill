import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, time
import pytz
import math

# ---------------------------------------------------------
# [설정] 앱 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="Roundhill WeeklyPay™ - 1월 2주차",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# [핵심] HTML 공백 제거 함수
# ---------------------------------------------------------
def render_html(raw_html):
    cleaned = " ".join([line.strip() for line in raw_html.splitlines() if line.strip()])
    st.markdown(cleaned, unsafe_allow_html=True)

# ---------------------------------------------------------
# [스타일] CSS (Roundhill Theme: Deep Teal & Mint)
# ---------------------------------------------------------
render_html("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 1. 글로벌 스타일 및 다크모드 강제 해제 */
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #f0fdfa !important; /* 아주 연한 민트 배경 */
        color: #191f28 !important;
    }

    /* Streamlit 기본 패딩 조정 */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* 2. 헤더 카드 (Deep Teal Gradient) */
    .header-card {
        background: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
        padding: 32px 24px;
        border-radius: 24px;
        color: white !important;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(15, 118, 110, 0.3);
        position: relative;
        overflow: hidden;
    }
    /* 헤더 텍스트 강제 화이트 */
    .header-card h2, .header-card div:not(.market-badge), .header-card span:not(.market-badge) {
        color: white !important;
    }
    .header-card::before {
        content: ''; position: absolute; top: -60px; right: -60px;
        width: 180px; height: 180px;
        background: rgba(255,255,255,0.1); border-radius: 50%; z-index: 0;
    }
    .header-content { position: relative; z-index: 1; }

    /* 3. 뱃지 스타일 (우선순위 강화) */
    .market-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 12px; border-radius: 20px;
        font-size: 0.8rem; font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }

    .header-card .status-open { background: #00e676 !important; color: #003300 !important; animation: pulse 2s infinite; }
    .header-card .status-pre { background: #ffea00 !important; color: #3e2723 !important; }
    .header-card .status-after { background: #d1c4e9 !important; color: #4527a0 !important; }
    .header-card .status-closed { background: #eceff1 !important; color: #455a64 !important; border: 1px solid #cfd8dc; }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 230, 118, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 230, 118, 0); }
    }

    .fx-badge {
        background: rgba(255,255,255,0.2);
        padding: 6px 12px; border-radius: 12px;
        font-size: 0.8rem; font-weight: 600;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.2);
        color: white !important;
    }

    /* 4. 타임라인 (유리 질감) */
    .timeline-container { display: flex; gap: 8px; margin-top: 24px; }
    .glass-box {
        flex: 1; text-align: center;
        background: rgba(255,255,255,0.1);
        padding: 10px; border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(4px);
    }
    .t-label { font-size: 0.7rem; color: rgba(255,255,255,0.8) !important; margin-bottom: 4px; }
    .t-val { font-size: 0.9rem; font-weight: 700; color: #fff !important; white-space: nowrap; }
    .accent-gold { color: #ffd700 !important; }
    .accent-green { color: #69f0ae !important; }

    /* 5. 메인 정보 카드 */
    .info-card {
        background: white !important; border-radius: 24px; padding: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.03);
        border: 1px solid #ccfbf1; margin-bottom: 20px;
    }
    .metric-grid { display: flex; gap: 8px; margin-top: 20px; }
    .metric-box {
        flex: 1; background: #f0fdfa !important; border-radius: 14px;
        padding: 12px 6px; text-align: center;
        border: 1px solid #99f6e4;
        min-width: 0;
    }
    .m-title { font-size: 0.7rem; color: #0f766e !important; font-weight: 600; margin-bottom: 4px; white-space: nowrap; }
    .m-data { font-size: 0.95rem; font-weight: 800; color: #115e59 !important; }

    /* 6. 계산기 카드 공통 */
    .calc-card-bg { background: white !important; border-radius: 24px; padding: 20px; border: 1px solid #e0e0e0; margin-top: 10px; }
    .calc-row { display: flex; justify-content: space-between; margin-bottom: 10px; align-items: center; }
    .calc-label { font-size: 0.9rem; color: #666 !important; }
    .calc-val { font-weight: 700; color: #333 !important; }
    .calc-divider { border-top: 1px dashed #ddd; margin: 12px 0; }
    .calc-total-label { font-size: 1rem; font-weight: 700; color: #0d9488 !important; }
    .calc-total-val { font-size: 1.4rem; font-weight: 800; color: #0f766e !important; }

    /* 주의사항 박스 */
    .caution-box {
        margin-top: 16px; padding: 14px;
        background: #fafafa !important; border-radius: 12px;
        border: 1px solid #eee;
        font-size: 0.8rem; color: #767676 !important; line-height: 1.5;
    }
    .caution-header { font-weight: 700; color: #555 !important; margin-bottom: 4px; display: block; }

    /* 뱃지류 */
    .badge-roc { background: #fff0f2 !important; color: #f04452 !important; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .badge-safe { background: #e8fdf3 !important; color: #02cba5 !important; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
    .ticker-tag { background: #ccfbf1 !important; color: #0f766e !important; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 0.9rem; }

    /* Streamlit 위젯 커스텀 */
    div.stButton > button {
        width: 100%; border-radius: 12px; font-weight: 700;
        background: #fff !important; 
        border: 1px solid #e5e8eb !important;
        color: #6b7684 !important;
        height: 48px; transition: all 0.2s;
    }
    div.stButton > button:hover { 
        background: #f0fdfa !important; 
        color: #0f766e !important; 
        border-color: #99f6e4 !important; 
    }
    div.stButton > button:active {
        color: #000 !important;
    }

    /* 탭 메뉴 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; overflow-x: auto; white-space: nowrap; 
        padding-bottom: 4px; -webkit-overflow-scrolling: touch;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px; background-color: #fff !important; 
        border-radius: 20px; border: 1px solid #e5e8eb;
        padding: 0 16px; font-size: 0.85rem; font-weight: 600;
        color: #666 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d9488 !important; 
        color: white !important; 
        border-color: #0d9488 !important;
    }

    /* [MOBILE] 모바일 반응형 처리 */
    @media (max-width: 480px) {
        .header-card { padding: 24px 16px; margin-bottom: 16px; }
        .header-card h2 { font-size: 1.3rem !important; }
        .timeline-container { gap: 6px; margin-top: 20px; }
        .t-val { font-size: 0.8rem; }

        .info-card { padding: 20px 16px; }
        .m-data { font-size: 0.85rem !important; }

        .calc-card-bg { padding: 16px; }
        .calc-total-val { font-size: 1.2rem !important; }
    }
    </style>
""")

# ---------------------------------------------------------
# [데이터] Roundhill WeeklyPay (2025-01-05 기준)
# ---------------------------------------------------------
# 배당락: 1/5(월)
# 지급일: 1/6(화)
SCHEDULE_KST = {
    "buy_limit": "1/5(월) 06:00", # 한국시간 기준 월요일 새벽 장마감 전
    "ex_date": "1/5(월)",
    "pay_date": "1/6(화)" 
}

# Roundhill 데이터 매핑 (23개 종목)
DATA_MAP = {
    'MSTW': {'div': 0.1608, 'rate': 85.39, 'sec': -0.51, 'roc': 100.00, 'name': 'MSTR WeeklyPay'},
    'HOOW': {'div': 0.6534, 'rate': 71.39, 'sec': 2.67, 'roc': 100.00, 'name': 'HOOD WeeklyPay'},
    'GDXW': {'div': 0.7216, 'rate': 64.81, 'sec': 1.89, 'roc': 100.00, 'name': 'Gold Miners Weekly'},
    'AMDW': {'div': 0.6279, 'rate': 64.66, 'sec': 1.89, 'roc': 100.00, 'name': 'AMD WeeklyPay'},
    'PLTW': {'div': 0.4573, 'rate': 63.62, 'sec': 2.09, 'roc': 100.00, 'name': 'PLTR WeeklyPay'},
    'COIW': {'div': 0.2399, 'rate': 62.76, 'sec': 3.76, 'roc': 100.00, 'name': 'COIN WeeklyPay'},
    'TSLW': {'div': 0.3940, 'rate': 61.39, 'sec': 1.73, 'roc': 100.00, 'name': 'TSLA WeeklyPay'},
    'NVDW': {'div': 0.4695, 'rate': 58.42, 'sec': 2.11, 'roc': 100.00, 'name': 'NVDA WeeklyPay'},
    'AVGW': {'div': 0.5967, 'rate': 65.09, 'sec': 1.87, 'roc': 100.00, 'name': 'AVGO WeeklyPay'},
    'ARMW': {'div': 0.2809, 'rate': 54.09, 'sec': 2.54, 'roc': 100.00, 'name': 'ARM WeeklyPay'},
    'BABW': {'div': 0.4040, 'rate': 53.84, 'sec': 2.51, 'roc': 100.00, 'name': 'BABA WeeklyPay'},
    'UBEW': {'div': 0.3640, 'rate': 47.79, 'sec': 2.21, 'roc': 100.00, 'name': 'UBER WeeklyPay'},
    'UNHW': {'div': 0.4518, 'rate': 47.06, 'sec': 0.00, 'roc': 100.00, 'name': 'UNH WeeklyPay'},
    'NFLW': {'div': 0.2403, 'rate': 45.56, 'sec': 2.57, 'roc': 100.00, 'name': 'NFLX WeeklyPay'},
    'GOOW': {'div': 0.6166, 'rate': 45.25, 'sec': 1.45, 'roc': 100.00, 'name': 'GOOGL WeeklyPay'},
    'AMZW': {'div': 0.3545, 'rate': 43.47, 'sec': 2.08, 'roc': 100.00, 'name': 'AMZN WeeklyPay'},
    'METW': {'div': 0.2920, 'rate': 42.45, 'sec': 2.84, 'roc': 100.00, 'name': 'META WeeklyPay'},
    'GLDW': {'div': 0.3456, 'rate': 33.81, 'sec': 0.00, 'roc': 100.00, 'name': 'Gold WeeklyPay'},
    'MSFW': {'div': 0.2394, 'rate': 31.62, 'sec': 2.56, 'roc': 100.00, 'name': 'MSFT WeeklyPay'},
    'COSW': {'div': 0.2460, 'rate': 30.08, 'sec': 2.29, 'roc': 100.00, 'name': 'COST WeeklyPay'},
    'AAPW': {'div': 0.2112, 'rate': 27.19, 'sec': 1.81, 'roc': 100.00, 'name': 'AAPL WeeklyPay'},
    'BRKW': {'div': 0.1814, 'rate': 21.11, 'sec': 2.10, 'roc': 100.00, 'name': 'BRKB WeeklyPay'},
    'TSYW': {'div': 0.1227, 'rate': 13.44, 'sec': 0.00, 'roc': 100.00, 'name': 'Treasury Weekly'},
}

# -----------------------------
# [함수] 마켓 상태 체크 (실시간)
# -----------------------------
def get_us_market_status():
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)

    # 1. 주말 체크
    if now_ny.weekday() >= 5: 
        return "⛔ 휴장 (주말)", "status-closed"

    # 2. 공휴일 체크 (2025/2026 주요 휴장일)
    holidays = [
        "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16"
    ]
    if now_ny.strftime("%Y-%m-%d") in holidays:
        return "⛔ 휴장 (공휴일)", "status-closed"

    # 3. 시간대 체크 (분 단위 환산)
    minutes = now_ny.hour * 60 + now_ny.minute

    if 240 <= minutes < 570:   # 04:00 ~ 09:30
        return "🌅 프리마켓", "status-pre"
    elif 570 <= minutes < 960: # 09:30 ~ 16:00
        return "🔥 정규장 오픈", "status-open"
    elif 960 <= minutes < 1200: # 16:00 ~ 20:00
        return "🌙 애프터마켓", "status-after"
    else:
        return "💤 장 마감", "status-closed"

# -----------------------------
# [함수] 데이터 연결 (15초 갱신)
# -----------------------------
@st.cache_data(ttl=15, show_spinner=False)
def get_market_info(ticker_keys):
    try:
        fx = yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1]
    except:
        fx = 1440.0 # Fallback

    prices = {}
    try:
        t_str = " ".join(ticker_keys)
        data = yf.download(t_str, period="1d", progress=False)['Close']
        for t in ticker_keys:
            try:
                # 데이터 형태에 따른 처리
                val = data[t].iloc[-1] if isinstance(data, pd.DataFrame) else data[t]
                prices[t] = float(val)
            except:
                prices[t] = 0.0
    except:
        pass

    now_time = datetime.now(pytz.timezone('Asia/Seoul')).strftime("%H:%M:%S")
    return fx, prices, now_time

# -----------------------------
# [UI] 실행 및 레이아웃
# -----------------------------
if st.button("🔄 실시간 시세 새로고침"):
    st.cache_data.clear()

with st.spinner("미국 현지 데이터 수신 중..."):
    t_list = sorted(list(DATA_MAP.keys()))
    usd_krw, price_map, update_time = get_market_info(t_list)
    market_text, market_class = get_us_market_status()

tax_rate = 0.154

# 1. 헤더 영역 (Roundhill Theme)
render_html(f"""
    <div class="header-card">
        <div class="header-content" style="display:flex; justify-content:space-between; align-items:start;">
            <div>
                <div class="market-badge {market_class}">{market_text}</div>
                <h2 style="margin:0; font-size:1.5rem; font-weight:800; letter-spacing:-0.5px;">
                    Roundhill WeeklyPay™<br>1월 2주차 배당
                </h2>
            </div>
            <div style="text-align:right;">
                <div class="fx-badge">🇺🇸 1$ = {usd_krw:,.0f}원</div>
                <div style="font-size:0.7rem; margin-top:4px; opacity:0.8;">{update_time} 기준</div>
            </div>
        </div>
        <div class="header-content timeline-container">
            <div class="glass-box">
                <div class="t-label">🚨 매수마감</div>
                <div class="t-val accent-gold">{SCHEDULE_KST['buy_limit']}</div>
            </div>
            <div class="glass-box">
                <div class="t-label">📉 배당락일</div>
                <div class="t-val">{SCHEDULE_KST['ex_date']}</div>
            </div>
            <div class="glass-box">
                <div class="t-label">💰 지급일</div>
                <div class="t-val accent-green">{SCHEDULE_KST['pay_date']}</div>
            </div>
        </div>
    </div>
""")

# 2. 종목 선택 및 상세 정보
st.markdown("### 💎 종목별 상세 분석")

col_sel, _ = st.columns([1, 0.01])
with col_sel:
    # 기본값 MSTW (1위 종목)
    def_idx = t_list.index("MSTW") if "MSTW" in t_list else 0
    sel_ticker = st.selectbox("분석할 ETF 선택", t_list, index=def_idx)

# 데이터 계산
d = DATA_MAP[sel_ticker]
curr_p = price_map.get(sel_ticker, 0.0)
div_krw = d['div'] * usd_krw
div_krw_net = div_krw * (1 - tax_rate)

# 성향 뱃지 (ROC 100%이므로 절세/안정형 강조)
risk_badge = "<span class='badge-safe'>🛡️ 절세/원금반환형 (ROC 100%)</span>"

# Rate나 SEC가 0.0인 경우 처리
rate_disp = f"{d['rate']}%" if d['rate'] > 0 else "-"
sec_disp = f"{d['sec']}%" if d['sec'] != 0 else "-"

render_html(f"""
    <div class="info-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span class="ticker-tag">{sel_ticker}</span>
                {risk_badge}
            </div>
            <span style="font-size:0.75rem; color:#888;">{d['name']}</span>
        </div>

        <div style="text-align:center; padding: 10px 0;">
            <div style="font-size:0.85rem; color:#0f766e; margin-bottom:6px;">1주당 확정 배당금</div>
            <div style="font-size:2.4rem; font-weight:900; color:#0d9488; letter-spacing:-1px; line-height:1;">
                ${d['div']:.4f}
            </div>
            <div style="font-size:1.1rem; font-weight:700; margin-top:8px;">
                <span style="color:#adb5bd;">(세전)</span> {div_krw:,.0f}원 
                <span style="margin:0 6px; color:#ddd;">|</span> 
                <span style="color:#0f766e;">{div_krw_net:,.0f}원 <span style="font-size:0.8rem; font-weight:500;">(세후)</span></span>
            </div>
        </div>

        <div class="metric-grid">
            <div class="metric-box">
                <div class="m-title">📊 분배율(Rate)</div>
                <div class="m-data">{rate_disp}</div>
            </div>
            <div class="metric-box">
                <div class="m-title">🏦 실질수익(SEC)</div>
                <div class="m-data">{sec_disp}</div>
            </div>
            <div class="metric-box">
                <div class="m-title">↩️ 원금반환(ROC)</div>
                <div class="m-data" style="color: #ef4444 !important;">{d['roc']}%</div>
            </div>
        </div>

        <div style="text-align:right; font-size:0.75rem; color:#adb5bd; margin-top:16px;">
            현재 주가 ${curr_p:.2f} 기준
        </div>
    </div>
""")

# 3. 통합 계산기 탭
st.write("")
tabs = st.tabs(["🧮 배당금", "💧 물타기", "🧪 스트레스", "📉 원금회수", "🔥 FIRE", "⛄ 스노우볼"])

# [탭1] 배당금 계산기
with tabs[0]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.write("") # Spacer
        shares = st.number_input("보유 수량", min_value=1, value=1000, step=10, key="cal_shares")
    with c2:
        val_pre = shares * div_krw
        val_tax = val_pre * tax_rate
        val_post = val_pre - val_tax
        render_html(f"""
            <div class="calc-card-bg">
                <div class="calc-row">
                    <span class="calc-label">세전 배당금</span>
                    <span class="calc-val">{val_pre:,.0f}원</span>
                </div>
                <div class="calc-row">
                    <span class="calc-label">세금 (15.4%)</span>
                    <span class="calc-val" style="color:#e92c2c;">-{val_tax:,.0f}원</span>
                </div>
                <div class="calc-divider"></div>
                <div class="calc-row">
                    <span class="calc-total-label">실제 입금액</span>
                    <span class="calc-total-val">{val_post:,.0f}원</span>
                </div>
            </div>
            <div class="caution-box">
                <span class="caution-header">📌 계산 기준</span>
                • 환율: <b>{usd_krw:,.2f}원</b> (실시간) / 세율: 15.4%<br>
                • 이번 주 배당금 <b>${d['div']:.4f}</b>가 기준입니다.
            </div>
        """)

# [탭2] 물타기 계산기
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        my_avg = st.number_input("내 평단가($)", min_value=0.1, value=curr_p*1.1, step=0.1, format="%.2f")
    with c2:
        my_qty = st.number_input("보유 수량", min_value=1, value=100, step=10, key="mul_qty")
    add_qty = st.number_input("추가 매수(주)", min_value=1, value=50, step=10)

    # 계산
    old_total = my_avg * my_qty
    new_total = old_total + (curr_p * add_qty)
    new_avg = new_total / (my_qty + add_qty)

    # 탈출 기간 단축
    m_div = d['div']
    if m_div > 0:
        old_w = my_avg / m_div
        new_w = new_avg / m_div
        saved = old_w - new_w
    else:
        old_w, new_w, saved = 0, 0, 0

    render_html(f"""
        <div class="calc-card-bg">
            <div style="font-size:0.9rem; color:#666; margin-bottom:8px;">평단가 변화</div>
            <div style="font-size:1.3rem; font-weight:700; display:flex; align-items:center; gap:8px;">
                ${my_avg:.2f} <span style="color:#ccc;">➔</span> <span style="color:#0f766e;">${new_avg:.2f}</span>
            </div>
            <div style="background:#f0fdfa; border-radius:12px; padding:12px; margin-top:16px;">
                <div style="font-size:0.85rem; color:#0f766e; font-weight:600;">🚀 탈출 기간 단축</div>
                <div style="font-size:1rem; font-weight:700; color:#0f766e; margin-top:4px;">
                    {old_w:.1f}주 ➔ {new_w:.1f}주 <span style="color:#00c853;">(-{saved:.1f}주 단축)</span>
                </div>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 추가 매수는 현재가 <b>${curr_p:.2f}</b> 체결 가정<br>
            • 배당금 <b>${m_div:.4f}</b> 유지 시 단순 시뮬레이션입니다.
        </div>
    """)

# [탭3] 스트레스 테스트
with tabs[2]:
    s_qty = st.number_input("보유 수량", min_value=100, value=1000, step=100, key="str_qty")
    base_pay = s_qty * div_krw_net

    render_html(f"""
        <div class="calc-card-bg">
            <div class="calc-row" style="background:#f0fdfa; padding:8px; border-radius:8px;">
                <span class="calc-label">⚡ 현재 유지</span>
                <span class="calc-val" style="color:#0f766e;">{base_pay:,.0f}원</span>
            </div>
            <div class="calc-row">
                <span class="calc-label">📉 -10% 삭감</span>
                <span class="calc-val">{base_pay*0.9:,.0f}원</span>
            </div>
            <div class="calc-row">
                <span class="calc-label">📉 -30% 삭감</span>
                <span class="calc-val">{base_pay*0.7:,.0f}원</span>
            </div>
            <div class="calc-row">
                <span class="calc-label" style="color:#e92c2c;">📉 -50% 삭감</span>
                <span class="calc-val" style="color:#e92c2c;">{base_pay*0.5:,.0f}원</span>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • <b>세후(15.4% 공제)</b> 금액 기준입니다.<br>
            • 배당 삭감 시나리오를 미리 확인하여 리스크를 관리하세요.
        </div>
    """)

# [탭4] 원금회수 (BEP)
with tabs[3]:
    bep_price = st.number_input("내 평단가($)", min_value=0.1, value=curr_p, step=0.1, format="%.2f", key="bep_p")
    if d['div'] > 0:
        w_need = bep_price / d['div']
        m_need = w_need / 4.3
    else:
        w_need, m_need = 0, 0

    render_html(f"""
        <div class="calc-card-bg" style="text-align:center;">
            <div style="font-size:0.9rem; color:#666; margin-bottom:8px;">원금 회수(Free Ride)까지</div>
            <div style="font-size:2rem; font-weight:900; color:#e92c2c; letter-spacing:-1px;">
                {w_need:.1f}주 <span style="font-size:1rem; color:#999; font-weight:500;">(약 {m_need:.1f}개월)</span>
            </div>
            <div style="margin-top:12px; font-size:0.85rem; color:#d32f2f; background:#fff0f2; padding:8px; border-radius:8px;">
                💡 <b>{w_need:.0f}번</b>만 배당 받으면 본전입니다!
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 현재 배당금 <b>${d['div']:.4f}</b>가 앞으로도 동일하게 지급된다는 가정입니다.<br>
            • 실제 회수 기간은 배당금 변동에 따라 달라질 수 있습니다.
        </div>
    """)

# [탭5] FIRE (주간 목표)
with tabs[4]:
    target = st.number_input("목표 '주간' 배당금 (만원)", min_value=10, value=50, step=10)
    if div_krw_net > 0:
        req_shares = math.ceil((target*10000) / div_krw_net)
        req_money = req_shares * curr_p * usd_krw
    else:
        req_shares, req_money = 0, 0

    render_html(f"""
        <div class="calc-card-bg">
            <div style="text-align:center; margin-bottom:16px;">
                <div style="font-size:0.9rem; color:#666;">매주 <b style="color:#0f766e;">{target}만원</b> 받으려면?</div>
            </div>
            <div style="display:flex; justify-content:space-around; align-items:center;">
                <div style="text-align:center;">
                    <div style="font-size:0.8rem; color:#888;">필요 주식</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#333;">{req_shares:,}주</div>
                </div>
                <div style="width:1px; height:30px; background:#eee;"></div>
                <div style="text-align:center;">
                    <div style="font-size:0.8rem; color:#888;">예상 투자금</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#0f766e;">{req_money/10000:,.0f}만원</div>
                </div>
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 환율 {usd_krw:,.0f}원 / 현재가 ${curr_p:.2f} 기준<br>
            • 세후 배당금을 기준으로 역산한 결과입니다.
        </div>
    """)

# [탭6] 스노우볼
with tabs[5]:
    snow_shares = st.number_input("현재 보유 수량", min_value=1, value=1000, step=10, key="snow_s")

    # 1. 이번주 받을 돈 (세후)
    this_pay = snow_shares * div_krw_net
    # 2. 재투자 가능 수량
    re_price = curr_p * usd_krw
    if re_price > 0:
        add_cnt = math.floor(this_pay / re_price)
        rem_cash = this_pay - (add_cnt * re_price)
        next_inc = add_cnt * div_krw_net
    else:
        add_cnt, rem_cash, next_inc = 0, 0, 0

    render_html(f"""
        <div class="calc-card-bg" style="background:linear-gradient(135deg, #f0fdfa 0%, #fff 100%);">
            <div style="text-align:center; margin-bottom:10px;">
                <span style="font-size:0.9rem; color:#555;">이번 배당금으로</span><br>
                <span style="font-size:1.5rem; font-weight:900; color:#0f766e;">+{add_cnt}주</span>
                <span style="font-size:1rem; font-weight:700;"> 추가 매수!</span>
            </div>
            <div style="background:white; border-radius:12px; padding:12px; text-align:center; border:1px solid #ccfbf1;">
                <div style="font-size:0.8rem; color:#888;">다음 주 늘어나는 배당금</div>
                <div style="font-size:1.1rem; font-weight:800; color:#0f766e;">+{next_inc:,.0f}원 🆙</div>
            </div>
            <div style="text-align:center; font-size:0.75rem; color:#999; margin-top:8px;">
                (남는 돈 {rem_cash:,.0f}원은 간식비 ☕)
            </div>
        </div>
        <div class="caution-box">
            <span class="caution-header">📌 계산 기준</span>
            • 재투자 단가: <b>${curr_p:.2f}</b> (현재가)<br>
            • 배당금이 유지된다고 가정했을 때의 복리 효과입니다.
        </div>
    """)

# 4. 용어 설명
st.write("")
with st.expander("🎓 주린이 용어 가이드"):
    render_html("""
    <div style="padding:10px; font-size:0.85rem; line-height:1.6; color:#555;">
        <p><b>1️⃣ Distribution Rate (분배율)</b><br>
        이번 배당금을 1년 내내 똑같이 준다고 가정했을 때의 연 수익률입니다.</p>
        <p><b>2️⃣ 30-Day SEC Yield</b><br>
        최근 30일간 펀드가 실제로 벌어들인 이자 수익(펀더멘털)입니다.</p>
        <p><b>3️⃣ ROC (Return of Capital)</b><br>
        <span style="color:#e92c2c;">⚠️ 중요!</span> 펀드가 번 돈이 아니라, <b>투자 원금을 깎아서</b> 배당으로 준 비율입니다.
        이번 Roundhill 배당은 <b>전액 ROC(100%)</b>로, 당장 세금은 없지만 평단가가 낮아집니다.</p>
    </div>
    """)
