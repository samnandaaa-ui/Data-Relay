"""
main.py
Entry point aplikasi GH Relay - United Power.

Struktur sengaja dipisah: _build_app() membungkus SEMUA import & setup
yang berpotensi gagal (termasuk import KivyMD itu sendiri). Kalau ada
apa pun yang gagal saat start, errornya ditangkap dan ditampilkan
LANGSUNG DI LAYAR sebagai teks (pakai Kivy polos, bukan KivyMD -- supaya
tetap tampil walau KivyMD sendiri yang jadi biang masalah). Ini penting
karena kita tidak punya akses adb/PC untuk lihat crash log Android biasa.
"""

import os
import traceback

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


def _build_app():
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

    asset_json_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "assets", "relay_database.json"
    )

    class GHRelayApp(MDApp):
        def build(self):
            self.title = "GH Relay - United Power"
            self.theme_cls.theme_style = "Dark" if IS_DARK else "Light"
            self.theme_cls.primary_palette = "Blue"
            Window.clearcolor = COLORS["bg"]

            conn = db_manager.get_connection()
            count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            if count == 0 and os.path.exists(asset_json_path):
                import_all(asset_json_path)

            sm = ScreenManager(transition=NoTransition())
            sm.add_widget(HomeScreen(name="home"))
            sm.add_widget(NodeScreen(name="node"))
            sm.add_widget(RelayEditScreen(name="relay_edit"))
            sm.add_widget(AddNodeScreen(name="add_node"))
            sm.current = "home"
            return sm

    return GHRelayApp()


class CrashScreenApp(App):
    """Fallback paling sederhana (Kivy polos) -- cuma dipakai kalau app utama gagal start."""

    def __init__(self, error_text, **kwargs):
        super().__init__(**kwargs)
        self.error_text = error_text

    def build(self):
        label = Label(
            text=self.error_text,
            font_size="13sp",
            size_hint_y=None,
            halign="left",
            valign="top",
            color=(1, 0.4, 0.4, 1),
        )
        label.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        label.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        scroll = ScrollView()
        scroll.add_widget(label)
        return scroll


if __name__ == "__main__":
    try:
        _build_app().run()
    except Exception:
        error_text = "APP GAGAL START:\n\n" + traceback.format_exc()
        try:
            crash_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")
            with open(crash_path, "w") as f:
                f.write(error_text)
        except Exception:
            pass
        CrashScreenApp(error_text).run()
