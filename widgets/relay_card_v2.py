"""
Relay Card V2
"""

from kivy.metrics import dp
from kivy.animation import Animation

from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from config.theme import COLORS


class RelayCardV2(MDCard):

    def __init__(
        self,
        relay_name="OCRL",
        relay_value="600 A",
        relay_status="Enabled",
        **kwargs
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.padding = dp(16)

        self.spacing = dp(10)

        self.radius = [18]

        self.elevation = 2

        self.size_hint_y = None

        self.adaptive_height = True

        self.md_bg_color = COLORS["card_enabled"]

        self.bind(on_touch_down=self._press)

        title = MDLabel(
            text=relay_name,
            bold=True,
            font_style="H6",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"]
        )

        value = MDLabel(
            text=relay_value,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"]
        )

        status_color = (
            COLORS["save"]
            if relay_status == "Enabled"
            else COLORS["danger"]
        )

        status = MDLabel(
            text=relay_status,
            bold=True,
            theme_text_color="Custom",
            text_color=status_color
        )

        self.add_widget(title)
        self.add_widget(value)
        self.add_widget(status)

    def _press(self, instance, touch):

        if not self.collide_point(*touch.pos):
            return

        Animation.cancel_all(self)

        (
            Animation(scale=0.98, d=0.06)
            +
            Animation(scale=1, d=0.06)
        ).start(self)
