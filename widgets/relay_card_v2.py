from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from config.theme import COLORS


class RelayCardV2(MDCard):

    def __init__(self, title, subtitle="", **kwargs):
        super().__init__(**kwargs)

        self.style = "elevated"
        self.ripple_behavior = True

        self.padding = dp(16)
        self.spacing = dp(6)

        self.orientation = "vertical"

        self.radius = [dp(14)]

        self.theme_bg_color = "Custom"
        self.md_bg_color = COLORS["input_bg"]

        title_lbl = MDLabel(
            text=title,
            font_style="Title",
            role="large",
            adaptive_height=True,
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        )

        self.add_widget(title_lbl)

        if subtitle:

            self.add_widget(

                MDLabel(
                    text=subtitle,
                    font_style="Body",
                    role="medium",
                    adaptive_height=True,
                    theme_text_color="Custom",
                    text_color=COLORS["text_secondary"],
                )

            )
