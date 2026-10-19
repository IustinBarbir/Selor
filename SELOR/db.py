"""
db.py — MySQL access layer.
"""

import os
import getpass
from contextlib import contextmanager
from datetime import date, datetime

import mysql.connector
from mysql.connector import Error as MySQLError

from config import get_db_config

TABLE = "selling_partner_cases"


DEFAULT_SEARCH_LIMIT = 2000



CASE_TYPES = ["DR", "SA"]
SP_TYPES = ["Vendor", "Seller", "N/A"]
SP_TYPES_VIEW = ["Vendor", "Seller"]
BUSINESS_MODELS = ["FBA", "MFN", "N/A"]
MARKETPLACES = ["UK", "DE", "FR", "IT", "ES", "N/A"]
CASE_STATUSES = ["Approved", "Not Approved", "Other", "Pending Review"]

CASE_REASON_CODES = {
    "Approved": [
        "Correct First Submission",
        "Correct Re-Submission",
        "ASIN exempt",
    ],
    "Not Approved": [
        "All documents missing",
        "Forged_Document_Confirmed",
        "General Queries from Seller",
        "Multiple rejection reasons",
        "Other (See Annotation)",
        "Product Images non-compliant",
        "Product_Images_missing",
        "Resolve request / Testing refusal",
        "Non Compliant Documents",
        "Out of Scope",
    ],
    "Other": [
        "ASIN-False Positive",
    ],
    "Pending Review": [
        "Escalated to SME",
        "Escalated to Program Team",
    ],
}


class DBError(RuntimeError):
    pass


@contextmanager
def get_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**get_db_config(), connection_timeout=8)
        yield conn
    except MySQLError as e:
        raise DBError(f"Could not connect to the database: {e}") from e
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def get_uploader() -> str:
    return os.environ.get("USERNAME") or os.environ.get("USER") or getpass.getuser()




