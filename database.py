"""
데이터베이스 초기화 및 관리 모듈
SQLite 기반 보건실 의약품 재고 관리 데이터베이스
"""

import sqlite3
import hashlib
import os
from datetime import datetime

# 데이터베이스 파일 경로
DB_PATH = os.path.join(os.path.dirname(__file__), "health_inventory.db")


def get_connection():
    """데이터베이스 연결을 반환합니다."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
    return conn


def hash_password(password: str) -> str:
    """비밀번호를 SHA-256으로 해싱합니다."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_database():
    """데이터베이스 테이블을 초기화합니다."""
    conn = get_connection()
    cursor = conn.cursor()

    # ─── 학교 계정 테이블 ───────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # ─── 의약품 재고 테이블 ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER NOT NULL,
            category TEXT DEFAULT '',
            name TEXT NOT NULL,
            spec TEXT DEFAULT '',
            current_stock INTEGER DEFAULT 0,
            recommended_stock INTEGER DEFAULT 0,
            expiry_date TEXT DEFAULT '',
            location TEXT DEFAULT '',
            memo TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (school_id) REFERENCES schools(id)
        )
    """)

    # ─── 입출고 이력 테이블 ─────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            action_type TEXT NOT NULL,   -- '입고' / '출고' / '폐기' / '수정'
            quantity INTEGER NOT NULL,
            stock_after INTEGER NOT NULL,
            note TEXT DEFAULT '',
            action_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (school_id) REFERENCES schools(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
#  학교 계정 관련 함수
# ═══════════════════════════════════════════════════════════════════

def register_school(school_name: str, password: str) -> tuple[bool, str]:
    """새 학교 계정을 등록합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO schools (school_name, password_hash, created_at) VALUES (?, ?, ?)",
            (school_name.strip(), hash_password(password), datetime.now().isoformat()),
        )
        conn.commit()
        return True, "계정이 성공적으로 등록되었습니다."
    except sqlite3.IntegrityError:
        return False, "이미 등록된 학교명입니다. 다른 학교명을 사용해 주세요."
    finally:
        conn.close()


def login_school(school_name: str, password: str) -> tuple[bool, dict | None]:
    """학교 계정으로 로그인합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM schools WHERE school_name = ? AND password_hash = ?",
        (school_name.strip(), hash_password(password)),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return True, dict(row)
    return False, None


def delete_school(school_id: int) -> tuple[bool, str]:
    """학교 계정과 모든 관련 데이터를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 입출고 이력 삭제
        cursor.execute("DELETE FROM stock_history WHERE school_id = ?", (school_id,))
        # 의약품 삭제
        cursor.execute("DELETE FROM medicines WHERE school_id = ?", (school_id,))
        # 학교 계정 삭제
        cursor.execute("DELETE FROM schools WHERE id = ?", (school_id,))
        conn.commit()
        return True, "학교 계정과 모든 데이터가 삭제되었습니다."
    except Exception as e:
        return False, f"삭제 실패: {str(e)}"
    finally:
        conn.close()


def get_all_schools_admin() -> list[dict]:
    """[관리자 전용] 모든 학교 계정 목록을 반환합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schools ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def admin_reset_password(school_id: int, new_password: str) -> tuple[bool, str]:
    """[관리자 전용] 학교 비밀번호를 초기화합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE schools SET password_hash = ? WHERE id = ?",
            (hash_password(new_password), school_id),
        )
        conn.commit()
        return True, "비밀번호가 변경되었습니다."
    except Exception as e:
        return False, f"변경 실패: {str(e)}"
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════
#  의약품 관련 함수
# ═══════════════════════════════════════════════════════════════════

