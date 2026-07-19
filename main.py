"""
main.py
Entry point aplikasi GH Relay - United Power.
Sejak fase polish (KivyMD): App diganti dari kivy.app.App ke kivymd.app.MDApp,
supaya bisa pakai komponen Material Design (Snackbar, Dialog, transisi halus,
dll) di seluruh screens/. Deteksi tema gelap/terang Android (config/theme.py)
tetap dipakai, sekarang diarahkan ke theme_cls bawaan KivyMD.
"""

import os
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

from config.theme import IS_DARK, COLORS
from database.db_manager import db_manager
from database.importer import import_all
from screens.home_screen import HomeScreen
from screens.node_screen import NodeScreen
from screens.relay_edit_screen import RelayEditScreen
from screens.add_node_screen import AddNodeScreen

ASSET_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "relay_database.json"
)


class GHRelayApp(MDApp):
    def build(self):
        self.title = "GH Relay - United Power"
        self.theme_cls.theme_style = "Dark" if IS_DARK else "Light"
        self.theme_cls.primary_palette = "Blue"
        Window.clearcolor = COLORS["bg"]  # fallback selama screens/ belum semua dikonversi ke MDScreen

        self._seed_database_if_empty()

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(NodeScreen(name="node"))
        sm.add_widget(RelayEditScreen(name="relay_edit"))
        sm.add_widget(AddNodeScreen(name="add_node"))
        sm.current = "home"
        return sm

    def _seed_database_if_empty(self):
        """Sama seperti sebelumnya, tidak berubah -- lihat riwayat Tahap 12."""
        conn = db_manager.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        if count == 0 and os.path.exists(ASSET_JSON_PATH):
            import_all(ASSET_JSON_PATH)


if __name__ == "__main__":
    GHRelayApp().run()
