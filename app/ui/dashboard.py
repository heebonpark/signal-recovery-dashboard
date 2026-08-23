import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from app.core.data_handler import load_data_with_actions, filter_data_by_role, get_year_bucket_col
from app.core.logger import get_logs, add_log
from app.core.auth import logout
from app.core.actions import ACTION_FIELDS, save_action

ROLE_LABELS = {"admin": "관리자", "branch": "지사", "car": "차량"}
REASON_PRESETS = ["고객 부재", "폐업/이전", "고객 거부", "부품 대기", "일정 조율 중", "직접 입력"]


def _to_excel_bytes(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="data")
    return buffer.getvalue()


def _find_col(df, keyword):
    return next((c for c in df.columns if keyword in c), None)


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


@st.dialog("상세 정보 · 조치 등록", width="large")
def show_row_dialog(row, row_index, dataset_choice, user_info):
    detail_cols = [c for c in row.index if c not in ACTION_FIELDS]

    st.markdown(f"**{row.get('고객명', '-')}**" + (f" · {row.get('상호')}" if row.get("상호") else ""))
    with st.expander("전체 상세 정보", expanded=True):
        grid = st.columns(2)
        for i, col_name in enumerate(detail_cols):
            value = row[col_name]
            display = "-" if (pd.isna(value) or str(value).strip() == "") else value
            with grid[i % 2]:
                st.markdown(
                    f"<div style='margin-bottom:10px;'>"
                    f"<span style='color:#64748b;font-size:0.78rem;'>{col_name}</span><br>"
                    f"<span style='font-weight:600;color:#0f172a;'>{display}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.subheader("✅ 조치 등록")

    c1, c2 = st.columns(2)
    with c1:
        action_date = st.date_input(
            "조치일자", value=_parse_date(row.get("조치일자")), key="dlg_action_date"
        )
        actor = st.text_input(
            "조치자", value=row.get("조치자") or user_info.get("user_id", ""), key="dlg_actor"
        )
    with c2:
        due_date = st.date_input(
            "조치예정일", value=_parse_date(row.get("조치예정일")), key="dlg_due_date"
        )
        current_reason = row.get("미조치 사유") or ""
        default_idx = REASON_PRESETS.index(current_reason) if current_reason in REASON_PRESETS else len(REASON_PRESETS) - 1
        reason_choice = st.selectbox("미조치 사유", REASON_PRESETS, index=default_idx, key="dlg_reason_choice")

    content = st.text_area("조치내용", value=row.get("조치내용") or "", key="dlg_content")

    if reason_choice == "직접 입력":
        reason_text = st.text_input(
            "사유 직접 입력",
            value=current_reason if current_reason not in REASON_PRESETS else "",
            key="dlg_reason_free",
        )
    else:
        reason_text = reason_choice

    save_col, close_col = st.columns(2)
    with save_col:
        if st.button("💾 저장", use_container_width=True, type="primary"):
            save_action(
                dataset_choice,
                row_index,
                {
                    "조치일자": action_date.isoformat() if action_date else "",
                    "조치자": actor,
                    "조치내용": content,
                    "조치예정일": due_date.isoformat() if due_date else "",
                    "미조치 사유": reason_text,
                },
                updated_by=user_info.get("user_id", ""),
            )
            add_log(user_info.get("user_id", ""), "SAVE_ACTION", f"{dataset_choice} row {row_index}")
            st.success("저장되었습니다.")
            st.rerun()
    with close_col:
        if st.button("닫기", use_container_width=True):
            st.rerun()


def render_dashboard():
    user_info = st.session_state.get("user_info", {})
    role = user_info.get("role", "unknown")
    user_id = user_info.get("user_id", "unknown")
    branch = user_info.get("branch", "unknown")
    role_label = ROLE_LABELS.get(role, role)

    header_col1, header_col2 = st.columns([8, 2])
    with header_col1:
        branch_suffix = f" · {branch} 소속" if branch not in ("unknown", "all", user_id) else ""
        st.markdown(
            f"""
            <h2 style='margin-bottom:0;'>📡 Data Intel PRO</h2>
            <p style='color:#64748b; margin-top:4px;'>
                <span class='badge'>{role_label}</span>{user_id}{branch_suffix}
            </p>
            """,
            unsafe_allow_html=True,
        )
    with header_col2:
        if st.button("로그아웃", use_container_width=True):
            add_log(user_id, "LOGOUT")
            logout()
            st.rerun()

    st.markdown("<div class='glass-container'>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(
        ["데이터 조회", "시각화 분석", "관리자 모니터링" if role == "admin" else "내 정보"]
    )

    dataset_choice = "무신호"

    with tab1:
        st.subheader("무신호 및 미복구 시설현황")
        dataset_choice = st.radio("데이터셋 선택", ["무신호", "미복구"], horizontal=True, key="dataset_choice")

        df = load_data_with_actions(dataset_choice)

        if df.empty:
            st.warning("데이터 파일을 찾을 수 없거나 데이터가 비어있습니다.")
        else:
            filtered_df = filter_data_by_role(df, user_info)
            year_col = get_year_bucket_col(filtered_df)

            filter_col1, filter_col2 = st.columns([3, 2])
            with filter_col1:
                search_term = st.text_input("🔍 검색 (고객명 / 차량 / 주소 / 상호)", key="search_term")
            with filter_col2:
                if year_col:
                    # 일부 셀에 손상된 값(엑셀 오류 코드 등)이 섞여 있을 수 있어 문자열만 사용
                    year_options = sorted(v for v in filtered_df[year_col].dropna().unique().tolist() if isinstance(v, str))
                else:
                    year_options = []
                selected_years = st.multiselect("경과 구간", year_options, key="year_filter") if year_options else []

            view_df = filtered_df
            if search_term:
                search_cols = [c for c in ["고객명", "차량", "주소", "상호"] if c in view_df.columns]
                if search_cols:
                    mask = pd.Series(False, index=view_df.index)
                    for c in search_cols:
                        mask |= view_df[c].astype(str).str.contains(search_term, case=False, na=False)
                    view_df = view_df[mask]
            if year_col and selected_years:
                view_df = view_df[view_df[year_col].isin(selected_years)]

            branch_col = _find_col(view_df, "지사")
            car_col = _find_col(view_df, "차량")
            long_term_count = int((view_df[year_col] == "24년이전").sum()) if year_col else None

            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f"<div class='metric-card'><h4>총 건수</h4><h2>{len(view_df):,}</h2></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='metric-card'><h4>지사 수</h4><h2>{view_df[branch_col].nunique() if branch_col else '-'}</h2></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='metric-card'><h4>차량 수</h4><h2>{view_df[car_col].nunique() if car_col else '-'}</h2></div>", unsafe_allow_html=True)
            m4.markdown(
                f"<div class='metric-card' style='border-left-color:#dc2626;'><h4>장기 미복구(24년 이전)</h4><h2>{long_term_count if long_term_count is not None else '-'}</h2></div>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("💡 행을 클릭하면 상세 정보를 보고 조치 내역(조치일자·조치자·조치내용·조치예정일·미조치 사유)을 등록할 수 있습니다.")
            event = st.dataframe(
                view_df,
                use_container_width=True,
                height=500,
                on_select="rerun",
                selection_mode="single-row",
                key=f"data_table_{dataset_choice}",
            )

            st.download_button(
                "⬇️ 엑셀 다운로드",
                data=_to_excel_bytes(view_df),
                file_name=f"{dataset_choice}_{user_id}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            selected_rows = event.selection.rows if event and event.selection else []
            if selected_rows:
                position = selected_rows[0]
                selected_row = view_df.iloc[position]
                original_index = view_df.index[position]
                show_row_dialog(selected_row, original_index, dataset_choice, user_info)

            # 위젯 조작(검색/필터)마다 재실행되어도, 실제로 조회 결과가 바뀐 경우에만 로그를 남긴다
            log_key = f"{dataset_choice}:{len(view_df)}:{search_term}:{selected_years}"
            if st.session_state.get("_last_view_log") != log_key:
                add_log(user_id, "VIEW_DATA", f"Viewed {dataset_choice} data. Rows: {len(view_df)}")
                st.session_state["_last_view_log"] = log_key

    with tab2:
        st.subheader("시각화 분석")
        df = load_data_with_actions(dataset_choice)
        if df.empty:
            st.info("표시할 데이터가 없습니다.")
        else:
            filtered_df = filter_data_by_role(df, user_info)
            branch_col = _find_col(filtered_df, "지사")
            car_col = _find_col(filtered_df, "차량")
            year_col = get_year_bucket_col(filtered_df)

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                if branch_col and filtered_df[branch_col].nunique() > 1:
                    counts = filtered_df[branch_col].value_counts().reset_index()
                    counts.columns = ["지사", "건수"]
                    fig = px.bar(counts, x="지사", y="건수", title="지사별 현황", color="건수", color_continuous_scale="Blues")
                    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("지사별 비교는 여러 지사를 조회할 수 있는 계정(관리자)에서만 표시됩니다.")
            with chart_col2:
                if year_col:
                    valid_years = filtered_df[year_col][filtered_df[year_col].apply(lambda v: isinstance(v, str))]
                    counts = valid_years.value_counts().reset_index()
                    counts.columns = ["경과 구간", "건수"]
                    fig = px.pie(counts, names="경과 구간", values="건수", title="경과 구간별 분포", hole=0.45)
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("경과 구간 정보가 없습니다.")

            action_cols_present = [c for c in ACTION_FIELDS if c in filtered_df.columns]
            if action_cols_present:
                st.markdown("---")
                st.subheader("📝 조치 등록 현황")

                registered_mask = filtered_df[action_cols_present].apply(
                    lambda r: any(str(v).strip() for v in r), axis=1
                )
                registered_count = int(registered_mask.sum())
                total_count = len(filtered_df)
                rate = (registered_count / total_count * 100) if total_count else 0

                rm1, rm2, rm3 = st.columns(3)
                rm1.markdown(f"<div class='metric-card'><h4>총 등록 건수</h4><h2>{registered_count:,}</h2></div>", unsafe_allow_html=True)
                rm2.markdown(f"<div class='metric-card'><h4>미등록 건수</h4><h2>{total_count - registered_count:,}</h2></div>", unsafe_allow_html=True)
                rm3.markdown(f"<div class='metric-card'><h4>등록률</h4><h2>{rate:.1f}%</h2></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                reg_col1, reg_col2 = st.columns(2)
                with reg_col1:
                    if branch_col and filtered_df[branch_col].nunique() > 1:
                        branch_reg = (
                            filtered_df.assign(_등록=registered_mask)
                            .groupby(branch_col)["_등록"].sum()
                            .reset_index()
                            .sort_values("_등록", ascending=False)
                        )
                        branch_reg.columns = ["지사", "등록 건수"]
                        fig = px.bar(branch_reg, x="지사", y="등록 건수", title="지사별 등록 건수", color="등록 건수", color_continuous_scale="Greens")
                        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("지사별 등록 현황은 여러 지사를 조회할 수 있는 계정(관리자)에서만 표시됩니다.")
                with reg_col2:
                    if car_col and filtered_df[car_col].nunique() > 1:
                        car_reg = (
                            filtered_df.assign(_등록=registered_mask)
                            .groupby(car_col)["_등록"].sum()
                            .reset_index()
                            .sort_values("_등록", ascending=False)
                        )
                        car_reg.columns = ["차량", "등록 건수"]
                        fig = px.bar(car_reg, x="차량", y="등록 건수", title="차량별 등록 건수", color="등록 건수", color_continuous_scale="Greens")
                        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("차량별 등록 현황은 차량이 2대 이상 조회 가능한 계정에서 표시됩니다.")

    with tab3:
        if role == "admin":
            st.subheader("시스템 활동 모니터링")
            logs = get_logs()
            if logs:
                logs_df = pd.DataFrame(logs).sort_values(by="timestamp", ascending=False).reset_index(drop=True)

                log_filter_col1, log_filter_col2 = st.columns([3, 2])
                with log_filter_col1:
                    log_search = st.text_input("🔍 로그 검색 (아이디 / 액션)", key="log_search")
                with log_filter_col2:
                    action_filter = st.multiselect("액션 필터", sorted(logs_df["action"].unique().tolist()), key="log_action_filter")

                view_logs = logs_df
                if log_search:
                    mask = (
                        view_logs["user_id"].astype(str).str.contains(log_search, case=False, na=False)
                        | view_logs["action"].astype(str).str.contains(log_search, case=False, na=False)
                    )
                    view_logs = view_logs[mask]
                if action_filter:
                    view_logs = view_logs[view_logs["action"].isin(action_filter)]

                lm1, lm2, lm3 = st.columns(3)
                lm1.markdown(f"<div class='metric-card'><h4>전체 로그</h4><h2>{len(logs_df):,}</h2></div>", unsafe_allow_html=True)
                lm2.markdown(f"<div class='metric-card'><h4>로그인 실패</h4><h2>{int((logs_df['action']=='LOGIN_FAILED').sum()):,}</h2></div>", unsafe_allow_html=True)
                lm3.markdown(f"<div class='metric-card'><h4>활동 사용자 수</h4><h2>{logs_df['user_id'].nunique():,}</h2></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(view_logs, use_container_width=True, height=450)
            else:
                st.info("기록된 활동 로그가 없습니다.")
        else:
            st.subheader("내 계정 정보")
            st.write(f"**아이디:** {user_id}")
            st.write(f"**역할:** {role_label}")
            st.write(f"**소속 지사:** {branch}")
            if role == "car":
                st.write(f"**차량 번호:** {user_info.get('car_id')}")

    st.markdown("</div>", unsafe_allow_html=True)
