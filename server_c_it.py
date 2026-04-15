import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Agent C - IT Policy Server (Audited)")

KB_DIR = Path(__file__).parent / "knowledge_base" / "it"
KB_AUDITOR_DIR = Path(__file__).parent / "knowledge_base" / "auditor"

# Matriks akses yang diizinkan per role
ACCESS_MATRIX = {
    "staff":        ["portal_internal", "email", "hr_system"],
    "senior staff": ["portal_internal", "email", "hr_system", "staging_server"],
    "supervisor":   ["portal_internal", "email", "hr_system", "staging_server", "reporting"],
    "manager":      ["portal_internal", "email", "hr_system", "staging_server", "reporting", "production_readonly"],
    "director":     ["portal_internal", "email", "hr_system", "staging_server", "reporting", "production_readonly", "production_server", "finance_system"],
}


def load_all_docs() -> list[dict]:
    """Membaca semua file .md dari folder knowledge base IT."""
    docs = []
    if not KB_DIR.exists():
        return docs
    for md_file in KB_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        docs.append({
            "filename": md_file.name,
            "title": md_file.stem.replace("_", " ").title(),
            "content": content
        })
    return docs


@mcp.tool()
def search_it_policies(query: str, role: str = "") -> str:
    """
    Mencari informasi dalam Knowledge Base Kebijakan IT (akses server, password policy, dll.).
    Gunakan tool ini untuk pertanyaan seputar keamanan IT, izin akses sistem, kebijakan password.
    Parameter:
        query: Kata kunci atau pertanyaan yang ingin dicari di dokumen IT.
        role: (Opsional) Role spesifik karyawan yang ingin dicek kebijakannya (misal: 'Staff', 'Manager').
    """
    docs = load_all_docs()

    # Gabungkan query dengan role jika diberikan
    full_query = f"{query} {role}".strip().lower()
    keywords = full_query.split()

    results = []
    for doc in docs:
        content_lower = doc["content"].lower()
        score = sum(1 for kw in keywords if kw in content_lower)

        if score > 0:
            lines = doc["content"].split("\n")

            # Jika ada role, prioritaskan baris yang mengandung nama role tersebut
            if role:
                relevant_lines = [
                    line for line in lines
                    if (role.lower() in line.lower() or
                        any(kw in line.lower() for kw in query.lower().split())) and line.strip()
                ]
            else:
                relevant_lines = [
                    line for line in lines
                    if any(kw in line.lower() for kw in keywords) and line.strip()
                ]

            snippet = "\n".join(relevant_lines[:12])
            results.append({
                "source": doc["filename"],
                "title": doc["title"],
                "score": score,
                "snippet": snippet
            })

    if not results:
        return "Tidak ditemukan kebijakan IT yang relevan dengan query tersebut."

    results.sort(key=lambda x: x["score"], reverse=True)

    output_parts = [f"=== Hasil Pencarian Kebijakan IT untuk: '{query}' (role: {role or 'semua'}) ===\n"]
    for r in results:
        output_parts.append(f"📄 Sumber: {r['title']} ({r['source']})")
        output_parts.append(r["snippet"])
        output_parts.append("")

    return "\n".join(output_parts)


def load_auditor_docs() -> list[dict]:
    """Membaca semua file .md dari knowledge base auditor."""
    docs = []
    if not KB_AUDITOR_DIR.exists():
        return docs
    for md_file in KB_AUDITOR_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        docs.append({
            "filename": md_file.name,
            "title": md_file.stem.replace("_", " ").title(),
            "content": content
        })
    return docs


