"""
models/relay_model.py
Query helper untuk tabel `relay_settings`, plus logic format tampilan
("Belum diisi", "Instant", dll) dan CRUD utk form edit.
"""

from database.db_manager import db_manager

RELAY_TYPE_LABELS = {
    "ocrl": "OCRL",
    "ocrh": "OCRH",
    "gfrl": "GFRL",
    "gfrh": "GFRH",
    "directional": "Directional",
    "thermal": "Thermal",
}

RELAY_TYPE_ORDER = ["ocrl", "ocrh", "gfrl", "gfrh", "directional", "thermal"]


def get_relay_cards(node_id):
    """
    Ambil status TAMPIL utk keenam jenis relay pada sebuah node (list of
    dict: type, label, enabled, lines) -- SELALU 6 hasil, termasuk yang
    belum ada barisnya sama sekali di relay_settings (dianggap "Belum
    diisi" juga), supaya kartu itu tetap bisa di-tap utk diisi pertama
    kali (bukan cuma utk edit yang sudah ada).
    """
    conn = db_manager.get_connection()
    rows = conn.execute(
        "SELECT * FROM relay_settings WHERE node_id = ?", (node_id,)
    ).fetchall()
    rows_by_type = {r["relay_type"]: dict(r) for r in rows}

    cards = []
    for relay_type in RELAY_TYPE_ORDER:
        row = rows_by_type.get(relay_type)
        if row is None:
            cards.append({"type": relay_type, "label": RELAY_TYPE_LABELS[relay_type],
                          "enabled": False, "lines": ["Belum diisi"]})
        else:
            cards.append(_format_card(relay_type, row))
    return cards


def get_raw_relay_setting(node_id, relay_type):
    """Ambil baris mentah (utk pre-fill form edit). None kalau belum ada baris."""
    conn = db_manager.get_connection()
    row = conn.execute(
        "SELECT * FROM relay_settings WHERE node_id = ? AND relay_type = ?",
        (node_id, relay_type),
    ).fetchone()
    return dict(row) if row else None


def get_curve_options():
    """Daftar nama kurva yang valid, dari tabel relay_curve_types (bukan hardcode)."""
    conn = db_manager.get_connection()
    rows = conn.execute("SELECT curve_name FROM relay_curve_types ORDER BY curve_name").fetchall()
    return [r["curve_name"] for r in rows]


def upsert_relay_setting(node_id, relay_type, enabled, pickup_xin=None,
                          pickup_ampere=None, tms=None, curve=None, delay=None,
                          trip_time_minutes=None, alarm_percent=None, trip_percent=None):
    """
    Simpan (insert kalau belum ada baris, update kalau sudah ada) satu
    jenis relay utk satu node. Dipakai baik utk mengisi relay yang tadinya
    'Belum diisi' maupun mengedit yang sudah ada.
    """
    conn = db_manager.get_connection()
    conn.execute(
        """INSERT INTO relay_settings
               (node_id, relay_type, enabled, pickup_xin, pickup_ampere,
                tms, curve, delay, trip_time_minutes, alarm_percent, trip_percent)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(node_id, relay_type) DO UPDATE SET
               enabled=excluded.enabled, pickup_xin=excluded.pickup_xin,
               pickup_ampere=excluded.pickup_ampere, tms=excluded.tms,
               curve=excluded.curve, delay=excluded.delay,
               trip_time_minutes=excluded.trip_time_minutes,
               alarm_percent=excluded.alarm_percent, trip_percent=excluded.trip_percent""",
        (node_id, relay_type, 1 if enabled else 0, pickup_xin, pickup_ampere,
         tms, curve, delay, trip_time_minutes, alarm_percent, trip_percent),
    )
    conn.commit()


def _fmt_ampere(value):
    if value is None:
        return None
    if float(value).is_integer():
        return f"{int(value)} A"
    return f"{value} A"


def _fmt_time(value):
    if value is None:
        return None
    if value == 0:
        return "Instant"
    return f"{value} s"


def _format_card(relay_type, row):
    label = RELAY_TYPE_LABELS[relay_type]

    if not row["enabled"]:
        return {"type": relay_type, "label": label, "enabled": False,
                "lines": ["Belum diisi"]}

    lines = []
    ampere_text = _fmt_ampere(row["pickup_ampere"])
    if ampere_text:
        lines.append(ampere_text)

    if relay_type == "thermal":
        if row["pickup_xin"] is not None:
            lines.append(f"{row['pickup_xin']}x In")
        if row["trip_time_minutes"] is not None:
            lines.append(f"Trip {row['trip_time_minutes']} menit")
        if row["alarm_percent"] is not None:
            lines.append(f"Alarm {row['alarm_percent']}%")
        if row["trip_percent"] is not None:
            lines.append(f"Trip {row['trip_percent']}%")
    elif relay_type in ("ocrl", "gfrl"):
        if row["tms"] is not None:
            lines.append(f"TMS {row['tms']} s")
        if row["curve"]:
            lines.append(row["curve"])
    else:
        time_text = _fmt_time(row["delay"])
        if time_text:
            lines.append(time_text)

    if not lines:
        lines = ["Belum diisi"]

    return {"type": relay_type, "label": label, "enabled": True, "lines": lines}
