"""
widgets/search_bar.py
"""

from kivy.metrics import dp

from kivymd.uix.textfield import MDTextField

from config.theme import COLORS


class SearchBar(MDTextField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.hint_text = "Cari Gardu Hubung..."

        self.mode = "rectangle"

        self.size_hint_y = None
        self.height = dp(56)

        self.line_color_normal = COLORS["accent"]
        self.line_color_focus = COLORS["accent"]

        self.text_color_normal = COLORS["text_primary"]
        self.text_color_focus = COLORS["text_primary"]

        self.fill_color_normal = COLORS["input_bg"]
        self.fill_color_focus = COLORS["input_bg"]

        self.radius = [18, 18, 18, 18]
