"""
screens/node_screen.py
Layar generik dipakai ulang utk SEMUA level hierarki (MDS 1, TDS 1,
output, dst) -- satu screen, bukan satu screen per level.

Sejak Tahap 9B: memakai get_display_bundle() dari node_model, sehingga
pasangan "OUT_X -> X" yang ber-nama sama (mis. OUT_TDS1 -> TDS1, sama-sama
"TDS 1") tampil sebagai SATU layar dengan 2 kelompok kartu relay berlabel
beda ("Relay outgoing dari ..." / "Relay incoming ..."), bukan 2 layar
tap terpisah seperti versi 9A.
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.metrics import dp

from models.node_model import get_node, get_display_bundle, get_display_path, delete_node
from models.relay_model import get_relay_cards
from widgets.relay_card import RelayCard

Builder.load_string(r"""
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
                color: (0.4, 0.4, 0.4, 1)
                halign: "right"
                valign: "middle"
                text_size: self.width, self.height

        Label:
            text: root.title_text
            font_size: "26sp"
            bold: True
            size_hint_y: None
            height: dp(44)
            color: (0.1, 0.1, 0.1, 1)
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
        else:
            self.load_node(node["parent_id"])

    def _render(self):
        bundle = get_display_bundle(self.current_node_id)
        display_node = bundle["display_node"]
        path = get_display_path(display_node["id"])

        self.title_text = display_node["nama"]
        self.breadcrumb_text = (
            " > ".join(p["nama"] for p in path[:-1]) if len(path) > 1 else ""
        )

        container = self.ids.content_list
        container.clear_widgets()

        if display_node.get("sumber_luar"):
            container.add_widget(
                self._info_label(f"Sumber: {display_node['sumber_luar']}")
            )

        chain = bundle["chain_node_ids"]
        for idx, nid in enumerate(chain):
            node = get_node(nid)
            if node.get("note"):
                container.add_widget(self._info_label(node["note"]))

            cards = get_relay_cards(nid)

            if len(chain) > 1:
                if idx < len(chain) - 1:
                    parent = get_node(node["parent_id"])
                    heading = f"Relay outgoing dari {parent['nama']}"
                else:
                    heading = f"Relay incoming {node['nama']}"
                container.add_widget(self._section_label(heading))

            for card in cards:
                card_widget = RelayCard(
                    label=card["label"],
                    lines_text="\n".join(card["lines"]),
                    enabled_flag=card["enabled"],
                    relay_type=card["type"],
                )
                card_widget.bind(
                    on_release=lambda *_a, n=nid, rt=card["type"], nm=node["nama"]:
                        self._open_relay_edit(n, rt, nm)
                )
                container.add_widget(card_widget)

        for child in bundle["children"]:
            container.add_widget(self._child_button(child))

        container.add_widget(self._add_button(display_node["id"]))
        container.add_widget(self._delete_button(display_node["nama"]))

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
            text="+ Tambah GH di sini",
            font_size="18sp",
            size_hint_y=None,
            height=dp(56),
            background_color=(0.3, 0.5, 0.75, 1),
        )
        btn.bind(on_release=lambda *_a: self._open_add_node(parent_id))
        return btn

    def _delete_button(self, nama):
        btn = Button(
            text="Hapus GH ini",
            font_size="18sp",
            size_hint_y=None,
            height=dp(56),
            background_color=(0.75, 0.15, 0.15, 1),
        )
        btn.bind(on_release=lambda *_a: self._confirm_delete(nama))
        return btn

    def _confirm_delete(self, nama):
        content = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(16))
        content.add_widget(Label(
            text=f'Hapus "{nama}" beserta semua kartu relay dan\n'
                 f'seluruh turunannya? Tindakan ini tidak bisa dibatalkan.',
            font_size="16sp",
            halign="center",
        ))
        btn_row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(10))
        cancel_btn = Button(text="Batal", font_size="17sp")
        confirm_btn = Button(text="Ya, Hapus", font_size="17sp",
                              background_color=(0.75, 0.15, 0.15, 1))
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Konfirmasi Hapus", content=content, size_hint=(0.85, 0.4))
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda *_a: self._do_delete(popup))
        popup.open()

    def _do_delete(self, popup):
        popup.dismiss()
        node = get_node(self.current_node_id)
        parent_id = node["parent_id"]
        delete_node(self.current_node_id)
        if parent_id is None:
            self.manager.current = "home"
        else:
            self.load_node(parent_id)

    def _info_label(self, text):
        lbl = Label(
            text=text, font_size="15sp", italic=True,
            color=(0.5, 0.35, 0.1, 1), size_hint_y=None, height=dp(30),
            halign="left",
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _section_label(self, text):
        lbl = Label(
            text=text, font_size="14sp", bold=True,
            color=(0.35, 0.35, 0.35, 1), size_hint_y=None, height=dp(26),
            halign="left",
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
