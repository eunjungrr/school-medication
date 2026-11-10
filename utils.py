"""
유틸리티 함수 모듈
날짜 처리, 재고 상태 판정, 엑셀 내보내기 등
"""

import io
import re
from datetime import date, datetime, timedelta
from typing import Optional

import pandas as pd

# ─── 분류 목록 ──────────────────────────────────────────────────────
CATEGORIES = [
    "해열·진통·소염제",
    "소화기계용약",
    "호흡기계용약",
    "연고·소독·패치류",
    "안이비인후과용",
    "알레르기·항히스타민제",
    "응급·구급약품",
    "기타",
]

# ─── 재고 상태 정의 ──────────────────────────────────────────────────
STATUS_EXPIRED = "즉시 폐기"          # 유통기한 경과
STATUS_EXPIRING = "교체 준비"         # 90일 이내 만료
STATUS_LOW = "재고 부족"              # 현재 재고 < 권장 재고
STATUS_OK = "정상"                    # 정상 보관

STATUS_EMOJI = {
    STATUS_EXPIRED:  "🔴",
    STATUS_EXPIRING: "🟡",
    STATUS_LOW:      "🚨",
    STATUS_OK:       "✅",
}

STATUS_COLOR = {
    STATUS_EXPIRED:  "#FF4B4B",
    STATUS_EXPIRING: "#FFA500",
    STATUS_LOW:      "#FF6B6B",
    STATUS_OK:       "#21BA45",
}

STATUS_BG = {
    STATUS_EXPIRED:  "#FFF0F0",
    STATUS_EXPIRING: "#FFFBF0",
    STATUS_LOW:      "#FFF3F0",
    STATUS_OK:       "#F0FFF4",
}


# ═══════════════════════════════════════════════════════════════════
#  날짜 처리 유틸리티
# ═══════════════════════════════════════════════════════════════════

def parse_expiry_date(raw: str) -> Optional[date]:
    """
    다양한 형식의 유통기한 문자열을 date 객체로 변환합니다.
    지원 형식: YYYY-MM-DD, YYYY/MM/DD, YYYYMMDD, YYYY-MM, YYYY/MM, YYYYMM
    """
    if not raw or str(raw).strip() in ("", "nan", "NaT", "None"):
        return None
    raw = str(raw).strip()

    # 형식 패턴 목록
    patterns = [
        (r"^(\d{4})-(\d{2})-(\d{2})$", "%Y-%m-%d"),
        (r"^(\d{4})/(\d{2})/(\d{2})$", "%Y/%m/%d"),
        (r"^(\d{4})(\d{2})(\d{2})$", "%Y%m%d"),
        (r"^(\d{4})-(\d{2})$", "%Y-%m"),
        (r"^(\d{4})/(\d{2})$", "%Y/%m"),
        (r"^(\d{6})$", "%Y%m"),
    ]

    for pattern, fmt in patterns:
        if re.match(pattern, raw):
            try:
                dt = datetime.strptime(raw, fmt)
                # 월까지만 입력된 경우 해당 월의 말일로 처리
                if fmt in ("%Y-%m", "%Y/%m", "%Y%m"):
                    import calendar
                    last_day = calendar.monthrange(dt.year, dt.month)[1]
                    return date(dt.year, dt.month, last_day)
                return dt.date()
            except ValueError:
                continue
    return None


def format_expiry_display(raw: str) -> str:
    """유통기한을 표시용 문자열로 변환합니다."""
    d = parse_expiry_date(raw)
    if d is None:
        return raw or "미입력"
    return d.strftime("%Y년 %m월 %d일")


def days_until_expiry(expiry_raw: str) -> Optional[int]:
    """오늘부터 유통기한까지의 남은 일수를 계산합니다. (음수면 경과)"""
    d = parse_expiry_date(expiry_raw)
    if d is None:
        return None
    return (d - date.today()).days


# ═══════════════════════════════════════════════════════════════════
#  재고 상태 판정
# ═══════════════════════════════════════════════════════════════════

