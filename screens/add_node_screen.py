"""
screens/add_node_screen.py
Form "Tambah GH": tambah node baru sebagai anak dari node yang sedang
dibuka di NodeScreen, atau sebagai akar baru kalau dibuka dari Home.
Warna diambil dari config/theme.py (ikut dark mode Android otomatis).
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.metrics import dp

from models.node_model import create_node, get_node
from config.theme import COLORS

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<AddNodeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            Button:
                text: "< Batal"
                font_size: "16sp"
                size_hint_x: None
                width: dp(100)
                on_release: root.cancel()

        Label:
            text: root.header_text
            font_size: "22sp"
            bold: True
            size_hint_y: None
            height: dp(48)
            color: COLORS["text_primary"]
            halign: "left"
            valign: "top"
            text_size: self.width, None

        Label:
            text: "Nama GH / Kubikel"
            font_size: "16sp"
            size_hint_y: None
            height: dp(24)
            color: COLORS["text_primary"]
            halign: "left"
            text_size: self.width, None
        TextInput:
            id: nama_input
            font_size: "18sp"
            multiline: False
            size_hint_y: None
            height: dp(52)
            background_color: COLORS["input_bg"]
            foreground_color: COLORS["text_primary"]

        Label:
            text: "Rasio CT (contoh: 600/5) -- boleh kosong"
            font_size: "16sp"
            size_hint_y: None
            height: dp(24)
            color: COLORS["text_primary"]
            halign: "left"
            text_size: self.width, None
        TextInput:
            id: ct_input
            font_size: "18sp"
            multiline: False
            size_hint_y: None
            height: dp(52)
            background_color: COLORS["input_bg"]
            foreground_color: COLORS["text_primary"]

        Label:
            text: "Rasio VT (contoh: 110) -- boleh kosong"
            font_size: "16sp"
            size_hint_y: None
            height: dp(24)
            color: COLORS["text_primary"]
            halign: "left"
            text_size: self.width, None
        TextInput:
            id: vt_input
            font_size: "18sp"
            multiline: False
            size_hint_y: None
            height: dp(52)
            background_color: COLORS["input_bg"]
            foreground_color: COLORS["text_primary"]

        Label:
            id: error_label
            text: ""
            font_size: "15sp"
            color: COLORS["danger"]
            size_hint_y: None
            height: dp(24)
            halign: "left"
            text_size: self.width, None

        Widget:

        Button:
            text: "Tambah"
            font_size: "20sp"
            bold: True
            size_hint_y: None
            height: dp(64)
            background_color: COLORS["save"]
            on_release: root.save()
""")


class AddNodeScreen(Screen):
    header_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_node_id = None

    def open_for(self, parent_id):
        self.parent_node_id = parent_id
        if parent_id is None:
            self.header_text = "Tambah GH baru (akar)"
        else:
            parent = get_node(parent_id)
            self.header_text = f"Tambah di bawah {parent['nama']}"
        self.ids.nama_input.text = ""
        self.ids.ct_input.text = ""
        self.ids.vt_input.text = ""
        self.ids.error_label.text = ""

    def save(self):
        nama = self.ids.nama_input.text.strip()
        if not nama:
            self.ids.error_label.text = "Nama tidak boleh kosong."
            return

        ct_ratio = self.ids.ct_input.text.strip() or None
        vt_ratio = self.ids.vt_input.text.strip() or None
        node_type = "root" if self.parent_node_id is None else "output"

        new_id = create_node(
            nama=nama, parent_id=self.parent_node_id,
            ct_ratio=ct_ratio, vt_ratio=vt_ratio, node_type=node_type,
        )

        node_screen = self.manager.get_screen("node")
        node_screen.load_node(new_id)
        self.manager.current = "node"

    def cancel(self):
        self.manager.current = "node" if self.parent_node_id is not None else "home"
