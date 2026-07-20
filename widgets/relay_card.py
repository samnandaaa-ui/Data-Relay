"""
widgets/relay_card.py
Kartu tampilan satu jenis relay (OCRL/OCRH/GFRL/GFRH/Directional/Thermal).
Dipakai berulang di NodeScreen untuk setiap kartu relay yang ada pada node.
Tappable -- tap kartu manapun membuka form edit.

VERSI KIVYMD (Material Design): dulu pakai BoxLayout+ButtonBehavior polos
dengan canvas.before manual buat gambar rounded rect sendiri. Sekarang
pakai MDCard asli (style "elevated") supaya dapat shadow/elevation
Material asli + ripple effect bawaan saat disentuh -- TIDAK PERLU lagi
gambar canvas manual.

PENTING (KivyMD dari branch master/2.x via buildozer.spec, BUKAN versi
stabil 1.x yang lebih umum di tutorial internet): MDCard sudah otomatis
punya ButtonBehavior bawaan (event on_release asli), jadi cara PAKAI dari
node_screen.py TIDAK BERUBAH SAMA SEKALI -- masih persis:
    RelayCard(label=..., lines_text=..., enabled_flag=..., relay_type=...)
    card_widget.bind(on_release=...)
node_screen.py tidak perlu diedit sama sekali untuk perubahan ini.

Warna latar kartu (enabled/disabled) TETAP ambil dari config/theme.py
COLORS, karena warna itu punya MAKNA (hijau muda = ada data terisi,
abu-abu = "Belum diisi") -- bukan sekadar warna dekoratif Material biasa,
jadi tidak diserahkan ke tema Material otomatis.
"""

from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty

from kivymd.uix.card import MDCard

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<RelayCard>:
    style: "elevated"
    ripple_behavior: True
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(16)
    spacing: dp(6)
    radius: [dp(14)]
    theme_bg_color: "Custom"
    md_bg_color: COLORS["card_enabled"] if self.enabled_flag else COLORS["card_disabled"]

    MDLabel:
        text: root.label
        font_style: "Title"
        role: "medium"
        adaptive_height: True
        halign: "left"
        text_size: self.width, None
        theme_text_color: "Custom"
        text_color: COLORS["text_primary"]

    MDLabel:
        text: root.lines_text
        font_style: "Body"
        role: "large"
        adaptive_height: True
        halign: "left"
        text_size: self.width, None
        theme_text_color: "Custom"
        text_color: COLORS["text_primary"] if root.enabled_flag else COLORS["text_disabled"]
""")


class RelayCard(MDCard):
    label = StringProperty("")
    lines_text = StringProperty("")
    enabled_flag = BooleanProperty(True)
    relay_type = StringProperty("")
