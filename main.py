import streamlit as st
from app.ui.styles import apply_custom_css
from app.ui.dashboard import render_dashboard
from app.core.auth import login
from app.core.logger import add_log
from app.core.data_handler import get_branch_vehicle_map

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

def render_login():
    st.markdown("<div class='glass-container' style='max-width: 460px; margin: 80px auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0f172a;'>📡 Data Intel PRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>무신호/미복구 시설현황 대시보드</p>", unsafe_allow_html=True)

    branch_map = get_branch_vehicle_map()

    login_type = st.radio(
        "로그인 유형",
        ["지사", "차량", "관리자"],
        horizontal=True,
        key="login_type",
    )

    username = None

    if login_type == "관리자":
        username = st.text_input("아이디", placeholder="admin", key="login_username")

    elif login_type == "지사":
        if branch_map:
            username = st.selectbox("지사 선택", list(branch_map.keys()), key="login_branch")
        else:
            st.warning("지사 목록을 불러올 수 없습니다. 데이터 파일을 확인해주세요.")

    else:  # 차량
        if branch_map:
            branch = st.selectbox("지사 선택", list(branch_map.keys()), key="login_branch_for_car")
            cars = branch_map.get(branch, [])
            if cars:
                username = st.selectbox("차량 선택", cars, key="login_car")
            else:
                st.warning("선택한 지사에 등록된 차량이 없습니다.")
        else:
            st.warning("차량 목록을 불러올 수 없습니다. 데이터 파일을 확인해주세요.")

    password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="login_password")

    if st.button("로그인", use_container_width=True, key="login_submit"):
        ok, error = login(username, password)
        if ok:
            add_log(username, "LOGIN_SUCCESS")
            st.success("로그인 성공!")
            st.rerun()
        else:
            add_log(username or "(미입력)", "LOGIN_FAILED", error or "")
            st.error(error)

    st.markdown("</div>", unsafe_allow_html=True)

# Main Routing
if st.session_state["authenticated"]:
    render_dashboard()
else:
    render_login()
