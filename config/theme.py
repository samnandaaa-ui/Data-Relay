"""
config/theme.py
Palet warna light/dark terpusat + deteksi tema Android saat ini.

SEMUA warna di widgets/screens HARUS diambil dari COLORS di sini, bukan
angka RGB ditulis langsung di masing-masing file -- supaya dark mode
konsisten di seluruh app sekaligus, dan gampang diubah di satu tempat.

Catatan desain: tema dideteksi SEKALI saat app pertama dibuka (saat modul
ini di-import), bukan reaktif kalau tema Android berubah sementara app
lagi jalan -- kompromi supaya tidak perlu logic listener konfigurasi
Android yang jauh lebih rumit. Kalau user ganti tema HP di tengah app
berjalan, cukup buka ulang app-nya.
"""

_LIGHT = {
    "bg": (0.97, 0.97, 0.97, 1),
    "text_primary": (0.1, 0.1, 0.1, 1),
    "text_secondary": (0.4, 0.4, 0.4, 1),
    "text_disabled": (0.55, 0.55, 0.55, 1),
    "card_enabled": (0.90, 0.95, 0.90, 1),
    "card_disabled": (0.92, 0.92, 0.92, 1),
    "card_pressed": (0.84, 0.90, 0.99, 1),
    "input_bg": (1, 1, 1, 1),
    "accent": (0.3, 0.5, 0.75, 1),
    "danger": (0.75, 0.15, 0.15, 1),
    "save": (0.2, 0.55, 0.3, 1),
    "info": (0.5, 0.35, 0.1, 1),
}

_DARK = {
    "bg": (0.11, 0.11, 0.12, 1),
    "text_primary": (0.92, 0.92, 0.92, 1),
    "text_secondary": (0.68, 0.68, 0.68, 1),
    "text_disabled": (0.55, 0.55, 0.55, 1),
    "card_enabled": (0.14, 0.24, 0.16, 1),
    "card_disabled": (0.20, 0.20, 0.21, 1),
    "card_pressed": (0.16, 0.23, 0.33, 1),
    "input_bg": (0.18, 0.18, 0.19, 1),
    "accent": (0.40, 0.60, 0.85, 1),
    "danger": (0.85, 0.40, 0.40, 1),
    "save": (0.35, 0.70, 0.45, 1),
    "info": (0.80, 0.60, 0.30, 1),
}


def _detect_android_dark_mode():
    """
    Cek tema gelap/terang Android lewat pyjnius. Return False (terang)
    kalau gagal deteksi apa pun sebabnya (mis. sedang tidak berjalan di
    Android sungguhan, atau API berubah) -- JANGAN sampai app gagal buka
    gara-gara deteksi tema ini, fallback aman selalu didahulukan.
    """
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Configuration = autoclass("android.content.res.Configuration")
        activity = PythonActivity.mActivity
        config = activity.getResources().getConfiguration()
        night_mode_flags = config.uiMode & Configuration.UI_MODE_NIGHT_MASK
        return night_mode_flags == Configuration.UI_MODE_NIGHT_YES
    except Exception:
        return False


IS_DARK = _detect_android_dark_mode()
COLORS = _DARK if IS_DARK else _LIGHT
