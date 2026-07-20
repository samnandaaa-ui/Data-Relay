"""
Data Relay
Base Widget

Widget dasar untuk seluruh komponen UI.

Semua widget baru sebaiknya mewarisi BaseWidget
agar memiliki utilitas umum dan animasi yang konsisten.
"""

from kivy.animation import Animation
from kivy.properties import NumericProperty

from kivymd.uix.relativelayout import MDRelativeLayout

from config.theme import ANIMATION


class BaseWidget(MDRelativeLayout):
    """Base class untuk widget Data Relay."""

    scale = NumericProperty(1.0)

    def animate_press(self):
        """Animasi saat widget ditekan."""

        Animation.cancel_all(self)

        (
            Animation(
                scale=0.97,
                duration=ANIMATION["fast"]
            )
            +
            Animation(
                scale=1.0,
                duration=ANIMATION["fast"]
            )
        ).start(self)

    def fade_in(self):

        self.opacity = 0

        Animation(
            opacity=1,
            duration=ANIMATION["normal"]
        ).start(self)

    def fade_out(self):

        Animation(
            opacity=0,
            duration=ANIMATION["normal"]
        ).start(self)
