from pathlib import Path
import ttkbootstrap as ttkb

from config import PORT, BAUDRATE
from communication import SerialReader
from logger import write_log
from ui.components.header import build_header_frame
from ui.components.tag_form import TagFormFrame
from ui.components.comm_panel import CommPanelFrame
# Reader panel component commented out per user request
# from ui.components.reader_panel import ReaderPanelFrame
from ui.components.log_panel import LogPanelFrame


class RFIDApp:
    """Main Application orchestrator for RFID Communicator UI."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent

        self.root = ttkb.Window(themename="darkly")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 750)
        self.root.title("RFID Communicator")

        self._configure_styles()
        self._set_app_icon()

        self.reader = SerialReader(PORT, BAUDRATE)
        self.logging_enabled = False
        self.rx_buffer = bytearray()

        self.main_frame = ttkb.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.header_frame = build_header_frame(self.main_frame, self.base_dir)

        self.content_frame = ttkb.Frame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.right_panel = ttkb.Frame(self.content_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.top_row = ttkb.Frame(self.right_panel)
        self.top_row.pack(fill="x", pady=(0, 12))

        # Log panel component
        self.log_panel_comp = LogPanelFrame(self.right_panel, self.root)

        # Comm panel component
        self.comm_panel_comp = CommPanelFrame(
            self.top_row,
            self.reader,
            lambda: self.log_panel_comp.log_console,
            self._on_connection_change,
        )

        # Tag form component (passes reader for UART read/write actions)
        self.tag_form_comp = TagFormFrame(
            self.content_frame,
            self.root,
            self.reader,
            lambda: self.log_panel_comp.log_console,
            reset_reader_status_cb=None,
        )

        self._bind_events()
        self.root.after(50, self.update_gui)

    def _configure_styles(self):
        style = ttkb.Style(theme="darkly")
        style.configure("Card.TFrame", background="#1f2937")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#F8FAFC")
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#E2E8F0")
        style.configure("Field.TLabel", font=("Segoe UI", 10), foreground="#E2E8F0")
        style.configure("Caption.TLabel", font=("Segoe UI", 9), foreground="#94a3b8")
        style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"), foreground="#A5B4FC")
        style.configure("Value.TLabel", font=("Segoe UI", 10), foreground="#E2E8F0")

    def _set_app_icon(self):
        icon_path = self.base_dir / "assets" / "Acc_logo.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except Exception:
                pass

    def _on_connection_change(self, connected: bool):
        pass

    def _bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        try:
            log_c = self.log_panel_comp.log_console
            log_c.bind("<Control-v>", self._handle_paste_to_log)
            log_c.bind("<Control-V>", self._handle_paste_to_log)
        except Exception:
            pass

    def _handle_paste_to_log(self, event=None):
        try:
            txt = self.root.clipboard_get()
        except Exception:
            return "break"

        hb = self._hex_bytes_from_text(txt.strip())
        if hb is None:
            return "break"

        log_c = self.log_panel_comp.log_console
        if self.reader.is_connected():
            self.reader.write_bytes(hb)
            write_log(f"UART TX (hex): {hb.hex().upper()}", log_c)
        else:
            write_log("UART TX ignored: reader not connected", log_c)

        return "break"

    @staticmethod
    def _hex_bytes_from_text(s: str) -> bytes | None:
        filtered = s.replace("0x", "").replace("0X", "").replace(" ", "")
        if len(filtered) % 2 != 0:
            return None
        try:
            return bytes.fromhex(filtered)
        except Exception:
            return None

    def _parse_uart_response(self, frame: bytes):
        """Universal parser for UART response frames starting with 24EF and ending with 23."""
        try:
            if len(frame) < 6:
                return

            tag_byte = frame[3]  # Payload Parameter Tag ID
            data_bytes = frame[4:-3] if len(frame) >= 7 else frame[4:-1]

            if tag_byte == 0x40:  # Tag EPC (0x00) -> Hex As-Is
                hex_val = data_bytes.hex().upper()
                self.tag_form_comp.set_field_value("tag_id", hex_val)
                write_log(f"Tag EPC Received: {hex_val}", self.log_panel_comp.log_console)

            elif tag_byte == 0x41:  # Serial Reader Number (0x01) -> Alphanumeric
                ascii_val = data_bytes.decode("ascii", errors="ignore").rstrip("\x00").strip()
                self.tag_form_comp.set_field_value("serial", ascii_val)
                write_log(f"Serial Number Received: {ascii_val}", self.log_panel_comp.log_console)

            elif tag_byte == 0x42:  # Trailer VIN (0x02) -> Alphanumeric
                ascii_val = data_bytes.decode("ascii", errors="ignore").rstrip("\x00").strip()
                self.tag_form_comp.set_field_value("vin", ascii_val)
                write_log(f"VIN Received: {ascii_val}", self.log_panel_comp.log_console)

            elif tag_byte == 0x43:  # Axle Count (0x03) -> Numerical
                num_val = int.from_bytes(data_bytes, byteorder="big") if data_bytes else 0
                self.tag_form_comp.set_field_value("axle", str(num_val))
                write_log(f"Axle Count Received: {num_val}", self.log_panel_comp.log_console)

            elif tag_byte == 0x44:  # Registration Number (0x04) -> Alphanumeric
                ascii_val = data_bytes.decode("ascii", errors="ignore").rstrip("\x00").strip()
                self.tag_form_comp.set_field_value("registration", ascii_val)
                write_log(f"Registration Number Received: {ascii_val}", self.log_panel_comp.log_console)

            elif tag_byte == 0x45:  # Gross Weight (0x05) -> Decimal
                weight_val = int.from_bytes(data_bytes, byteorder="big") if data_bytes else 0
                self.tag_form_comp.set_field_value("gvw", str(weight_val))
                write_log(f"Gross Weight Received: {weight_val}", self.log_panel_comp.log_console)

            elif tag_byte in (0x7F, 0x46):  # Meta Data / TA Cert (0x06) -> Hex As-Is
                hex_val = data_bytes.hex().upper()
                self.tag_form_comp.set_field_value("cert", hex_val)
                write_log(f"Meta Data Received: {hex_val}", self.log_panel_comp.log_console)

        except Exception as e:
            write_log(f"Error parsing response frame: {e}", self.log_panel_comp.log_console)

    def update_gui(self):
        """Optimized GUI event loop that processes UART byte batches without locking the main thread."""
        batch = self.reader.get_raw_batch(max_items=30)
        for raw in batch:
            self.rx_buffer.extend(raw)

        # Buffer cap protection
        if len(self.rx_buffer) > 8192:
            del self.rx_buffer[:-2048]

        # Parse framed UART packets ($ ... #)
        while True:
            try:
                start = self.rx_buffer.index(0x24)  # '$'
            except ValueError:
                self.rx_buffer.clear()
                break

            # Discard preceding noise before frame start
            if start > 0:
                del self.rx_buffer[:start]

            try:
                end = self.rx_buffer.index(0x23, 1)  # '#'
            except ValueError:
                if len(self.rx_buffer) > 512:
                    del self.rx_buffer[0]
                break

            frame = bytes(self.rx_buffer[: end + 1])
            del self.rx_buffer[: end + 1]

            frame_hex = frame.hex().upper()
            write_log(
                f"UART RX (hex): {frame_hex}",
                self.log_panel_comp.log_console,
            )

            # Check if frame is a valid response packet (starts with 24EF)
            if frame_hex.startswith("24EF"):
                self._parse_uart_response(frame)

        self.root.after(50, self.update_gui)

    def on_close(self):
        try:
            self.reader.stop()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


def create_app() -> ttkb.Window:
    app = RFIDApp()
    return app.root
