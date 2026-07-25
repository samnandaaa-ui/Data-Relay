"""
widgets/relay_card.py
Kartu tampilan satu jenis relay (OCRL/OCRH/GFRL/GFRH/Directional/Thermal),
gaya panel industrial: strip warna status di sisi kiri (hijau = terisi &
aktif, abu = belum diisi, mirip indikator status SCADA) + bayangan tipis
di bawah kartu utk kesan elevasi. Pakai BoxLayout+ButtonBehavior murni
(bukan MDCard) -- kombinasi ini sudah terbukti stabil di project ini
sejak awal, MDCard+ButtonBehavior sempat bentrok MRO (lihat riwayat).
Tappable -- tap kartu manapun membuka form edit.
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
    padding: dp(18), dp(14), dp(16), dp(14)
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.35
        RoundedRectangle:
            pos: self.x + dp(2), self.y - dp(3)
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: COLORS["card_pressed"] if self.state == "down" else (COLORS["card_enabled"] if self.enabled_flag else COLORS["card_disabled"])
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: COLORS["status_ok"] if self.enabled_flag else COLORS["status_neutral"]
        Rectangle:
            pos: self.pos
            size: (dp(5), self.height)

    Label:
        text: root.label
        font_size: "20sp"
        bold: True
        color: COLORS["text_primary"]
        size_hint_y: None
        height: self.texture_size[1]
        halign: "left"
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


class RelayCard(ButtonBehavior, BoxLayout):
    label = StringProperty("")
    lines_text = StringProperty("")
    enabled_flag = BooleanProperty(True)
    relay_type = StringProperty("")
