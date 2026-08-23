import streamlit as st
from app.ui.styles import apply_custom_css
from app.ui.dashboard import render_dashboard
from app.core.auth import login, is_locked_out, MAX_LOGIN_ATTEMPTS, LOCKOUT_SECONDS
from app.core.logger import add_log
from app.core.data_handler import get_branch_vehicle_map, get_data_snapshot_info

# Page Config
st.set_page_config(
    page_title="Data Intel PRO - 무신호/미복구 시설현황",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply CSS
apply_custom_css()

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

LOGIN_TYPE_META = {
    "지사": {"icon": "🏢", "desc": "소속 지사의 시설 현황을 조회하고 조치를 등록합니다."},
    "차량": {"icon": "🚚", "desc": "담당 차량의 시설만 조회하고 조치를 등록합니다."},
    "관리자": {"icon": "🛡️", "desc": "전체 지사·차량 데이터와 활동 로그를 관리합니다."},
}


def render_login():
    branch_map = get_branch_vehicle_map()
    snapshot = get_data_snapshot_info()
    branch_count = len(branch_map)
    car_count = sum(len(v) for v in branch_map.values())
    total_rows = snapshot["total_rows"]
    snapshot_date = snapshot["snapshot_date"].strftime("%Y.%m.%d") if snapshot["snapshot_date"] else "-"

    st.markdown("<div class='login-shell'>", unsafe_allow_html=True)
    hero_col, form_col = st.columns([1.15, 1], gap="large")

    with hero_col:
        st.markdown(
            f"""
            <div class='hero-panel'>
                <div class='hero-blob hero-blob-1'></div>
                <div class='hero-blob hero-blob-2'></div>
                <div class='hero-content'>
                    <span class='hero-badge'>📡 SIGNAL RECOVERY PLATFORM</span>
                    <h1>Data Intel PRO</h1>
                    <p class='hero-sub'>무신호 · 미복구 시설현황을 한눈에 파악하고<br>지사·차량 단위로 신속하게 조치를 등록하세요.</p>
                    <div class='hero-stats'>
                        <div class='hero-stat'><strong>{branch_count}</strong><span>관리 지사</span></div>
                        <div class='hero-stat'><strong>{car_count}</strong><span>운영 차량</span></div>
                        <div class='hero-stat'><strong>{total_rows:,}</strong><span>관리 대상 건수</span></div>
                    </div>
                    <ul class='hero-features'>
                        <li>지사 · 차량 단위 권한별 데이터 필터링</li>
                        <li>행 클릭 한 번으로 상세정보 · 조치 등록</li>
                        <li>실시간 시각화 및 등록 현황 분석</li>
                    </ul>
                    <p class='hero-footnote'>데이터 기준일 {snapshot_date}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form_col:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h3 class='login-title'>로그인</h3>", unsafe_allow_html=True)
        st.markdown("<p class='login-caption'>계정 유형을 선택하고 정보를 입력하세요.</p>", unsafe_allow_html=True)

        login_type = st.radio(
            "로그인 유형", list(LOGIN_TYPE_META.keys()), horizontal=True,
            key="login_type", label_visibility="collapsed",
        )
        meta = LOGIN_TYPE_META[login_type]
        st.markdown(
            f"<div class='login-type-hint'>{meta['icon']}&nbsp; {meta['desc']}</div>",
            unsafe_allow_html=True,
        )

        # 지사/차량 선택은 즉시 반영되어야 하는 계단식(cascading) 드롭다운이라 폼 밖에 둔다
        username = None
        if login_type == "지사":
            if branch_map:
                username = st.selectbox("지사 선택", list(branch_map.keys()), key="login_branch")
            else:
                st.warning("지사 목록을 불러올 수 없습니다. 데이터 파일을 확인해주세요.")
        elif login_type == "차량":
            if branch_map:
                branch = st.selectbox("지사 선택", list(branch_map.keys()), key="login_branch_for_car")
                cars = branch_map.get(branch, [])
                if cars:
                    username = st.selectbox("차량 선택", cars, key="login_car")
                else:
                    st.warning("선택한 지사에 등록된 차량이 없습니다.")
            else:
                st.warning("차량 목록을 불러올 수 없습니다. 데이터 파일을 확인해주세요.")

        if login_type != "관리자" and username:
            locked, remaining = is_locked_out(username)
            if locked:
                st.markdown(
                    f"<div class='lockout-banner'>🔒 이 계정은 로그인 시도 초과로 잠겨 있습니다. "
                    f"<strong>{remaining}초</strong> 후 다시 시도해주세요.</div>",
                    unsafe_allow_html=True,
                )

        with st.form("login_form", clear_on_submit=False):
            if login_type == "관리자":
                username = st.text_input("아이디", placeholder="admin")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            submitted = st.form_submit_button("로그인 →", use_container_width=True)

        if submitted:
            ok, error = login(username, password)
            if ok:
                add_log(username, "LOGIN_SUCCESS")
                st.rerun()
            else:
                add_log(username or "(미입력)", "LOGIN_FAILED", error or "")
                st.markdown(f"<div class='login-error'>⚠️ {error}</div>", unsafe_allow_html=True)

        st.markdown(
            f"<p class='security-footnote'>🔐 비밀번호는 암호화되어 저장되며, "
            f"{MAX_LOGIN_ATTEMPTS}회 연속 실패 시 {LOCKOUT_SECONDS // 60}분간 계정이 잠깁니다.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# Main Routing
if st.session_state["authenticated"]:
    render_dashboard()
else:
    render_login()