def get_medicine_status(medicine: dict) -> str:
    """
    의약품 하나의 상태를 판정합니다.
    우선순위: 즉시폐기 > 교체준비 > 재고부족 > 정상
    """
    remaining_days = days_until_expiry(medicine.get("expiry_date", ""))

    # 유통기한이 입력된 경우만 만료 체크
    if remaining_days is not None:
        if remaining_days < 0:
            return STATUS_EXPIRED
        if remaining_days <= 90:
            return STATUS_EXPIRING

    # 재고 부족 체크
    recommended = medicine.get("recommended_stock", 0) or 0
    current = medicine.get("current_stock", 0) or 0
    if recommended > 0 and current < recommended:
        return STATUS_LOW

    return STATUS_OK


def get_dashboard_counts(medicines: list[dict]) -> dict:
    """대시보드용 상태별 의약품 개수를 집계합니다."""
    counts = {
        STATUS_EXPIRED: 0,
        STATUS_EXPIRING: 0,
        STATUS_LOW: 0,
        STATUS_OK: 0,
    }
    for med in medicines:
        status = get_medicine_status(med)
        counts[status] += 1
    return counts


def filter_by_status(medicines: list[dict], status: str) -> list[dict]:
    """특정 상태의 의약품만 필터링합니다."""
    return [m for m in medicines if get_medicine_status(m) == status]


# ═══════════════════════════════════════════════════════════════════
#  엑셀/CSV 내보내기 & 양식 생성
# ═══════════════════════════════════════════════════════════════════

EXPORT_COLUMNS = {
    "id": "번호",
    "category": "분류",
    "name": "품명",
    "spec": "규격/단위",
    "current_stock": "현재 재고",
    "recommended_stock": "권장 재고",
    "expiry_date": "유효기한",
    "location": "보관 위치",
    "memo": "관리 TIP/메모",
}


def medicines_to_dataframe(medicines: list[dict]) -> pd.DataFrame:
    """의약품 목록을 pandas DataFrame으로 변환합니다."""
    if not medicines:
        return pd.DataFrame(columns=list(EXPORT_COLUMNS.values()))

    today = date.today()
    rows = []
    for m in medicines:
        status = get_medicine_status(m)
        days = days_until_expiry(m.get("expiry_date", ""))
        rows.append({
            "번호": m["id"],
            "분류": m.get("category", ""),
            "품명": m.get("name", ""),
            "규격/단위": m.get("spec", ""),
            "현재 재고": m.get("current_stock", 0),
            "권장 재고": m.get("recommended_stock", 0),
            "유효기한": format_expiry_display(m.get("expiry_date", "")),
            "잔여 일수": f"{days}일" if days is not None else "-",
            "상태": f"{STATUS_EMOJI.get(status, '')} {status}",
            "보관 위치": m.get("location", ""),
            "관리 TIP/메모": m.get("memo", ""),
        })
    return pd.DataFrame(rows)


