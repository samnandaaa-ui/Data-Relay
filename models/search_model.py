"""
models/search_model.py
Pencarian node berdasarkan nama (parsial, tidak peka huruf besar/kecil).
Hasil diarahkan lewat get_display_bundle supaya konsisten dengan node_screen
(kalau match ada di pasangan OUT_X/X yang digabung, hasilnya 1, bukan 2).
"""

from database.db_manager import db_manager
from models.node_model import get_display_bundle, get_display_path


def search_nodes(query):
    """Kembalikan list hasil siap-tampil: {node_id, nama, breadcrumb}."""
    query = query.strip()
    if not query:
        return []

    conn = db_manager.get_connection()
    rows = conn.execute(
        "SELECT id FROM nodes WHERE nama LIKE ? COLLATE NOCASE ORDER BY nama",
        (f"%{query}%",),
    ).fetchall()

    results = []
    seen_display_ids = set()
    for row in rows:
        bundle = get_display_bundle(row["id"])
        display_node = bundle["display_node"]
        if display_node["id"] in seen_display_ids:
            continue
        seen_display_ids.add(display_node["id"])

        path = get_display_path(display_node["id"])
        results.append({
            "node_id": display_node["id"],
            "nama": display_node["nama"],
            "breadcrumb": " > ".join(p["nama"] for p in path[:-1]),
        })
    return results
