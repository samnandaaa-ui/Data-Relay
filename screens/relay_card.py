"""
screens/relay_card.py
Widget kartu untuk satu relay setting (OCRL, GFRH, Thermal, dst).
Terima dict siap-tampil dari relay_model.get_relay_cards() -- widget
ini tidak tahu apa-apa soal SQL atau struktur data mentahnya.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class RelayCard(BoxLayout):
    def __init__(self, card, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(12),
            spacing=dp(4),
            **kwargs,
        )
        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(0.92, 0.92, 0.92, 1)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        title = Label(
            text=card["label"],
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(26),
            halign="left",
            valign="middle",
        )
        title.bind(size=title.setter("text_size"))
        self.add_widget(title)

        opacity = 1.0 if card["enabled"] else 0.55
        for line in card["lines"]:
            lbl = Label(
                text=line,
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(20),
                halign="left",
                valign="middle",
                opacity=opacity,
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)

    def _update_bg(self, *_args):
        self._bg.pos = self.pos
        self._bg.size = self.size
