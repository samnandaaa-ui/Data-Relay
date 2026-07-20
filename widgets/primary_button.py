from kivy.metrics import dp

from kivymd.uix.button import MDButton, MDButtonText

from config.theme import COLORS


class PrimaryButton(MDButton):

    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)

        self.style = "filled"
        self.theme_bg_color = "Custom"
        self.md_bg_color = COLORS["accent"]

        self.size_hint_y = None
        self.height = dp(48)

        self.add_widget(
            MDButtonText(
                text=text
            )
        )
