"""
Base widget untuk komponen Data-Relay.
"""

from kivy.properties import NumericProperty
from kivymd.uix.relativelayout import MDRelativeLayout


class BaseWidget(MDRelativeLayout):
    """Widget dasar yang nantinya dapat ditambah animasi dan style umum."""

    scale = NumericProperty(1.0)
