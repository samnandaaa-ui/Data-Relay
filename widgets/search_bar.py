from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldLeadingIcon,
    MDTextFieldHintText,
)


class SearchBar(MDTextField):

    def __init__(self, hint="Cari...", **kwargs):
        super().__init__(**kwargs)

        self.mode = "filled"

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
