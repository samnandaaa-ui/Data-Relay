"""
widgets/relay_card.py
Kartu tampilan satu jenis relay (OCRL/OCRH/GFRL/GFRH/Directional/Thermal),
gaya panel industrial: elevasi/bayangan jelas (MDCard) + indikator status
bulat (hijau = terisi & aktif, abu = belum diisi), mirip status indicator
di software SCADA. Tappable (ButtonBehavior) -- tap kartu manapun
membuka form edit. Warna dari config/theme.py (ikut dark mode Android).
"""

from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<RelayCard>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(16), dp(14), dp(16), dp(14)
    spacing: dp(6)
    radius: dp(6)
    theme_bg_color: "Custom"
    md_bg_color: COLORS["card_pressed"] if self.state == "down" else (COLORS["card_enabled"] if self.enabled_flag else COLORS["card_disabled"])
    theme_shadow_color: "Custom"
    shadow_color: 0, 0, 0, 0.45
    theme_shadow_offset: "Custom"
    shadow_offset: (0, -2)
    theme_shadow_softness: "Custom"
    shadow_softness: 6
    theme_elevation_level: "Custom"
    elevation_level: 1

    BoxLayout:
        size_hint_y: None
        height: max(dp(22), title_lbl.texture_size[1])
        spacing: dp(10)

        Widget:
            size_hint: None, None
            size: dp(10), dp(10)
            pos_hint: {"center_y": 0.5}
            canvas.before:
                Color:
                    rgba: COLORS["status_ok"] if root.enabled_flag else COLORS["status_neutral"]
                Ellipse:
                    pos: self.pos
                    size: self.size

        Label:
            id: title_lbl
            text: root.label
            font_size: "20sp"
            bold: True
            color: COLORS["text_primary"]
            size_hint_y: None
            height: self.texture_size[1]
            halign: "left"
            valign: "middle"
            text_size: self.width, None

    Label:
        text: root.lines_text
        font_size: "17sp"
        color: COLORS["text_primary"] if root.enabled_flag else COLORS["text_disabled"]
        size_hint_y: None
        height: self.texture_size[1]
        halign: "left"
        valign: "top"
        text_size: self.width, None
""")


class RelayCard(ButtonBehavior, MDCard):
    label = StringProperty("")
    lines_text = StringProperty("")
    enabled_flag = BooleanProperty(True)
    relay_type = StringProperty("")
