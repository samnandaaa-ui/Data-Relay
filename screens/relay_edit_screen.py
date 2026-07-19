"""
screens/relay_edit_screen.py
Form edit satu jenis relay (OCRL/OCRH/GFRL/GFRH/Directional/Thermal) utk
satu node. Dibuka dengan tap kartu relay di NodeScreen (baik yang sudah
ada isinya, maupun yang masih "Belum diisi" -- keduanya form yang sama).
Daftar kurva TIDAK di-hardcode -- diambil dari relay_curve_types.
Warna diambil dari config/theme.py (ikut dark mode Android otomatis).
"""

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.metrics import dp

from models.relay_model import (
    RELAY_TYPE_LABELS,
    get_curve_options,
    get_raw_relay_setting,
    upsert_relay_setting,
)
from config.theme import COLORS

NO_CURVE_TEXT = "Pilih kurva"

Builder.load_string(r"""
#:import COLORS config.theme.COLORS

<RelayEditScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            Button:
                text: "< Batal"
                font_size: "16sp"
                size_hint_x: None
                width: dp(100)
                on_release: root.cancel()

        Label:
            text: root.header_text
            font_size: "24sp"
            bold: True
            size_hint_y: None
            height: dp(40)
            color: COLORS["text_primary"]
            halign: "left"
            text_size: self.width, None

        ScrollView:
            BoxLayout:
                id: form_fields
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(14)
                padding: [0, dp(10)]

        Button:
            text: "Simpan"
            font_size: "20sp"
            bold: True
            size_hint_y: None
            height: dp(64)
            background_color: COLORS["save"]
            on_release: root.save()
""")


class RelayEditScreen(Screen):
    header_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_id = None
        self.relay_type = None
        self.inputs = {}
        self.enabled_switch = None
        self.curve_spinner = None

    def open_for(self, node_id, relay_type, node_nama):
        self.node_id = node_id
        self.relay_type = relay_type
        self.header_text = f"{RELAY_TYPE_LABELS[relay_type]} - {node_nama}"
        self._build_form()

    def _build_form(self):
        container = self.ids.form_fields
        container.clear_widgets()
        self.inputs = {}
        self.curve_spinner = None

        row = get_raw_relay_setting(self.node_id, self.relay_type)

        self.enabled_switch = Switch(active=bool(row["enabled"]) if row else False)
        container.add_widget(self._field_row("Aktif", self.enabled_switch))

        self.inputs["pickup_xin"] = self._number_field(container, "Pickup (x In)", row, "pickup_xin")
        self.inputs["pickup_ampere"] = self._number_field(container, "Pickup (Ampere)", row, "pickup_ampere")

        if self.relay_type in ("ocrl", "gfrl"):
            self.inputs["tms"] = self._number_field(container, "TMS (detik)", row, "tms")
            current_curve = row["curve"] if row and row["curve"] else NO_CURVE_TEXT
            self.curve_spinner = Spinner(
                text=current_curve,
                values=get_curve_options(),
                size_hint_y=None, height=dp(48), font_size="18sp",
            )
            container.add_widget(self._field_row("Kurva", self.curve_spinner))
        elif self.relay_type == "thermal":
            self.inputs["trip_time_minutes"] = self._number_field(container, "Trip (menit)", row, "trip_time_minutes")
            self.inputs["alarm_percent"] = self._number_field(container, "Alarm (%)", row, "alarm_percent")
            self.inputs["trip_percent"] = self._number_field(container, "Trip (%)", row, "trip_percent")
        else:
            self.inputs["delay"] = self._number_field(container, "Delay (detik)", row, "delay")

    def _number_field(self, container, label_text, row, field):
        value = row[field] if row and row.get(field) is not None else ""
        ti = TextInput(
            text=str(value), input_filter="float", multiline=False,
            font_size="18sp", size_hint_y=None, height=dp(48),
            background_color=COLORS["input_bg"], foreground_color=COLORS["text_primary"],
        )
        container.add_widget(self._field_row(label_text, ti))
        return ti

    def _field_row(self, label_text, widget):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(10))
        lbl = Label(
            text=label_text, font_size="16sp", size_hint_x=0.45,
            halign="left", valign="middle", color=COLORS["text_primary"],
        )
        lbl.bind(size=lbl.setter("text_size"))
        row.add_widget(lbl)
        row.add_widget(widget)
        return row

    def _parse_float(self, text):
        text = (text or "").strip()
        return float(text) if text else None

    def save(self):
        values = {field: self._parse_float(widget.text) for field, widget in self.inputs.items()}

        curve = None
        if self.curve_spinner is not None and self.curve_spinner.text != NO_CURVE_TEXT:
            curve = self.curve_spinner.text

        upsert_relay_setting(
            node_id=self.node_id,
            relay_type=self.relay_type,
            enabled=self.enabled_switch.active,
            pickup_xin=values.get("pickup_xin"),
            pickup_ampere=values.get("pickup_ampere"),
            tms=values.get("tms"),
            curve=curve,
            delay=values.get("delay"),
            trip_time_minutes=values.get("trip_time_minutes"),
            alarm_percent=values.get("alarm_percent"),
            trip_percent=values.get("trip_percent"),
        )
        self.manager.get_screen("node").load_node(self.node_id)
        self.manager.current = "node"

    def cancel(self):
        self.manager.current = "node"
