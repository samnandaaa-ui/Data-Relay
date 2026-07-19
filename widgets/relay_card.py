"""
widgets/relay_card.py
Kartu tampilan satu jenis relay (OCRL/OCRH/GFRL/GFRH/Directional/Thermal).
Dipakai berulang di NodeScreen untuk setiap kartu relay yang ada pada node.
Tappable (ButtonBehavior) -- tap kartu manapun membuka form edit.
Warna diambil dari config/theme.py (ikut dark mode Android otomatis).
"""

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, BooleanProperty

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<RelayCard>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(16)
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: COLORS["card_pressed"] if self.state == "down" else (COLORS["card_enabled"] if self.enabled_flag else COLORS["card_disabled"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

    Label:
        text: root.label
        font_size: "22sp"
        bold: True
        color: COLORS["text_primary"]
        size_hint_y: None
        height: self.texture_size[1]
        halign: "left"
        text_size: self.width, None

    Label:
        text: root.lines_text
        font_size: "18sp"
        color: COLORS["text_primary"] if root.enabled_flag else COLORS["text_disabled"]
        size_hint_y: None
        height: self.texture_size[1]
        halign: "left"
        valign: "top"
        text_size: self.width, None
""")


class RelayCard(ButtonBehavior, BoxLayout):
    label = StringProperty("")
    lines_text = StringProperty("")
    enabled_flag = BooleanProperty(True)
    relay_type = StringProperty("")
