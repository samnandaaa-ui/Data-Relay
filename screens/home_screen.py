"""
screens/home_screen.py
Layar utama: kotak pencarian + daftar node akar (MSS, MDS 2, dst).
Mengetik di kotak cari langsung memfilter/mengganti daftar jadi hasil
pencarian (lewat search_model), tanpa perlu tombol "cari".
Warna diambil dari config/theme.py (ikut dark mode Android otomatis).
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp

from models.node_model import get_roots
from models.search_model import search_nodes
from config.theme import COLORS

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<HomeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(12)

        Label:
            text: "United Power"
            font_size: "28sp"
            bold: True
            size_hint_y: None
            height: dp(48)
            color: COLORS["text_primary"]

        Label:
            text: "Setting Relay Proteksi Gardu Hubung"
            font_size: "15sp"
            size_hint_y: None
            height: dp(24)
            color: COLORS["text_secondary"]

        TextInput:
            id: search_input
            hint_text: "Cari nama GH..."
            font_size: "16sp"
            size_hint_y: None
            height: dp(56)
            multiline: False
            padding: [dp(12), dp(16), dp(12), dp(16)]
            background_color: COLORS["input_bg"]
            foreground_color: COLORS["text_primary"]
            hint_text_color: COLORS["text_secondary"]
            on_text: root.on_search_text(self.text)

        Button:
            text: "+ Tambah GH baru (akar)"
            font_size: "16sp"
            size_hint_y: None
            height: dp(48)
            background_color: COLORS["accent"]
            on_release: root.open_add_root()

        ScrollView:
            BoxLayout:
                id: result_list
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)
                padding: [0, dp(8)]
""")


class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        self.ids.search_input.text = ""
        self._show_roots()

    def on_search_text(self, text):
        text = text.strip()
        if not text:
            self._show_roots()
        else:
            self._show_search_results(text)

    def _show_roots(self):
        container = self.ids.result_list
        container.clear_widgets()
        for node in get_roots():
            container.add_widget(self._build_root_button(node))

    def _show_search_results(self, query):
        container = self.ids.result_list
        container.clear_widgets()
        results = search_nodes(query)
        if not results:
            container.add_widget(self._empty_label(f'Tidak ditemukan: "{query}"'))
            return
        for r in results:
            container.add_widget(self._build_result_button(r))

    def _build_root_button(self, node):
        label_text = node["nama"]
        if node.get("sumber_luar"):
            label_text += f"\n({node['sumber_luar']})"
        btn = Button(
            text=label_text,
            font_size="22sp",
            size_hint_y=None,
            height=dp(80) if node.get("sumber_luar") else dp(64),
            halign="center",
        )
        btn.bind(on_release=lambda *_a, n=node: self._open_node(n["id"]))
        return btn

    def _build_result_button(self, result):
        label_text = result["nama"]
        if result["breadcrumb"]:
            label_text += f"\n{result['breadcrumb']}"
        btn = Button(
            text=label_text,
            font_size="18sp",
            size_hint_y=None,
            height=dp(64),
            halign="center",
        )
        btn.bind(on_release=lambda *_a, nid=result["node_id"]: self._open_node(nid))
        return btn

    def _empty_label(self, text):
        return Label(
            text=text,
            font_size="16sp",
            color=COLORS["text_secondary"],
            size_hint_y=None,
            height=dp(60),
        )

    def _open_node(self, node_id):
        node_screen = self.manager.get_screen("node")
        node_screen.load_node(node_id)
        self.manager.current = "node"

    def open_add_root(self):
        add_screen = self.manager.get_screen("add_node")
        add_screen.open_for(None)
        self.manager.current = "add_node"