def keyword_search(docs: list[dict], query: str, max_lines: int = 12) -> list[dict]:
    """Melakukan pencarian keyword sederhana dan mengembalikan hasil relevan."""
    query_lower = query.lower()
    keywords = query_lower.split()
    results = []

    for doc in docs:
        content_lower = doc["content"].lower()
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            lines = doc["content"].split("\n")
            relevant_lines = [
                line for line in lines
                if any(kw in line.lower() for kw in keywords) and line.strip()
            ]
            snippet = "\n".join(relevant_lines[:max_lines])
            results.append({
                "source": doc["filename"],
                "title": doc["title"],
                "score": score,
                "snippet": snippet
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


@mcp.tool()
def search_audit_policies(query: str) -> str:
    """
    Mencari informasi dalam Knowledge Base Kebijakan Audit Internal Auresys.
    Gunakan tool ini untuk pertanyaan seputar prosedur audit, wewenang auditor,
    indikator risiko (red flags), sanksi pelanggaran, dan frekuensi audit.
    Parameter:
        query: Kata kunci atau pertanyaan terkait kebijakan audit.
    """
    docs = [d for d in load_auditor_docs() if "audit" in d["filename"]]
    results = keyword_search(docs, query)

    if not results:
        return "Tidak ditemukan kebijakan audit yang relevan dengan query tersebut."

    output_parts = [f"=== Hasil Pencarian Kebijakan Audit untuk: '{query}' ===\n"]
    for r in results:
        output_parts.append(f"📋 Sumber: {r['title']} ({r['source']})")
        output_parts.append(r["snippet"])
        output_parts.append("")

    return "\n".join(output_parts)


@mcp.tool()
def search_monitoring_docs(query: str) -> str:
    """
    Mencari informasi dalam Knowledge Base Monitoring Sistem & SLA Auresys.
    Gunakan tool ini untuk pertanyaan seputar SLA, metrik monitoring, prosedur
    respons insiden, severity level, retensi log, dan alat monitoring.
    Parameter:
        query: Kata kunci atau pertanyaan terkait monitoring.
    """
    docs = [d for d in load_auditor_docs() if "monitoring" in d["filename"]]
    results = keyword_search(docs, query)

    if not results:
        return "Tidak ditemukan dokumen monitoring yang relevan dengan query tersebut."

    output_parts = [f"=== Hasil Pencarian Monitoring untuk: '{query}' ===\n"]
    for r in results:
        output_parts.append(f"📊 Sumber: {r['title']} ({r['source']})")
        output_parts.append(r["snippet"])
        output_parts.append("")

    return "\n".join(output_parts)


@mcp.tool()
def check_access_violation(role: str, system: str) -> str:
    """
    Memeriksa apakah seorang karyawan dengan role tertentu memiliki hak akses
    ke suatu sistem. Digunakan untuk audit kepatuhan akses dan deteksi pelanggaran.
    Parameter:
        role:   Role/jabatan karyawan (contoh: 'Staff', 'Manager', 'Director').
        system: Nama sistem yang diakses (contoh: 'production_server', 'finance_system', 'staging_server').
    """
    role_lower = role.lower().strip()
    system_lower = system.lower().strip().replace(" ", "_")

    allowed_systems = ACCESS_MATRIX.get(role_lower)

    if allowed_systems is None:
        return json.dumps({
            "status": "ROLE_TIDAK_DIKENAL",
            "pesan": f"Role '{role}' tidak ada dalam matriks akses.",
            "role_tersedia": list(ACCESS_MATRIX.keys())
        }, ensure_ascii=False, indent=2)

    is_authorized = system_lower in allowed_systems

    if is_authorized:
        status = "✅ AKSES DIIZINKAN"
        flag = False
        rekomendasi = f"Role '{role}' memiliki hak akses ke '{system}'. Tidak ada pelanggaran."
    else:
        status = "🚨 PELANGGARAN AKSES TERDETEKSI"
        flag = True
        rekomendasi = (
            f"Role '{role}' TIDAK diizinkan mengakses '{system}'. "
            "Insiden ini harus dilaporkan ke IT Security dan dicatat dalam Lembar Kerja Audit (LKA). "
            "Jika ini adalah akses ke production_server, eskalasi segera ke Chief Auditor."
        )

    return json.dumps({
        "status": status,
        "pelanggaran_terdeteksi": flag,
        "role": role,
        "sistem_diakses": system,
        "sistem_diizinkan_untuk_role": allowed_systems,
        "rekomendasi": rekomendasi
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