def insert_case(data: dict) -> None:
    query = f"""
        INSERT INTO {TABLE} (
            case_type, case_id, sp_type,
            sp_identifier, sp_identifier_na,
            seller_business_model,
            sp_name, sp_name_na,
            asin, asin_na,
            marketplace, case_status, case_reason_code,
            expiry_date, expiry_na, case_date,
            notes, uploader, upload_date
        ) VALUES (
            %(case_type)s, %(case_id)s, %(sp_type)s,
            %(sp_identifier)s, %(sp_identifier_na)s,
            %(seller_business_model)s,
            %(sp_name)s, %(sp_name_na)s,
            %(asin)s, %(asin_na)s,
            %(marketplace)s, %(case_status)s, %(case_reason_code)s,
            %(expiry_date)s, %(expiry_na)s, %(case_date)s,
            %(notes)s, %(uploader)s, %(upload_date)s
        )
    """
    params = dict(data)
    params.setdefault("notes", None)
    params.setdefault("case_date", None)
    params["uploader"] = get_uploader()
    params["upload_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
        except MySQLError as e:
            conn.rollback()
            raise DBError(f"Error saving the case: {e}") from e
        finally:
            cursor.close()




def fetch_cases(filters: dict, limit=DEFAULT_SEARCH_LIMIT) -> list:

    clauses = []
    params: dict = {}

    if filters.get("sp_identifier"):
        clauses.append("t.sp_identifier LIKE %(sp_identifier)s")
        params["sp_identifier"] = f"%{filters['sp_identifier']}%"

    if filters.get("case_id"):
        clauses.append("t.case_id LIKE %(case_id)s")
        params["case_id"] = f"%{filters['case_id']}%"

    if filters.get("asin"):
        clauses.append("t.asin LIKE %(asin)s")
        params["asin"] = f"%{filters['asin']}%"

    if filters.get("case_type"):
        clauses.append("t.case_type = %(case_type)s")
        params["case_type"] = filters["case_type"]

    if filters.get("sp_type"):
        clauses.append("t.sp_type = %(sp_type)s")
        params["sp_type"] = filters["sp_type"]

    if filters.get("marketplace"):
        clauses.append("t.marketplace = %(marketplace)s")
        params["marketplace"] = filters["marketplace"]

    if filters.get("case_statuses"):
        st_clauses = []
        for i, val in enumerate(filters["case_statuses"]):
            key = f"status_{i}"
            st_clauses.append(f"%({key})s")
            params[key] = val
        clauses.append(f"t.case_status IN ({', '.join(st_clauses)})")

    if filters.get("reason_codes"):
        rc_clauses = []
        for i, val in enumerate(filters["reason_codes"]):
            key = f"reason_{i}"
            rc_clauses.append(f"%({key})s")
            params[key] = val
        clauses.append(f"t.case_reason_code IN ({', '.join(rc_clauses)})")

    if filters.get("exp_date_from") or filters.get("exp_date_to"):
        d_from = filters.get("exp_date_from") or date(1990, 1, 1)
        d_to = filters.get("exp_date_to") or date(2400, 1, 1)
        clauses.append("t.expiry_date BETWEEN %(exp_date_from)s AND %(exp_date_to)s")
        params["exp_date_from"] = d_from
        params["exp_date_to"] = d_to

    if filters.get("case_date_from") or filters.get("case_date_to"):
        cd_from = filters.get("case_date_from") or date(1990, 1, 1)
        cd_to = filters.get("case_date_to") or date(2400, 1, 1)
        clauses.append("t.case_date BETWEEN %(case_date_from)s AND %(case_date_to)s")
        params["case_date_from"] = cd_from
        params["case_date_to"] = cd_to

    if filters.get("cert_status"):
        if filters["cert_status"] == "Valid":
            clauses.append("(t.expiry_na = 0 AND t.expiry_date >= CURDATE())")
        elif filters["cert_status"] == "Expired":
            clauses.append("(t.expiry_na = 0 AND t.expiry_date < CURDATE())")
        elif filters["cert_status"] == "N/A":
            clauses.append("t.expiry_na = 1")

    rank_clause = "rnk >= 1" if filters.get("historical", True) else "rnk = 1"
    clauses.append(rank_clause)

    where_sql = " AND ".join(clauses) if clauses else "1 = 1"
    limit_sql = f"LIMIT {int(limit)}" if limit is not None else ""

    query = f"""
        WITH sp_validity AS (
            SELECT sp_identifier,
                   MAX(CASE WHEN expiry_na = 0 AND expiry_date >= CURDATE() THEN 1 ELSE 0 END) AS has_valid_cert
            FROM {TABLE}
            GROUP BY sp_identifier
        ),
        ranked AS (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY sp_identifier ORDER BY expiry_date DESC) AS rnk
            FROM {TABLE}
        )
        SELECT
            t.id, t.case_type, t.case_id, t.sp_type, t.sp_identifier,
            t.seller_business_model, t.sp_name, t.asin, t.marketplace,
            t.case_status, t.case_reason_code,
            COALESCE(t.expiry_date, 'N/A') AS expiry_date,
            CASE
                WHEN t.expiry_na = 1 THEN 'N/A'
                WHEN t.expiry_date >= CURDATE() THEN 'Valid'
                ELSE 'Expired'
            END AS cert_status,
            COALESCE(v.has_valid_cert, 0) AS has_valid_cert_any_row,
            COALESCE(t.case_date, 'N/A') AS case_date,
            t.notes, t.uploader
        FROM ranked t
        LEFT JOIN sp_validity v ON v.sp_identifier = t.sp_identifier
        WHERE {where_sql}
        ORDER BY t.id DESC
        {limit_sql}
    """

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except MySQLError as e:
            raise DBError(f"Query error: {e}") from e
        finally:
            cursor.close()




EXPORT_HEADERS = [
    "Case Type", "Case ID", "SP Type", "Partner ID/Vendor Code",
    "Seller Business Model", "SP Name", "ASIN", "MP", "Case Status",
    "Case Reason Code", "Expiry Date", "Certificate Status",
    "Has Valid Cert (any row)", "Case Date", "User",
]


def export_to_excel(rows: list, output_path: str) -> str:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Export"
    ws.append(EXPORT_HEADERS)

    for r in rows:
        ws.append([
            r.get("case_type"), r.get("case_id"), r.get("sp_type"), r.get("sp_identifier"),
            r.get("seller_business_model"), r.get("sp_name"), r.get("asin"), r.get("marketplace"),
            r.get("case_status"), r.get("case_reason_code"), r.get("expiry_date"),
            r.get("cert_status"), "Yes" if r.get("has_valid_cert_any_row") else "No",
            r.get("case_date"), r.get("uploader"),
        ])

    for col in ws.columns:
        max_len = max((len(str(c.value)) for c in col if c.value is not None), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 45)

    wb.save(output_path)
    return output_path
