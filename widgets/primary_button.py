from kivy.metrics import dp

from kivymd.uix.button import (
    MDButton,
    MDButtonText,
)


from config.theme import COLORS


class PrimaryButton(MDButton):
    """
    Reusable Filled Button
    KivyMD 2.x
    """

    def __init__(
        self,
        text="",
        on_release=None,
        **kwargs,
    ):
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

        if on_release:
            self.bind(on_release=on_release)

    def set_text(self, text):
        for child in self.children:
            if isinstance(child, MDButtonText):
                child.text = text
                return