def add_medicine(school_id: int, data: dict) -> tuple[bool, str]:
    """의약품을 새로 등록합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            INSERT INTO medicines
                (school_id, category, name, spec, current_stock,
                 recommended_stock, expiry_date, location, memo,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            school_id,
            data.get("category", ""),
            data["name"],
            data.get("spec", ""),
            data.get("current_stock", 0),
            data.get("recommended_stock", 0),
            data.get("expiry_date", ""),
            data.get("location", ""),
            data.get("memo", ""),
            now, now,
        ))
        medicine_id = cursor.lastrowid
        # 입고 이력 기록
        if data.get("current_stock", 0) > 0:
            cursor.execute("""
                INSERT INTO stock_history
                    (school_id, medicine_id, medicine_name, action_type,
                     quantity, stock_after, note, action_date, created_at)
                VALUES (?, ?, ?, '입고', ?, ?, ?, ?, ?)
            """, (
                school_id, medicine_id, data["name"],
                data.get("current_stock", 0),
                data.get("current_stock", 0),
                data.get("note", "최초 등록"),
                datetime.now().strftime("%Y-%m-%d"),
                now,
            ))
        conn.commit()
        return True, f"'{data['name']}' 이(가) 성공적으로 등록되었습니다."
    except Exception as e:
        return False, f"등록 실패: {str(e)}"
    finally:
        conn.close()


def get_medicines(school_id: int, category: str = None, search: str = None) -> list[dict]:
    """의약품 목록을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM medicines WHERE school_id = ?"
    params = [school_id]
    if category and category != "전체":
        query += " AND category = ?"
        params.append(category)
    if search:
        query += " AND (name LIKE ? OR spec LIKE ? OR location LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    query += " ORDER BY expiry_date ASC, name ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_medicine_by_id(medicine_id: int) -> dict | None:
    """ID로 의약품을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_medicine(medicine_id: int, data: dict) -> tuple[bool, str]:
    """의약품 정보를 수정합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            UPDATE medicines SET
                category = ?, name = ?, spec = ?,
                recommended_stock = ?, expiry_date = ?,
                location = ?, memo = ?, updated_at = ?
            WHERE id = ?
        """, (
            data.get("category", ""),
            data["name"],
            data.get("spec", ""),
            data.get("recommended_stock", 0),
            data.get("expiry_date", ""),
            data.get("location", ""),
            data.get("memo", ""),
            now,
            medicine_id,
        ))
        conn.commit()
        return True, "수정되었습니다."
    except Exception as e:
        return False, f"수정 실패: {str(e)}"
    finally:
        conn.close()


def update_stock(school_id: int, medicine_id: int, action_type: str,
                 quantity: int, note: str = "") -> tuple[bool, str]:
    """
    재고를 입출고 처리합니다.
    action_type: '입고' | '불출' (또는 '출고') | '폐기'
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("SELECT * FROM medicines WHERE id = ? AND school_id = ?",
                   (medicine_id, school_id))
    med = cursor.fetchone()
    if not med:
        conn.close()
        return False, "해당 약품을 찾을 수 없습니다."

    current = med["current_stock"]
    if action_type == "입고":
        new_stock = current + quantity
    else:  # 불출 / 출고 / 폐기
        if quantity > current:
            conn.close()
            return False, f"재고 부족: 현재 재고({current})보다 많은 수량을 처리할 수 없습니다."
        new_stock = current - quantity

    cursor.execute(
        "UPDATE medicines SET current_stock = ?, updated_at = ? WHERE id = ?",
        (new_stock, now, medicine_id)
    )
    cursor.execute("""
        INSERT INTO stock_history
            (school_id, medicine_id, medicine_name, action_type,
             quantity, stock_after, note, action_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        school_id, medicine_id, med["name"], action_type,
        quantity, new_stock, note,
        datetime.now().strftime("%Y-%m-%d"), now,
    ))
    conn.commit()
    conn.close()
    return True, f"'{med['name']}' {action_type} 처리 완료. 현재 재고: {new_stock}"


def rollback_last_stock_action(school_id: int, medicine_id: int) -> tuple[bool, str]:
    """
    해당 약품의 가장 최근 입출고/불출/폐기 작업을 1단계 이전으로 되돌립니다.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        # 최근 이력 1건 조회
        cursor.execute("""
            SELECT * FROM stock_history
            WHERE school_id = ? AND medicine_id = ?
            ORDER BY id DESC LIMIT 1
        """, (school_id, medicine_id))
        last_hist = cursor.fetchone()
        if not last_hist:
            return False, "되돌릴 수 있는 이전 입출고 내역이 없습니다."

        cursor.execute("SELECT * FROM medicines WHERE id = ? AND school_id = ?",
                       (medicine_id, school_id))
        med = cursor.fetchone()
        if not med:
            return False, "약품 정보를 찾을 수 없습니다."

        atype = last_hist["action_type"]
        qty = last_hist["quantity"]
        curr = med["current_stock"]

        # 원래대로 복원 계산
        if atype == "입고":
            if curr < qty:
                return False, f"현재 재고({curr})가 입고 취소 수량({qty})보다 적어 되돌릴 수 없습니다."
            restored_stock = curr - qty
        else:  # 불출 / 출고 / 폐기
            restored_stock = curr + qty

        # 약품 재고 복원
        cursor.execute("UPDATE medicines SET current_stock = ?, updated_at = ? WHERE id = ?",
                       (restored_stock, now, medicine_id))

        # 되돌린 이력 레코드 삭제
        cursor.execute("DELETE FROM stock_history WHERE id = ?", (last_hist["id"],))
        conn.commit()
        return True, f"최근 '{atype}'({qty}개) 작업이 취소되고, 현재 재고가 {restored_stock}개로 복원되었습니다."
    except Exception as e:
        return False, f"되돌리기 실패: {str(e)}"
    finally:
        conn.close()


def delete_medicines(medicine_ids: list[int]) -> tuple[bool, str]:
    """선택한 의약품들을 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        placeholders = ",".join(["?"] * len(medicine_ids))
        cursor.execute(f"DELETE FROM stock_history WHERE medicine_id IN ({placeholders})",
                       medicine_ids)
        cursor.execute(f"DELETE FROM medicines WHERE id IN ({placeholders})",
                       medicine_ids)
        conn.commit()
        return True, f"{len(medicine_ids)}개 품목이 삭제되었습니다."
    except Exception as e:
        return False, f"삭제 실패: {str(e)}"
    finally:
        conn.close()


def bulk_insert_medicines(school_id: int, records: list[dict]) -> tuple[int, list[str]]:
    """엑셀에서 불러온 의약품 목록을 일괄 등록합니다."""
    success_count = 0
    errors = []
    for i, rec in enumerate(records, 1):
        if not rec.get("name"):
            errors.append(f"행 {i}: 품명이 없어 건너뜁니다.")
            continue
        ok, msg = add_medicine(school_id, rec)
        if ok:
            success_count += 1
        else:
            errors.append(f"행 {i} ({rec.get('name', '?')}): {msg}")
    return success_count, errors


# ═══════════════════════════════════════════════════════════════════
#  입출고 이력 관련 함수
# ═══════════════════════════════════════════════════════════════════

def get_stock_history(school_id: int, medicine_id: int = None,
                      limit: int = 200) -> list[dict]:
    """입출고 이력을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    if medicine_id:
        cursor.execute("""
            SELECT * FROM stock_history
            WHERE school_id = ? AND medicine_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (school_id, medicine_id, limit))
    else:
        cursor.execute("""
            SELECT * FROM stock_history
            WHERE school_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (school_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_history_records(history_ids: list[int]) -> tuple[bool, str]:
    """선택한 이력 레코드를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        placeholders = ",".join(["?"] * len(history_ids))
        cursor.execute(f"DELETE FROM stock_history WHERE id IN ({placeholders})",
                       history_ids)
        conn.commit()
        return True, f"{len(history_ids)}개 이력이 삭제되었습니다."
    except Exception as e:
        return False, f"삭제 실패: {str(e)}"
    finally:
        conn.close()
