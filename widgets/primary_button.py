"""
widgets/primary_button.py
Primary Button Data Relay
"""

from kivy.metrics import dp
from kivy.animation import Animation

from kivymd.uix.button import MDRaisedButton

from config.theme import COLORS


class PrimaryButton(MDRaisedButton):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.md_bg_color = COLORS["accent"]
        self.text_color = (1, 1, 1, 1)

        self.radius = [18, 18, 18, 18]

        self.elevation = 2

        self.size_hint_y = None
        self.height = dp(52)

        self.font_size = "16sp"

    def on_press(self):
        Animation.cancel_all(self)

        Animation(
            opacity=0.85,
            d=0.08
        ).start(self)

        return super().on_press()

    def on_release(self):
        Animation.cancel_all(self)

        Animation(
            opacity=1,
            d=0.08
        ).start(self)

        return super().on_release()
