"""
database/importer.py
Import data relay dari relay_database.json (assets/) ke SQLite.

File JSON sumbernya berisi 5 objek JSON terpisah yang ditempel berurutan
(bukan satu dokumen JSON valid, bukan array) -- fungsi _load_json_objects
membaca itu dengan aman. Aman dijalankan berkali-kali: import_all() akan
menghapus data hierarki lama dulu sebelum menulis ulang (idempotent),
supaya tidak dobel kalau di-run ulang.
"""

import json
from database.db_manager import db_manager

RELAY_TYPE_FIELDS = {
    "ocrl": ["pickup_xin", "pickup_ampere", "tms", "curve"],
    "ocrh": ["pickup_xin", "pickup_ampere", "delay", "curve"],
    "gfrl": ["pickup_xin", "pickup_ampere", "tms", "curve"],
    "gfrh": ["pickup_xin", "pickup_ampere", "delay", "curve"],
    "directional": ["pickup_xin", "pickup_ampere", "delay"],
    "thermal": ["pickup_xin", "trip_time_minutes", "alarm_percent", "trip_percent"],
}


def _load_json_objects(path):
    """File sumber = beberapa objek JSON ditempel berurutan, bukan satu JSON valid."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    decoder = json.JSONDecoder()
    objects = []
    idx = 0
    n = len(raw)
    while idx < n:
        while idx < n and raw[idx].isspace():
            idx += 1
        if idx >= n:
            break
        obj, end_idx = decoder.raw_decode(raw, idx)
        objects.append(obj)
        idx = end_idx
    return objects


def _clean(value):
    """String kosong dianggap belum diisi -> None (konsisten dengan 'Belum diisi')."""
    if value == "" or value is None:
        return None
    return value


def _insert_node(cur, node_key, nama, parent_id, node_type, ct_ratio=None,
                  vt_ratio=None, sumber_luar=None, note=None):
    cur.execute(
        """INSERT INTO nodes (node_key, nama, parent_id, node_type, ct_ratio,
                               vt_ratio, sumber_luar, note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (node_key, nama, parent_id, node_type, _clean(ct_ratio),
         _clean(vt_ratio), sumber_luar, note),
    )
    return cur.lastrowid


