"""
models/node_model.py
Query helper untuk tabel `nodes`. Semua akses tabel nodes lewat sini,
supaya screens/ tidak perlu tahu SQL sama sekali.
"""

import re
from database.db_manager import db_manager


def get_roots():
    """Ambil semua node akar (parent_id NULL) -- ini yang muncul di Home."""
    conn = db_manager.get_connection()
    rows = conn.execute(
        "SELECT * FROM nodes WHERE parent_id IS NULL ORDER BY sort_order, nama"
    ).fetchall()
    return [dict(r) for r in rows]


def get_node(node_id):
    """Ambil satu node berdasarkan id-nya."""
    conn = db_manager.get_connection()
    row = conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)).fetchone()
    return dict(row) if row else None


def get_children(node_id):
    """Ambil semua anak langsung dari sebuah node."""
    conn = db_manager.get_connection()
    rows = conn.execute(
        "SELECT * FROM nodes WHERE parent_id = ? ORDER BY sort_order, nama",
        (node_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def create_node(nama, parent_id, ct_ratio=None, vt_ratio=None, node_type="output"):
    """
    Tambah node baru (fitur "Tambah GH"). node_key teknis dibuat otomatis
    dari nama -- pengguna cukup mengisi nama, tidak perlu mikirin id.
    Kalau nama yang sama sudah dipakai di induk yang sama, angka penanda
    ditambahkan di belakang node_key (bukan di nama tampilan) supaya tetap
    unik sesuai UNIQUE(parent_id, node_key) di skema.
    """
    conn = db_manager.get_connection()
    base_key = "GH_" + re.sub(r"[^A-Za-z0-9]+", "_", nama.strip().upper()).strip("_")
    node_key = base_key
    suffix = 1
    while conn.execute(
        "SELECT 1 FROM nodes WHERE parent_id IS ? AND node_key = ?",
        (parent_id, node_key),
    ).fetchone():
        suffix += 1
        node_key = f"{base_key}_{suffix}"

    cur = conn.execute(
        """INSERT INTO nodes (node_key, nama, parent_id, node_type, ct_ratio, vt_ratio)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (node_key, nama.strip(), parent_id, node_type, ct_ratio or None, vt_ratio or None),
    )
    conn.commit()
    return cur.lastrowid


def delete_node(node_id):
    """
    Hapus node beserta SEMUA turunannya (cascade lewat FK ON DELETE CASCADE
    di schema.sql). Kalau dipanggil dengan id node PALING ATAS suatu rantai
    gabungan OUT_X/X (current_node_id di NodeScreen, BUKAN display_node),
    otomatis seluruh rantai + anak-anaknya ikut terhapus lewat cascade --
    tidak perlu logic khusus.
    """
    conn = db_manager.get_connection()
    conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
    conn.commit()


def get_ancestor_path(node_id):
    """
    Ambil daftar node dari akar sampai node_id ini sendiri (buat breadcrumb).
    Hasil: [{'nama': 'MSS', ...}, {'nama': 'MDS 1', ...}, ...] berurutan dari atas.
    """
    path = []
    current = get_node(node_id)
    while current is not None:
        path.append(current)
        if current["parent_id"] is None:
            break
        current = get_node(current["parent_id"])
    return list(reversed(path))


def get_display_bundle(node_id):
    """
    Menangani pola "OUT_X -> X" di data sumber (mis. node "OUT_TDS1" yang
    anak tunggalnya adalah node "TDS1", dan keduanya ber-nama sama persis
    "TDS 1" -- itu 2 relay fisik berbeda tapi 1 lokasi yang sama di mata
    teknisi). Kalau pola ini terdeteksi, gabungkan jadi satu "tampilan
    efektif": kartu relay dari SEMUA node di rantai itu ditampilkan
    bersamaan, tapi tombol lanjut/anak diambil dari node PALING BAWAH
    rantai -- supaya teknisi tidak tap 2x utk 2 layar yang namanya sama.

    Rantai HANYA disambung kalau anak tunggal itu nama-nya identik dengan
    node saat ini -- node dgn nama beda (mis. MSS -> "MDS 1") tidak pernah
    digabung, walau anaknya cuma satu.
    """
    chain_ids = [node_id]
    current = get_node(node_id)
    while True:
        children = get_children(current["id"])
        if len(children) == 1 and children[0]["nama"] == current["nama"]:
            current = children[0]
            chain_ids.append(current["id"])
        else:
            break

    return {
        "chain_node_ids": chain_ids,
        "display_node": current,
        "children": get_children(current["id"]),
    }


def get_display_path(node_id):
    """
    Seperti get_ancestor_path, tapi menggabungkan pasangan OUT_X/X yang
    ber-nama sama berurutan jadi 1 entri breadcrumb (konsisten dgn
    get_display_bundle) -- supaya breadcrumb tidak menampilkan nama yang
    sama dua kali berturut-turut (mis. "TDS 1 > TDS 1").
    """
    raw_path = get_ancestor_path(node_id)
    deduped = []
    for node in raw_path:
        if deduped and deduped[-1]["nama"] == node["nama"]:
            continue
        deduped.append(node)
    return deduped
