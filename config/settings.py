"""
config/settings.py
Konstanta konfigurasi aplikasi: path file, versi, dan pengaturan umum.
Dipisah dari business logic supaya gampang diubah tanpa menyentuh kode lain.
"""


import os

APP_NAME = "GH Relay - United Power"
APP_VERSION = "0.1.0"

DB_FILENAME = "gh_relay.db"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_path():
    """
    Path lengkap file database.
    - Kalau app Kivy sedang berjalan (ada instance App aktif), pakai folder
      privat aplikasi (app.user_data_dir) -- ini yang benar di Android.
    - Kalau belum ada App aktif (misal testing database.py langsung dari
      terminal), simpan di folder root project ini saja.
    """
    try:
        from kivy.app import App
        app = App.get_running_app()
        if app is not None:
            return os.path.join(app.user_data_dir, DB_FILENAME)
    except Exception:
        pass
    return os.path.join(PROJECT_ROOT, DB_FILENAME)
