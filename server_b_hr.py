from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Agent B - HR Knowledge Base")

KB_DIR = Path(__file__).parent / "knowledge_base" / "hr"


def load_all_docs() -> list[dict]:
    """Membaca semua file .md dari folder knowledge base HR."""
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
def search_hr_docs(query: str) -> str:
    """
    Mencari informasi dalam Knowledge Base Dokumen HR (kebijakan cuti, onboarding, dll.).
    Gunakan tool ini untuk pertanyaan seputar kebijakan SDM, cuti, masa percobaan, onboarding karyawan.
    Parameter:
        query: Kata kunci atau pertanyaan yang ingin dicari di dokumen HR.
    """
    docs = load_all_docs()
    query_lower = query.lower()

    results = []
    for doc in docs:
        # Score sederhana: hitung berapa banyak kata dari query yang muncul di konten
        keywords = query_lower.split()
        content_lower = doc["content"].lower()
        score = sum(1 for kw in keywords if kw in content_lower)

        if score > 0:
            # Ambil potongan konten yang relevan
            lines = doc["content"].split("\n")
            relevant_lines = [
                line for line in lines
                if any(kw in line.lower() for kw in keywords) and line.strip()
            ]
            snippet = "\n".join(relevant_lines[:10])  # Ambil max 10 baris relevan
            results.append({
                "source": doc["filename"],
                "title": doc["title"],
                "score": score,
                "snippet": snippet
            })

    if not results:
        return "Tidak ditemukan dokumen HR yang relevan dengan query tersebut."

    # Urutkan berdasarkan score tertinggi
    results.sort(key=lambda x: x["score"], reverse=True)

    output_parts = [f"=== Hasil Pencarian HR untuk: '{query}' ===\n"]
    for r in results:
        output_parts.append(f"📄 Sumber: {r['title']} ({r['source']})")
        output_parts.append(r["snippet"])
        output_parts.append("")

    return "\n".join(output_parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")
