from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from config.theme import COLORS


class RelayCardV2(MDCard):
    """
    Reusable Relay Card
    """

    def __init__(
        self,
        title="",
        subtitle="",
        on_release=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.orientation = "vertical"

        self.style = "elevated"

        self.ripple_behavior = True

        self.padding = dp(16)
        self.spacing = dp(6)

        self.radius = [dp(14)]

        self.size_hint_y = None

        self.theme_bg_color = "Custom"
        self.md_bg_color = COLORS["input_bg"]

        self.bind(minimum_height=self.setter("height"))

        self.title_label = MDLabel(
            text=title,
            font_style="Title",
            role="large",
            adaptive_height=True,
            halign="left",
            theme_text_color="Custom",
            text_color=COLORS["text_primary"],
        )

        self.title_label.bind(
            width=lambda inst, val:
            setattr(inst, "text_size", (val, None))
        )

        self.add_widget(self.title_label)

        self.subtitle_label = MDLabel(
            text=subtitle,
            font_style="Body",
            role="medium",
            adaptive_height=True,
            halign="left",
            theme_text_color="Custom",
            text_color=COLORS["text_secondary"],
        )

        self.subtitle_label.bind(
            width=lambda inst, val:
            setattr(inst, "text_size", (val, None))
        )

        if subtitle:
            self.add_widget(self.subtitle_label)

        if on_release:
            self.bind(on_release=on_release)

    def set_title(self, text):
        self.title_label.text = text

    def set_subtitle(self, text):
        self.subtitle_label.text = text

        if text:
            if self.subtitle_label.parent is None:
                self.add_widget(self.subtitle_label)
        else:
            if self.subtitle_label.parent:
                self.remove_widget(self.subtitle_label)

