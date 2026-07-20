"""
screens/home_screen.py
Layar utama: kotak pencarian + daftar node akar (MSS, MDS 2, dst).
Mengetik di kotak cari langsung memfilter/mengganti daftar jadi hasil
pencarian (lewat search_model), tanpa perlu tombol "cari".
Warna diambil dari config/theme.py (ikut dark mode Android otomatis).

VERSI KIVYMD (Material Design): kotak cari & tombol "+ Tambah GH" sekarang
pakai komponen Material asli (MDTextField, MDButton) -- otomatis dapat
gaya filled + ripple Material. Daftar GH (akar & hasil cari) sekarang
pakai MDCard bertumpuk (bukan Button polos) supaya kelihatan seperti
kartu dengan shadow, bukan tombol datar.

Konstruksi widget PER-ITEM (kartu tiap GH) tetap dengan cara lama --
Python imperatif langsung (bukan template <rule> KV terpisah) -- pola
yang sama persis dipakai di node_screen.py, supaya gaya kodenya
konsisten di seluruh project.

CATATAN KEPERCAYAAN DIRI (baca ini sebelum coba di device):
KivyMD yang dipakai project ini ditarik dari branch MASTER (lihat
buildozer.spec: .../KivyMD/archive/master.zip), yaitu versi 2.x yang
API-nya beda cukup jauh dari versi 1.x lama yang lebih umum di
tutorial internet. Kode di file ini sudah dicocokkan ke dokumentasi
resmi KivyMD "latest" (https://kivymd.readthedocs.io/en/latest/) per
20 Juli 2026 untuk MDCard, MDButton, MDTextField, dan MDLabel -- TAPI
belum bisa dites jalan sungguhan (kivy/kivymd tidak ada di sandbox
Claude, dan Termux:X11 ditolak user sesuai PROJECT_STATUS.md) . Jadi
levelnya: [DICOCOKKAN KE DOKUMENTASI, BELUM DIUJI JALAN].

Satu titik paling tidak pasti: tinggi (height) MDTextField di-set manual
dp(56) di bawah, karena BoxLayout vertical di sini butuh tinggi pasti
biar ScrollView di bawahnya dapat sisa ruang -- tapi contoh resmi
KivyMD untuk MDTextField tidak pernah set height manual (mereka selalu
pakai pos_hint di layar kosong). Kalau nanti APK jalan dan kotak
carinya kepotong/kegedean, itu tempat pertama yang perlu diubah.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

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

        MDLabel:
            text: "United Power"
            font_style: "Headline"
            role: "medium"
            size_hint_y: None
            height: dp(44)
            theme_text_color: "Custom"
            text_color: COLORS["text_primary"]

        MDLabel:
            text: "Setting Relay Proteksi Gardu Hubung"
            font_style: "Body"
            role: "medium"
            size_hint_y: None
            height: dp(24)
            theme_text_color: "Custom"
            text_color: COLORS["text_secondary"]

        MDTextField:
            id: search_input
            mode: "filled"
            size_hint_y: None
            height: dp(56)
            on_text: root.on_search_text(self.text)

            MDTextFieldLeadingIcon:
                icon: "magnify"

            MDTextFieldHintText:
                text: "Cari nama GH / kubikel... (contoh: Borine)"

        MDButton:
            style: "filled"
            size_hint_y: None
            height: dp(48)
            theme_bg_color: "Custom"
            md_bg_color: COLORS["accent"]
            on_release: root.open_add_root()

            MDButtonIcon:
                icon: "plus"

            MDButtonText:
                text: "Tambah GH baru (akar)"

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
            container.add_widget(self._build_root_card(node))

    def _show_search_results(self, query):
        container = self.ids.result_list
        container.clear_widgets()
        results = search_nodes(query)
        if not results:
            container.add_widget(self._empty_label(f'Tidak ditemukan: "{query}"'))
            return
        for r in results:
            container.add_widget(self._build_result_card(r))

    def _build_node_card(self, title_text, subtitle_text, on_tap):
        """
        Satu kartu di daftar (dipakai utk node akar maupun hasil cari).
        Baris subtitle CUMA ditambahkan kalau ada isinya -- supaya kartu
        tanpa subtitle tidak menyisakan celah kosong di bawah judul.
        """
        card = MDCard(
            orientation="vertical",
            style="elevated",
            ripple_behavior=True,
            padding=dp(16),
            spacing=dp(4),
            radius=[dp(14)],
            size_hint_y=None,
            theme_bg_color="Custom",
            md_bg_color=COLORS["input_bg"],
        )
        card.bind(minimum_height=card.setter("height"))

        title = MDLabel(
            text=title_text,
            font_style="Title",
            role="large",
            adaptive_height=True,
            halign="left",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        )
        title.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        card.add_widget(title)

        if subtitle_text:
            subtitle = MDLabel(
                text=subtitle_text,
                font_style="Body",
                role="medium",
                adaptive_height=True,
                halign="left",
                theme_text_color="Custom",
                text_color=COLORS["text_secondary"],
            )
            subtitle.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
            card.add_widget(subtitle)

        card.bind(on_release=on_tap)
        return card

    def _build_root_card(self, node):
        subtitle = f"({node['sumber_luar']})" if node.get("sumber_luar") else ""
        return self._build_node_card(
            node["nama"], subtitle,
            lambda *_a, n=node: self._open_node(n["id"]),
        )

    def _build_result_card(self, result):
        return self._build_node_card(
            result["nama"], result["breadcrumb"],
            lambda *_a, nid=result["node_id"]: self._open_node(nid),
        )

    def _empty_label(self, text):
        lbl = MDLabel(
            text=text,
            font_style="Body",
            role="large",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
            size_hint_y=None,
            height=dp(60),
            halign="center",
        )
        lbl.bind(width=lambda inst, val: setattr(inst, "text_size", (val, None)))
        return lbl

    def _open_node(self, node_id):
        node_screen = self.manager.get_screen("node")
        node_screen.load_node(node_id)
        self.manager.current = "node"

    def open_add_root(self):
        add_screen = self.manager.get_screen("add_node")
        add_screen.open_for(None)
        self.manager.current = "add_node"
