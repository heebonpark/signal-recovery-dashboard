import json
import os
import hashlib
import secrets
import threading
import time
import streamlit as st

from app.core.data_handler import get_branch_vehicle_map

USERS_FILE_PATH = os.path.expanduser("~/.dataintelligence_pro/users.json")
LOCKOUT_FILE_PATH = os.path.expanduser("~/.dataintelligence_pro/lockouts.json")

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300
DEFAULT_BRANCH_CAR_PASSWORD = "1234"  # 지사/차량 계정 최초 비밀번호. 최초 로그인 후 변경 필요.

_file_lock = threading.Lock()


def _hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return digest, salt


def _verify_password(password, record):
    if "password_hash" in record and "salt" in record:
        digest, _ = _hash_password(password, record["salt"])
        return digest == record["password_hash"]
    # 레거시 평문 비밀번호 (다음 로그인 성공 시 해시로 자동 전환됨)
    return record.get("password") == password


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users():
    return _load_json(USERS_FILE_PATH, {})


def save_users(users):
    with _file_lock:
        _save_json(USERS_FILE_PATH, users)


def ensure_default_accounts():
    """관리자 계정과, 데이터 파일에 존재하는 모든 지사/차량 계정을 자동 생성한다.
    이미 존재하는 계정(관리자가 비밀번호를 바꾼 계정 포함)은 건드리지 않는다."""
    users = load_users()
    changed = False

    if "admin" not in users:
        digest, salt = _hash_password("admin")
        users["admin"] = {"password_hash": digest, "salt": salt, "role": "admin", "branch": "all"}
        changed = True

    branch_map = get_branch_vehicle_map()
    for branch, cars in branch_map.items():
        if branch not in users:
            digest, salt = _hash_password(DEFAULT_BRANCH_CAR_PASSWORD)
            users[branch] = {
                "password_hash": digest,
                "salt": salt,
                "role": "branch",
                "branch": branch,
            }
            changed = True
        for car in cars:
            if car not in users:
                digest, salt = _hash_password(DEFAULT_BRANCH_CAR_PASSWORD)
                users[car] = {
                    "password_hash": digest,
                    "salt": salt,
                    "role": "car",
                    "branch": branch,
                    "car_id": car,
                }
                changed = True

    if changed:
        save_users(users)
    return users


def _load_lockouts():
    return _load_json(LOCKOUT_FILE_PATH, {})


def _save_lockouts(data):
    with _file_lock:
        _save_json(LOCKOUT_FILE_PATH, data)


def is_locked_out(username):
    data = _load_lockouts()
    record = data.get(username)
    if not record:
        return False, 0
    remaining = record.get("locked_until", 0) - time.time()
    if record.get("count", 0) >= MAX_LOGIN_ATTEMPTS and remaining > 0:
        return True, int(remaining)
    return False, 0


def _register_failed_attempt(username):
    data = _load_lockouts()
    record = data.get(username, {"count": 0, "locked_until": 0})
    record["count"] = record.get("count", 0) + 1
    if record["count"] >= MAX_LOGIN_ATTEMPTS:
        record["locked_until"] = time.time() + LOCKOUT_SECONDS
    data[username] = record
    _save_lockouts(data)


def _clear_attempts(username):
    data = _load_lockouts()
    if username in data:
        del data[username]
        _save_lockouts(data)


def authenticate(username, password):
    users = ensure_default_accounts()
    record = users.get(username)
    if not record or not _verify_password(password, record):
        return None

    # 레거시 평문 비밀번호를 해시로 자동 전환
    if "password" in record:
        digest, salt = _hash_password(password)
        migrated = {k: v for k, v in record.items() if k != "password"}
        migrated["password_hash"] = digest
        migrated["salt"] = salt
        users[username] = migrated
        save_users(users)
        record = migrated

    user_info = record.copy()
    user_info["user_id"] = username
    return user_info


def login(username, password):
    """성공 시 (True, None), 실패 시 (False, 사용자에게 보여줄 에러 메시지)를 반환한다."""
    if not username:
        return False, "로그인 정보를 선택해주세요."

    locked, remaining = is_locked_out(username)
    if locked:
        return False, f"로그인 시도 횟수를 초과했습니다. {remaining}초 후 다시 시도해주세요."

    user = authenticate(username, password)
    if user:
        _clear_attempts(username)
        st.session_state["authenticated"] = True
        st.session_state["user_info"] = user
        return True, None

    _register_failed_attempt(username)
    return False, "아이디 또는 비밀번호가 올바르지 않습니다."


def logout():
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = None
