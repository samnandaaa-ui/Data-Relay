"""
main.py
Entry point aplikasi GH Relay - United Power.
Mendaftarkan semua screens ke ScreenManager, set warna latar sesuai tema,
isi database dari assets/relay_database.json kalau ini pertama kali app
dibuka (tabel nodes masih kosong), lalu jalankan App.
"""

import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

from config.theme import COLORS
from database.db_manager import db_manager
from database.importer import import_all
from screens.home_screen import HomeScreen
from screens.node_screen import NodeScreen
from screens.relay_edit_screen import RelayEditScreen
from screens.add_node_screen import AddNodeScreen

ASSET_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "assets", "relay_database.json"
)


class GHRelayApp(App):
    def build(self):
        self.title = "GH Relay - United Power"
        Window.clearcolor = COLORS["bg"]

        self._seed_database_if_empty()

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(NodeScreen(name="node"))
        sm.add_widget(RelayEditScreen(name="relay_edit"))
        sm.add_widget(AddNodeScreen(name="add_node"))
        sm.current = "home"
        return sm

    def _seed_database_if_empty(self):
        """
        Kalau ini pertama kali app dibuka (tabel nodes masih kosong), isi
        otomatis dari assets/relay_database.json yang dibundel ke APK.
        Sesudah itu database jadi milik user sepenuhnya -- import ini
        TIDAK akan jalan lagi selama tabelnya sudah ada isi, walau app
        dibuka ulang berkali-kali. Diuji: editan user tidak pernah
        ketiban re-import di buka kedua.
        """
        conn = db_manager.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        if count == 0 and os.path.exists(ASSET_JSON_PATH):
            import_all(ASSET_JSON_PATH)


if __name__ == "__main__":
    GHRelayApp().run()
