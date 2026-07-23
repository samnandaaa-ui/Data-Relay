"""
database/importer.py
Import data relay dari relay_database.json (assets/) ke SQLite.

STRUKTUR HIERARKI (revisi lapangan Juli 2026):
Setiap "hub" (MSS, MDS 1, TDS 1, TDS 2, MDS 2, TDS 3, MDS 3) TIDAK PERNAH
menampilkan kartu relay-nya sendiri secara langsung -- kalau ada data
relay utk hub itu, otomatis dijadikan anak tersendiri bernama
"Incoming <nama hub>". Anak-anak outgoing diganti namanya jadi format
"Outgoing <Nama>" (atau "Trafo" khusus transformator, tanpa awalan) dan
TETAP menampilkan kartu relay-nya sendiri (tidak digabung/collapse
dengan node lain).
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

OUTGOING_DISPLAY_NAMES = {
    "POLTEK": "Outgoing Poltek",
    "BORINE": "Outgoing Borine",
    "RUDJI": "Outgoing Rudji",
    "SASAKURA": "Outgoing Sasakura",
    "MBG": "Outgoing MBG",
    "ECLAT": "Outgoing Eclat",
    "GMS": "Outgoing GMS",
    "GTI": "Outgoing GTI",
    "ALBA": "Outgoing Alba",
    "ZHONGBU": "Outgoing Zhongbu",
    "VOK": "Outgoing VOK",
    "TDS 1": "Outgoing TDS 1",
    "TDS 2": "Outgoing TDS 2",
    "TDS 3": "Outgoing TDS 3",
    "MDS 1": "Outgoing MDS 1",
}


def _load_json_objects(path):
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
    if value == "" or value is None:
        return None
    return value


def _display_name(raw_nama):
    if raw_nama.strip().upper() == "TRAFO":
        return "Trafo"
    return OUTGOING_DISPLAY_NAMES.get(raw_nama, f"Outgoing {raw_nama.title()}")


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


def _insert_hub(cur, node_key, nama, parent_id, is_root, ct_ratio, vt_ratio,
                 relay_dict, sumber_luar=None):
    hub_id = _insert_node(
        cur, node_key=node_key, nama=nama, parent_id=parent_id,
        node_type="root" if is_root else "panel",
        ct_ratio=ct_ratio, vt_ratio=vt_ratio, sumber_luar=sumber_luar,
    )
    incoming_id = _insert_node(
        cur, node_key=f"IN_{node_key}", nama=f"Incoming {nama}",
        parent_id=hub_id, node_type="output",
    )
    _insert_relay_settings(cur, incoming_id, relay_dict)
    return hub_id


def _process_outgoing_entry(cur, entry, parent_hub_id, standalone_lookup, visited):
    node_id = _insert_node(
        cur, node_key=entry["id"], nama=_display_name(entry["nama"]),
        parent_id=parent_hub_id, node_type="panel",
        ct_ratio=entry.get("ct_ratio"), vt_ratio=entry.get("vt_ratio"),
        note=entry.get("note"),
    )
    _insert_relay_settings(cur, node_id, entry.get("relay"))

    key = entry["id"]
    if key.startswith("OUT_"):
        target_id = key[len("OUT_"):]
        if target_id in standalone_lookup and target_id not in visited:
            visited.add(target_id)
            obj = standalone_lookup[target_id]
            incoming = obj.get("incoming", {})
            hub_id = _insert_hub(
                cur, node_key=obj["id"], nama=obj["nama"], parent_id=node_id,
                is_root=False, ct_ratio=incoming.get("ct_ratio"),
                vt_ratio=incoming.get("vt_ratio"), relay_dict=incoming.get("relay"),
            )
            for child in obj.get("outgoing", []):
                _process_outgoing_entry(cur, child, hub_id, standalone_lookup, visited)


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
    mss_hub_id = _insert_hub(
        cur, node_key=mss["id"], nama=mss["nama"], parent_id=None, is_root=True,
        ct_ratio=mss["incoming"].get("ct_ratio"), vt_ratio=mss["incoming"].get("vt_ratio"),
        relay_dict=mss["incoming"].get("relay"),
    )

    for child in mss.get("outgoing", []):
        node_id = _insert_node(
            cur, node_key=child["id"], nama=_display_name(child["nama"]),
            parent_id=mss_hub_id, node_type="panel",
            ct_ratio=child.get("ct_ratio"), vt_ratio=child.get("vt_ratio"),
            note=child.get("note"),
        )
        _insert_relay_settings(cur, node_id, child.get("relay"))

        target_id = child["id"][len("OUT_"):] if child["id"].startswith("OUT_") else None
        if target_id and target_id in panels_by_id:
            mds1 = panels_by_id[target_id]
            mds1_hub_id = _insert_hub(
                cur, node_key=mds1["id"], nama=mds1["nama"], parent_id=node_id,
                is_root=False, ct_ratio=mds1["incoming"].get("ct_ratio"),
                vt_ratio=mds1["incoming"].get("vt_ratio"),
                relay_dict=mds1["incoming"].get("relay"),
            )
            for grandchild in mds1.get("outgoing", []):
                _process_outgoing_entry(cur, grandchild, mds1_hub_id, standalone_lookup, visited)

    for obj_id, obj in standalone_lookup.items():
        if obj_id in visited:
            continue
        visited.add(obj_id)
        incoming = obj.get("incoming", {})
        sumber_luar = (
            "POT (PLN) - di luar jaringan United Power" if obj_id == "MDS2" else None
        )
        hub_id = _insert_hub(
            cur, node_key=obj["id"], nama=obj["nama"], parent_id=None, is_root=True,
            ct_ratio=incoming.get("ct_ratio"), vt_ratio=incoming.get("vt_ratio"),
            relay_dict=incoming.get("relay"), sumber_luar=sumber_luar,
        )
        for child in obj.get("outgoing", []):
            _process_outgoing_entry(cur, child, hub_id, standalone_lookup, visited)

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
