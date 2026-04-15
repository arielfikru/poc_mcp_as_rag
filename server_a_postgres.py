import json
import os
import sqlite3
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Agent A - Database Server (Audited)")

# Benchmark gaji per role untuk deteksi anomali
SALARY_BENCHMARK = {
    "staff":        {"min": 4_000_000,  "max": 8_000_000,  "avg": 5_500_000},
    "senior staff": {"min": 7_000_000,  "max": 12_000_000, "avg": 9_000_000},
    "supervisor":   {"min": 8_000_000,  "max": 15_000_000, "avg": 11_000_000},
    "manager":      {"min": 12_000_000, "max": 22_000_000, "avg": 16_000_000},
    "director":     {"min": 20_000_000, "max": 40_000_000, "avg": 28_000_000},
}

DB_PATH = Path(__file__).parent / "auresys_poc.db"

def get_db_connection():
    """Membuat koneksi ke SQLite database dan return connection object."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Agar hasil query bisa diakses seperti dict
    return conn

def init_db():
    """Inisialisasi database dan seed data jika belum ada."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            salary INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    # Cek apakah sudah ada data
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    if count == 0:
        employees = [
            (101, "Budi Santoso", "Staff", "Engineering", 5000000, "budi.santoso@auresys.id"),
            (102, "Siti Rahayu", "Manager", "Engineering", 15000000, "siti.rahayu@auresys.id"),
            (103, "Ahmad Fauzi", "Senior Staff", "IT Security", 8500000, "ahmad.fauzi@auresys.id"),
            (104, "Dewi Permata", "Director", "Product", 25000000, "dewi.permata@auresys.id"),
            (105, "Rizky Pratama", "Supervisor", "HR", 10000000, "rizky.pratama@auresys.id"),
            (106, "Lina Marlina", "Staff", "Marketing", 5500000, "lina.marlina@auresys.id"),
        ]
        cursor.executemany(
            "INSERT INTO employees (id, name, role, department, salary, email) VALUES (?, ?, ?, ?, ?, ?)",
            employees
        )
        conn.commit()
    conn.close()

# Inisialisasi DB saat module diload
init_db()


@mcp.tool()
def get_user_info(user_id: str) -> str:
    """
    Mencari informasi lengkap seorang karyawan berdasarkan ID karyawan mereka.
    Mengembalikan nama, role, departemen, gaji, dan email karyawan.
    Parameter:
        user_id: Nomor ID karyawan (contoh: '101', '103', '105').
    """
    # BUGFIX: Tangani error jika user_id bukan angka
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return json.dumps({
            "error": f"Format user_id tidak valid: '{user_id}'. "
                     "Harap gunakan ID numerik (contoh: '101'). "
                     "Gunakan tool search_employee_by_name jika ingin mencari berdasarkan nama."
        }, ensure_ascii=False)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?", (user_id_int,))
    row = cursor.fetchone()
    conn.close()

    if row:
        result = dict(row)
        return json.dumps(result, ensure_ascii=False)
    else:
        return json.dumps({
            "error": f"Karyawan dengan ID {user_id} tidak ditemukan.",
            "hint": "Gunakan tool list_employees untuk melihat daftar ID yang tersedia."
        }, ensure_ascii=False)


@mcp.tool()
def search_employee_by_name(name: str) -> str:
    """
    Mencari karyawan berdasarkan nama (partial match, tidak case-sensitive).
    Berguna ketika hanya mengetahui nama karyawan tanpa ID-nya.
    Parameter:
        name: Nama atau sebagian nama karyawan yang ingin dicari.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM employees WHERE LOWER(name) LIKE ?",
        (f"%{name.lower()}%",)
    )
    rows = cursor.fetchall()
    conn.close()

    if rows:
        result = [dict(row) for row in rows]
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "error": f"Tidak ditemukan karyawan dengan nama mengandung '{name}'.",
            "hint": "Gunakan tool list_employees untuk melihat daftar seluruh karyawan."
        }, ensure_ascii=False)


@mcp.tool()
def list_employees() -> str:
    """
    Menampilkan daftar seluruh karyawan yang ada di database beserta informasi dasar mereka
    (ID, nama, role, departemen). Berguna untuk mendapatkan gambaran umum atau mencari ID karyawan.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, role, department FROM employees ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    employees = [dict(row) for row in rows]
    return json.dumps(employees, ensure_ascii=False, indent=2)


@mcp.tool()
def get_department_summary() -> str:
    """
    Menampilkan ringkasan statistik karyawan per departemen:
    jumlah karyawan, total gaji, dan rata-rata gaji.
    Berguna untuk monitoring, pelaporan manajemen, dan analisis SDM.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            department,
            COUNT(*) as jumlah_karyawan,
            SUM(salary) as total_gaji,
            ROUND(AVG(salary), 0) as rata_rata_gaji,
            MIN(salary) as gaji_terendah,
            MAX(salary) as gaji_tertinggi
        FROM employees
        GROUP BY department
        ORDER BY department
    """)
    rows = cursor.fetchall()
    conn.close()

    summary = [dict(row) for row in rows]
    return json.dumps({
        "departemen": summary,
        "total_karyawan_perusahaan": sum(d["jumlah_karyawan"] for d in summary)
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def check_salary_anomaly(salary: int, role: str) -> str:
    """
    Memeriksa apakah gaji seorang karyawan wajar atau berpotensi anomali
    berdasarkan benchmark gaji per role di perusahaan.
    Digunakan dalam audit payroll untuk mendeteksi penyimpangan.
    Parameter:
        salary: Gaji karyawan dalam Rupiah (contoh: 5000000).
        role:   Role/jabatan karyawan (contoh: 'Staff', 'Manager', 'Director').
    """
    role_lower = role.lower().strip()
    benchmark = SALARY_BENCHMARK.get(role_lower)

    if not benchmark:
        available = list(SALARY_BENCHMARK.keys())
        return json.dumps({
            "status": "ROLE_TIDAK_DIKENAL",
            "pesan": f"Role '{role}' tidak ada dalam benchmark. Role yang tersedia: {available}",
            "rekomendasi": "Verifikasi manual diperlukan."
        }, ensure_ascii=False, indent=2)

    pct_vs_avg = round((salary / benchmark["avg"] - 1) * 100, 1)
    pct_vs_max = round((salary / benchmark["max"]) * 100, 1)

    if salary < benchmark["min"]:
        status = "⚠️ ANOMALI - DI BAWAH MINIMUM"
        flag = True
        rekomendasi = "Gaji di bawah batas minimum untuk role ini. Periksa kontrak dan keputusan pengangkatan."
    elif salary > benchmark["max"] * 1.5:
        status = "🚨 ANOMALI KRITIS - JAUH DI ATAS MAKSIMUM"
        flag = True
        rekomendasi = "Gaji melebihi 150% batas maksimum. Diperlukan investigasi dan persetujuan Direktur."
    elif salary > benchmark["max"]:
        status = "⚠️ ANOMALI - DI ATAS MAKSIMUM"
        flag = True
        rekomendasi = "Gaji melampaui batas maksimum. Perlu justifikasi tertulis dari Manajer HRD."
    else:
        status = "✅ WAJAR"
        flag = False
        rekomendasi = "Gaji berada dalam rentang normal untuk role ini."

    return json.dumps({
        "status": status,
        "perlu_investigasi": flag,
        "role": role,
        "gaji_diperiksa": salary,
        "benchmark": benchmark,
        "persentase_vs_rata_rata": f"{pct_vs_avg:+.1f}%",
        "persentase_vs_maksimum": f"{pct_vs_max:.1f}%",
        "rekomendasi": rekomendasi
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
