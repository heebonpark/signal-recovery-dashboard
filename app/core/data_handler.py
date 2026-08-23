import pandas as pd
import os
import re
import datetime
import unicodedata
import streamlit as st

from app.core.actions import ACTION_FIELDS, apply_actions

DATA_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _find_branch_col(df):
    return next((c for c in df.columns if "지사" in c), None)


def _find_car_col(df):
    return next((c for c in df.columns if "차량" in c), None)


def _find_customer_no_col(df):
    return next((c for c in df.columns if "고객번호" in c), None)


def get_year_bucket_col(df):
    """경과 구간(예: '25년', '24년이전') 컬럼. 파일마다 컬럼명이 다르다."""
    for name in ["최종신호2", "최종"]:
        if name in df.columns:
            return name
    return None


@st.cache_data
def load_data(file_type="무신호"):
    # Determine which file to load
    # macOS(HFS+/APFS)는 한글 파일명을 NFD(자모 분리)로 저장하므로,
    # 소스코드에 NFC로 적힌 문자열과 그대로 비교하면 매칭되지 않는다. 정규화 후 비교.
    # 두 파일명 모두 "무신호"와 "미복구"를 공통으로 포함하므로("무신호 미복구_..._미복구 리스트.xlsx"),
    # 단순 부분일치로는 파일을 구분할 수 없다. "{종류} 리스트.xlsx"로 끝나는지로 정확히 구분한다.
    target = unicodedata.normalize("NFC", file_type)
    suffix = f"{target} 리스트.xlsx"
    filename = ""
    for f in os.listdir(DATA_DIR):
        normalized = unicodedata.normalize("NFC", f)
        if normalized.endswith(suffix):
            filename = f
            break

    if not filename:
        return pd.DataFrame()

    filepath = os.path.join(DATA_DIR, filename)
    try:
        df = pd.read_excel(filepath)
        branch_col = _find_branch_col(df)
        car_col = _find_car_col(df)
        customer_no_col = _find_customer_no_col(df)
        # astype(str)은 NaN을 문자열 "nan"으로 바꿔버리므로, 값이 있는 셀만 정리한다
        strip_if_present = lambda v: str(v).strip() if pd.notna(v) else v
        if branch_col:
            df[branch_col] = df[branch_col].apply(strip_if_present)
        if car_col:
            df[car_col] = df[car_col].apply(strip_if_present)
        if customer_no_col:
            # 엑셀에서 숫자로 읽혀 "17,370.0" 처럼 표시되던 것을 순수 식별자 문자열로 변환
            df[customer_no_col] = df[customer_no_col].apply(
                lambda v: str(int(v)) if pd.notna(v) else ""
            )
        for field in ACTION_FIELDS:
            if field in df.columns:
                df[field] = df[field].apply(lambda v: "" if pd.isna(v) else str(v))
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()


def load_data_with_actions(file_type="무신호"):
    """load_data()는 원본 엑셀 결과를 캐시하므로, 사용자가 등록한 조치 내역은
    캐시와 무관하게 매번 별도로 덮어씌운다."""
    df = load_data(file_type)
    return apply_actions(df, file_type)


@st.cache_data
def get_branch_vehicle_map():
    """데이터 파일 전체를 스캔하여 {지사: [차량, ...]} 형태의 맵을 반환한다.
    로그인 화면의 지사/차량 선택 드롭다운과 계정 자동 생성에 사용된다."""
    mapping = {}
    for file_type in ["무신호", "미복구"]:
        df = load_data(file_type)
        if df.empty:
            continue
        branch_col = _find_branch_col(df)
        car_col = _find_car_col(df)
        if not branch_col or not car_col:
            continue
        for branch, group in df.groupby(branch_col):
            if not branch or branch.lower() == "nan":
                continue
            cars = {c for c in group[car_col].dropna().astype(str) if c and c.lower() != "nan"}
            mapping.setdefault(branch, set()).update(cars)

    return {branch: sorted(cars) for branch, cars in sorted(mapping.items())}


@st.cache_data
def get_data_snapshot_info():
    """랜딩 페이지에 표시할 요약 정보: 데이터 기준일(파일명의 YYMMDD)과 전체 관리 건수."""
    total_rows = 0
    for file_type in ["무신호", "미복구"]:
        total_rows += len(load_data(file_type))

    snapshot_date = None
    for f in os.listdir(DATA_DIR):
        normalized = unicodedata.normalize("NFC", f)
        if not normalized.endswith(".xlsx"):
            continue
        match = re.search(r"(\d{6})", normalized)
        if match:
            try:
                snapshot_date = datetime.datetime.strptime(match.group(1), "%y%m%d").date()
                break
            except ValueError:
                continue

    return {"snapshot_date": snapshot_date, "total_rows": total_rows}


def filter_data_by_role(df, user_info):
    if df.empty:
        return df

    role = user_info.get("role")
    branch = user_info.get("branch")
    car_id = user_info.get("car_id")

    branch_col = _find_branch_col(df)
    car_col = _find_car_col(df)

    if role == "admin" or branch == "all":
        return df

    if role == "car" and car_col:
        # 차량 계정은 본인 차량 데이터만 정확히 일치하는 행만 조회 (부분일치 시 타 차량 데이터 노출 위험)
        return df[df[car_col].astype(str) == str(car_id)]

    if role == "branch" and branch_col:
        return df[df[branch_col] == branch]

    return df
