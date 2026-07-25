"""
screens/node_screen.py
Layar generik dipakai ulang utk SEMUA level hierarki -- satu screen,
bukan satu screen per level.

Setiap layar menampilkan: kartu incoming milik node itu sendiri, LALU
utk tiap anak: kalau anak itu adalah "Outgoing X" yang jadi pintu ke hub
lain (mis. "Outgoing MDS 1" -> hub "MDS 1"), kartu relay anak itu
ditampilkan LANGSUNG DI SINI (di layar induknya, krn breaker itu secara
fisik ada di induk), diikuti tombol navigasi terpisah ke hub tujuannya.
Kalau anak itu tidak menuju hub lain (leaf, mis. "Trafo"), cukup tombol
biasa spt sebelumnya (kartunya baru tampil setelah di-tap).
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.metrics import dp

from models.node_model import get_node, get_children, get_display_bundle, get_display_path, delete_node
from models.relay_model import get_relay_cards
from widgets.relay_card import RelayCard
from config.theme import COLORS

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<NodeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(8)

            Button:
                text: "< Kembali"
                font_size: "16sp"
                size_hint_x: None
                width: dp(110)
                on_release: root.go_back()

            Label:
                text: root.breadcrumb_text
                font_size: "14sp"
                color: COLORS["text_secondary"]
                halign: "right"
                valign: "middle"
                text_size: self.width, self.height

        Label:
            text: root.title_text
            font_size: "26sp"
            bold: True
            size_hint_y: None
            height: dp(44)
            color: COLORS["text_primary"]
            halign: "left"
            text_size: self.width, None

        ScrollView:
            BoxLayout:
                id: content_list
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)
                padding: [0, dp(8)]
""")


class NodeScreen(Screen):
    breadcrumb_text = StringProperty("")
    title_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_node_id = None

    def load_node(self, node_id):
        self.current_node_id = node_id
        self._render()

    def go_back(self):
        node = get_node(self.current_node_id)
        if node is None or node["parent_id"] is None:
            self.manager.current = "home"
            return
        path = get_display_path(self.current_node_id)
        if len(path) <= 1:
            self.manager.current = "home"
        else:
            self.load_node(path[-2]["id"])

    def _render(self):
        node = get_node(self.current_node_id)
        path = get_display_path(self.current_node_id)

        self.title_text = node["nama"]
        self.breadcrumb_text = (
            " > ".join(p["nama"] for p in path[:-1]) if len(path) > 1 else ""
        )

        container = self.ids.content_list
        container.clear_widgets()

        if node.get("sumber_luar"):
            container.add_widget(self._info_label(f"Sumber: {node['sumber_luar']}"))
        if node.get("note"):
            container.add_widget(self._info_label(node["note"]))

        for card in get_relay_cards(self.current_node_id):
            container.add_widget(self._card_widget(self.current_node_id, node["nama"], card))

        for child in get_children(self.current_node_id):
            bundle = get_display_bundle(child["id"])
            if len(bundle["chain_node_ids"]) > 1:
                container.add_widget(self._section_label(child["nama"]))
                for card in get_relay_cards(child["id"]):
                    container.add_widget(self._card_widget(child["id"], child["nama"], card))
                container.add_widget(self._nav_button(bundle["display_node"]))
            else:
                container.add_widget(self._child_button(child))

        container.add_widget(self._add_button(self.current_node_id))
        container.add_widget(self._delete_button(node["nama"]))

    def _card_widget(self, node_id, node_nama, card):
        card_widget = RelayCard(
            label=card["label"],
            lines_text="\n".join(card["lines"]),
            enabled_flag=card["enabled"],
            relay_type=card["type"],
        )
        card_widget.bind(
            on_release=lambda *_a, n=node_id, rt=card["type"], nm=node_nama:
                self._open_relay_edit(n, rt, nm)
        )
        return card_widget

    def _open_relay_edit(self, node_id, relay_type, node_nama):
        edit_screen = self.manager.get_screen("relay_edit")
        edit_screen.open_for(node_id, relay_type, node_nama)
        self.manager.current = "relay_edit"

    def _open_add_node(self, parent_id):
        add_screen = self.manager.get_screen("add_node")
        add_screen.open_for(parent_id)
        self.manager.current = "add_node"

    def _add_button(self, parent_id):
        btn = Button(
            text="+ Tambah GH di sini", font_size="18sp",
            size_hint_y=None, height=dp(56),
            background_color=COLORS["accent"],
        )
        btn.bind(on_release=lambda *_a: self._open_add_node(parent_id))
        return btn

    def _delete_button(self, nama):
        btn = Button(
            text="Hapus GH ini", font_size="18sp",
            size_hint_y=None, height=dp(56),
            background_color=COLORS["danger"],
        )
        btn.bind(on_release=lambda *_a: self._confirm_delete(nama))
        return btn

    def _confirm_delete(self, nama):
        content = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(16))
        content.add_widget(Label(
            text=f'Hapus "{nama}" beserta semua kartu relay dan\n'
                 f'seluruh turunannya? Tindakan ini tidak bisa dibatalkan.',
            font_size="16sp", color=COLORS["text_primary"], halign="center",
        ))
        btn_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        cancel_btn = Button(text="Batal", font_size="17sp")
        confirm_btn = Button(text="Ya, Hapus", font_size="17sp",
                              background_color=COLORS["danger"])
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Konfirmasi Hapus", content=content, size_hint=(0.85, 0.4))
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda *_a: self._do_delete(popup))
        popup.open()

    def _do_delete(self, popup):
        popup.dismiss()
        path = get_display_path(self.current_node_id)
        back_id = path[-2]["id"] if len(path) > 1 else None
        delete_node(self.current_node_id)
        if back_id is None:
            self.manager.current = "home"
        else:
            self.load_node(back_id)

    def _info_label(self, text):
        lbl = Label(
            text=text, font_size="15sp", italic=True,
            color=COLORS["info"], size_hint_y=None, height=dp(30), halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _section_label(self, text):
        lbl = Label(
            text=text, font_size="14sp", bold=True,
            color=COLORS["text_secondary"], size_hint_y=None, height=dp(26), halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _child_button(self, child):
        btn = Button(
            text=child["nama"], font_size="20sp",
            size_hint_y=None, height=dp(64),
        )
        btn.bind(on_release=lambda *_a, c=child: self.load_node(c["id"]))
        return btn

    def _nav_button(self, hub_node):
        btn = Button(
            text=f"\u2192 Masuk {hub_node['nama']}",
            font_size="18sp", size_hint_y=None, height=dp(56),
            background_color=COLORS["accent"],
        )
        btn.bind(on_release=lambda *_a, h=hub_node: self.load_node(h["id"]))
        return btn