def history_to_dataframe(history: list[dict]) -> pd.DataFrame:
    """입출고 이력을 pandas DataFrame으로 변환합니다."""
    if not history:
        return pd.DataFrame()
    rows = []
    for h in history:
        rows.append({
            "번호": h["id"],
            "처리일": h.get("action_date", ""),
            "품명": h.get("medicine_name", ""),
            "구분": h.get("action_type", ""),
            "수량": h.get("quantity", 0),
            "처리 후 재고": h.get("stock_after", 0),
            "비고": h.get("note", ""),
        })
    return pd.DataFrame(rows)


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    """DataFrame을 엑셀 바이트로 변환합니다."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()


def create_upload_template() -> bytes:
    """엑셀 일괄 업로드용 양식(템플릿)을 생성합니다."""
    template_data = {
        "분류": ["해열·진통·소염제", "소화기계용약"],
        "품명(필수)": ["타이레놀 500mg", "훼스탈골드정"],
        "규격/단위(필수)": ["정", "정"],
        "입고수량(필수)": [100, 50],
        "권장재고": [100, 50],
        "유효기한(필수)\nYYYY-MM-DD": ["2026-12-31", "2027-06-30"],
        "보관위치": ["약장 1-A", "약장 2-B"],
        "관리TIP/메모": ["발열 시 사용", "소화불량 시 사용"],
    }
    df = pd.DataFrame(template_data)
    return to_excel_bytes(df, sheet_name="의약품_일괄등록_양식")


def create_edupaing_template(medicines: list[dict]) -> bytes:
    """에듀파인 등록용 엑셀 양식을 생성합니다."""
    rows = []
    for i, m in enumerate(medicines, 1):
        rows.append({
            "순번": i,
            "품목명": m.get("name", ""),
            "규격": m.get("spec", ""),
            "단위": "",
            "수량": m.get("current_stock", 0),
            "단가": "",
            "금액": "",
            "유효기한": m.get("expiry_date", ""),
            "보관장소": m.get("location", ""),
            "비고": m.get("memo", ""),
        })
    df = pd.DataFrame(rows)
    return to_excel_bytes(df, sheet_name="에듀파인_등록양식")


def create_ledger_template(medicines: list[dict], school_name: str) -> bytes:
    """관리대장 출력용 엑셀을 생성합니다."""
    today = date.today().strftime("%Y년 %m월 %d일")
    rows = []
    for i, m in enumerate(medicines, 1):
        status = get_medicine_status(m)
        days = days_until_expiry(m.get("expiry_date", ""))
        rows.append({
            "순번": i,
            "분류": m.get("category", ""),
            "품명": m.get("name", ""),
            "규격/단위": m.get("spec", ""),
            "현재재고": m.get("current_stock", 0),
            "권장재고": m.get("recommended_stock", 0),
            "유효기한": format_expiry_display(m.get("expiry_date", "")),
            "잔여일수": f"{days}일" if days is not None else "-",
            "상태": f"{STATUS_EMOJI.get(status, '')} {status}",
            "보관위치": m.get("location", ""),
            "관리메모": m.get("memo", ""),
            "점검일": today,
            "담당자": "",
        })
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="의약품관리대장")
        ws = writer.sheets["의약품관리대장"]
        # 열 너비 자동 조정
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 30)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════
#  엑셀 업로드 파싱
# ═══════════════════════════════════════════════════════════════════

def parse_upload_excel(file_bytes: bytes) -> tuple[list[dict], list[str]]:
    """
    업로드된 엑셀/CSV 파일을 파싱하여 의약품 등록용 딕셔너리 목록을 반환합니다.
    반환: (records, error_messages)
    """
    try:
        try:
            df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
        except Exception:
            df = pd.read_csv(io.BytesIO(file_bytes), dtype=str)
    except Exception as e:
        return [], [f"파일 읽기 실패: {str(e)}"]

    # 컬럼 정규화 (공백 제거, 줄바꿈 제거)
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    df = df.dropna(how="all")  # 완전히 빈 행 제거

    # 컬럼 매핑 (유연하게 처리)
    col_map = {
        "분류": "category",
        "품명": "name",
        "품명(필수)": "name",
        "규격": "spec",
        "규격/단위": "spec",
        "규격/단위(필수)": "spec",
        "입고수량": "current_stock",
        "입고수량(필수)": "current_stock",
        "수량": "current_stock",
        "권장재고": "recommended_stock",
        "유효기한": "expiry_date",
        "유효기한(필수)": "expiry_date",
        "유효기한(필수) YYYY-MM-DD": "expiry_date",
        "보관위치": "location",
        "관리TIP/메모": "memo",
        "관리메모": "memo",
    }

    records = []
    errors = []
    for i, row in df.iterrows():
        rec = {}
        for col, key in col_map.items():
            if col in df.columns:
                val = str(row.get(col, "")).strip()
                if val and val.lower() not in ("nan", "none", ""):
                    rec[key] = val

        # 필수 항목 체크
        if not rec.get("name"):
            errors.append(f"행 {i+2}: 품명이 없어 건너뜁니다.")
            continue

        # 숫자 변환
        for num_key in ("current_stock", "recommended_stock"):
            try:
                rec[num_key] = int(float(rec.get(num_key, 0) or 0))
            except ValueError:
                rec[num_key] = 0

        records.append(rec)

    return records, errors
