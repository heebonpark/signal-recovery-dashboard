import json
import os
import threading

ACTIONS_FILE_PATH = os.path.expanduser("~/.dataintelligence_pro/actions.json")

ACTION_FIELDS = ["조치일자", "조치자", "조치내용", "조치예정일", "미조치 사유"]

_file_lock = threading.Lock()


def _load_all():
    if not os.path.exists(ACTIONS_FILE_PATH):
        return {}
    try:
        with open(ACTIONS_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_all(data):
    with _file_lock:
        os.makedirs(os.path.dirname(ACTIONS_FILE_PATH), exist_ok=True)
        with open(ACTIONS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def row_key(dataset_type, row_index):
    return f"{dataset_type}_{row_index}"


def get_action(dataset_type, row_index):
    data = _load_all()
    return data.get(row_key(dataset_type, row_index), {})


def save_action(dataset_type, row_index, values, updated_by):
    with _file_lock:
        data = _load_all()
    key = row_key(dataset_type, row_index)
    record = {field: values.get(field, "") for field in ACTION_FIELDS}
    record["_updated_by"] = updated_by
    data[key] = record
    _save_all(data)


def apply_actions(df, dataset_type):
    """저장된 조치 내역을 데이터프레임의 조치 관련 컬럼에 덮어씌운다."""
    if df.empty:
        return df

    available_fields = [f for f in ACTION_FIELDS if f in df.columns]
    if not available_fields:
        return df

    data = _load_all()
    if not data:
        return df

    df = df.copy()
    for idx in df.index:
        record = data.get(row_key(dataset_type, idx))
        if not record:
            continue
        for field in available_fields:
            value = record.get(field, "")
            if value:
                df.at[idx, field] = value
    return df
