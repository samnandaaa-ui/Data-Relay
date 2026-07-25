"""
config/theme.py
Palet warna bergaya panel industrial (SCADA/ABB/Schneider-like): dasar
gelap netral, aksen biru teknikal, indikator status hijau/abu/merah yang
tegas -- bukan warna pastel. Deteksi tema Android tetap dipakai; light
mode juga dibuat lebih "teknikal" (abu dingin, bukan putih polos).

SEMUA warna di widgets/screens HARUS diambil dari COLORS di sini.
"""

_LIGHT = {
    "bg": (0.93, 0.94, 0.95, 1),
    "surface": (1, 1, 1, 1),
    "text_primary": (0.08, 0.10, 0.12, 1),
    "text_secondary": (0.38, 0.42, 0.46, 1),
    "text_disabled": (0.60, 0.63, 0.66, 1),
    "card_enabled": (1, 1, 1, 1),
    "card_disabled": (0.88, 0.89, 0.91, 1),
    "card_pressed": (0.85, 0.91, 0.98, 1),
    "input_bg": (1, 1, 1, 1),
    "accent": (0.10, 0.42, 0.68, 1),
    "danger": (0.75, 0.15, 0.15, 1),
    "save": (0.15, 0.50, 0.30, 1),
    "info": (0.55, 0.40, 0.05, 1),
    "status_ok": (0.15, 0.55, 0.30, 1),
    "status_neutral": (0.65, 0.67, 0.70, 1),
}

_DARK = {
    "bg": (0.06, 0.08, 0.10, 1),
    "surface": (0.11, 0.13, 0.16, 1),
    "text_primary": (0.90, 0.93, 0.95, 1),
    "text_secondary": (0.58, 0.63, 0.68, 1),
    "text_disabled": (0.45, 0.48, 0.52, 1),
    "card_enabled": (0.11, 0.14, 0.17, 1),
    "card_disabled": (0.13, 0.15, 0.17, 1),
    "card_pressed": (0.14, 0.22, 0.32, 1),
    "input_bg": (0.14, 0.16, 0.19, 1),
    "accent": (0.25, 0.60, 0.88, 1),
    "danger": (0.88, 0.35, 0.35, 1),
    "save": (0.30, 0.68, 0.42, 1),
    "info": (0.82, 0.62, 0.25, 1),
    "status_ok": (0.30, 0.75, 0.45, 1),
    "status_neutral": (0.38, 0.42, 0.47, 1),
}


def _detect_android_dark_mode():
    """Cek tema gelap/terang Android lewat pyjnius. False (terang) kalau
    gagal deteksi -- jangan sampai app crash gara-gara deteksi tema ini."""
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
