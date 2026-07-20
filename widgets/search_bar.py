from kivy.metrics import dp

from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
)


class SearchBar(MDTextField):
    """
    Reusable Search Bar
    KivyMD 2.x
    """

    def __init__(
        self,
        hint="Cari...",
        on_text=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.mode = "filled"

        self.size_hint_y = None
        self.height = dp(56)

        self.add_widget(
            MDTextFieldLeadingIcon(
                icon="magnify"
            )
        )

        self.add_widget(
            MDTextFieldHintText(
                text=hint
            )
        )

        if on_text:
            self.bind(text=lambda instance, value: on_text(value))

    def clear(self):
        self.text = ""

    def get_text(self):
        return self.text.strip()