def _insert_relay_settings(cur, node_id, relay_dict):
    """
    relay_dict contoh: {"ocrl": {...}, "ocrh": {...}, ...}.
    Kalau relay_dict cuma {"enabled": false} tanpa breakdown per jenis,
    tidak ada baris dibuat (artinya semua tampil 'Belum diisi' di UI nanti).
    """
    if not relay_dict:
        return
    if set(relay_dict.keys()) <= {"enabled"}:
        return

    for relay_type, fields in relay_dict.items():
        if relay_type not in RELAY_TYPE_FIELDS:
            continue
        enabled = 1 if fields.get("enabled") else 0
        values = {f: fields.get(f) for f in RELAY_TYPE_FIELDS[relay_type]}
        cur.execute(
            """INSERT INTO relay_settings
               (node_id, relay_type, enabled, pickup_xin, pickup_ampere,
                tms, curve, delay, trip_time_minutes, alarm_percent, trip_percent)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                node_id, relay_type, enabled,
                values.get("pickup_xin"), values.get("pickup_ampere"),
                values.get("tms"), values.get("curve"), values.get("delay"),
                values.get("trip_time_minutes"), values.get("alarm_percent"),
                values.get("trip_percent"),
            ),
        )


def _child_type(entry, standalone_lookup):
    key = entry["id"]
    has_own_outgoing = bool(entry.get("outgoing"))
    links_to_standalone = key.startswith("OUT_") and key[len("OUT_"):] in standalone_lookup
    return "panel" if (has_own_outgoing or links_to_standalone) else "output"


def _process_entry(cur, entry, parent_id, node_type, standalone_lookup, visited):
    node_id = _insert_node(
        cur, node_key=entry["id"], nama=entry["nama"], parent_id=parent_id,
        node_type=node_type, ct_ratio=entry.get("ct_ratio"),
        vt_ratio=entry.get("vt_ratio"), note=entry.get("note"),
    )
    _insert_relay_settings(cur, node_id, entry.get("relay"))

    key = entry["id"]
    if key.startswith("OUT_"):
        target_id = key[len("OUT_"):]
        if target_id in standalone_lookup and target_id not in visited:
            visited.add(target_id)
            _process_standalone(cur, standalone_lookup[target_id], node_id,
                                 standalone_lookup, visited)

    for child in entry.get("outgoing", []):
        _process_entry(cur, child, node_id, _child_type(child, standalone_lookup),
                        standalone_lookup, visited)


def _process_standalone(cur, obj, parent_id, standalone_lookup, visited):
    incoming = obj.get("incoming", {})
    node_id = _insert_node(
        cur, node_key=obj["id"], nama=obj["nama"], parent_id=parent_id,
        node_type="panel", ct_ratio=incoming.get("ct_ratio"),
        vt_ratio=incoming.get("vt_ratio"),
    )
    _insert_relay_settings(cur, node_id, incoming.get("relay"))

    for child in obj.get("outgoing", []):
        _process_entry(cur, child, node_id, _child_type(child, standalone_lookup),
                        standalone_lookup, visited)


def import_all(json_path):
    conn = db_manager.get_connection()
    cur = conn.cursor()

    objects = _load_json_objects(json_path)
    root_obj = objects[0]
    standalone_objs = objects[1:]
    standalone_lookup = {o["id"]: o for o in standalone_objs}
    visited = set()

    cur.execute("DELETE FROM relay_settings")
    cur.execute("DELETE FROM nodes")
    cur.execute("DELETE FROM relay_curve_types")

    for curve_name in root_obj.get("relay_curves", []):
        cur.execute(
            "INSERT OR IGNORE INTO relay_curve_types (curve_name) VALUES (?)",
            (curve_name,),
        )

    for key, value in root_obj.get("settings", {}).items():
        cur.execute(
            "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
            (f"settings.{key}", json.dumps(value)),
        )
    for key, value in root_obj.get("validation_rules", {}).items():
        cur.execute(
            "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
            (f"validation_rules.{key}", json.dumps(value)),
        )

    panels = root_obj["gardu_hubung"][0]["panels"]
    panels_by_id = {p["id"]: p for p in panels}

    mss = panels_by_id["MSS"]
    mss_id = _insert_node(
        cur, node_key=mss["id"], nama=mss["nama"], parent_id=None,
        node_type="root", ct_ratio=mss["incoming"].get("ct_ratio"),
        vt_ratio=mss["incoming"].get("vt_ratio"),
    )
    _insert_relay_settings(cur, mss_id, mss["incoming"].get("relay"))

    for child in mss.get("outgoing", []):
        node_id = _insert_node(
            cur, node_key=child["id"], nama=child["nama"], parent_id=mss_id,
            node_type="panel", ct_ratio=child.get("ct_ratio"),
            vt_ratio=child.get("vt_ratio"), note=child.get("note"),
        )
        _insert_relay_settings(cur, node_id, child.get("relay"))

        target_id = child["id"][len("OUT_"):] if child["id"].startswith("OUT_") else None
        if target_id and target_id in panels_by_id:
            mds1 = panels_by_id[target_id]
            mds1_id = _insert_node(
                cur, node_key=mds1["id"], nama=mds1["nama"], parent_id=node_id,
                node_type="panel", ct_ratio=mds1["incoming"].get("ct_ratio"),
                vt_ratio=mds1["incoming"].get("vt_ratio"),
            )
            _insert_relay_settings(cur, mds1_id, mds1["incoming"].get("relay"))
            for grandchild in mds1.get("outgoing", []):
                _process_entry(cur, grandchild, mds1_id,
                                _child_type(grandchild, standalone_lookup),
                                standalone_lookup, visited)

    if "MDS2" in standalone_lookup:
        mds2 = standalone_lookup["MDS2"]
        visited.add("MDS2")
        mds2_id = _insert_node(
            cur, node_key=mds2["id"], nama=mds2["nama"], parent_id=None,
            node_type="root", ct_ratio=mds2["incoming"].get("ct_ratio"),
            vt_ratio=mds2["incoming"].get("vt_ratio"),
            sumber_luar="POT (PLN) - di luar jaringan United Power",
        )
        _insert_relay_settings(cur, mds2_id, mds2["incoming"].get("relay"))
        for child in mds2.get("outgoing", []):
            _process_entry(cur, child, mds2_id, _child_type(child, standalone_lookup),
                            standalone_lookup, visited)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM nodes")
    total_nodes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM relay_settings")
    total_relays = cur.fetchone()[0]
    return total_nodes, total_relays


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/relay_database.json"
    n_nodes, n_relays = import_all(path)
    print(f"Import selesai: {n_nodes} node, {n_relays} baris relay setting.")
