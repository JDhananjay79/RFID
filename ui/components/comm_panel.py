import threading
import tkinter as tk
import ttkbootstrap as ttkb
from serial.tools import list_ports
from config import PORT, BAUDRATE
from logger import write_log


def detect_com_ports():
    try:
        ports = [port.device for port in list_ports.comports()]
        return sorted(ports)
    except Exception:
        return []


class CommPanelFrame:
    """Component managing serial communication settings and non-blocking connect/disconnect controls."""

    def __init__(self, parent_frame, reader, log_console_getter, on_connection_change_cb):
        self.reader = reader
        self.get_log_console = log_console_getter
        self.on_connection_change_cb = on_connection_change_cb

        # Register async disconnect callback with SerialReader
        self.reader.set_disconnect_callback(self._on_async_disconnect)

        self.communication_frame = tk.LabelFrame(
            parent_frame,
            text="Communication",
            padx=18,
            pady=18,
            bg="#1f2937",
            fg="#f8fafc",
            font=("Segoe UI", 11, "bold"),
        )
        self.communication_frame.pack(side="left", fill="y", expand=False, padx=(0, 10), pady=(0, 4))
        self.communication_frame.configure(width=400)
        self.communication_frame.columnconfigure(1, weight=1)
        self.communication_frame.columnconfigure(3, weight=1)

        self.medium_var = tk.StringVar(value="UART")
        self.status_var = tk.StringVar(value="Disconnected")
        self.baud_var = tk.StringVar(value=str(BAUDRATE))

        ports = detect_com_ports()
        if not ports:
            ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
        default_port = PORT if PORT in ports else ports[0]
        self.port_var = tk.StringVar(value=default_port)

        self._build_widgets(ports)

    def _build_widgets(self, available_ports):
        available_baud_rates = ["9600", "19200", "38400", "57600", "115200"]
        self.port_combobox = None

        fields = [
            ("Medium", self.medium_var, ["UART", "PCAN"]),
            ("COM Port", self.port_var, available_ports),
            ("Baud Rate", self.baud_var, available_baud_rates),
        ]

        for label_text, variable, values in fields:
            if label_text == "Medium":
                row, col, grid_padx, grid_pady = 0, 0, (12, 24), (0, 10)
            elif label_text == "COM Port":
                row, col, grid_padx, grid_pady = 0, 2, (12, 0), (0, 10)
            else:
                row, col, grid_padx, grid_pady = 1, 0, (12, 0), (0, 16)

            ttkb.Label(self.communication_frame, text=label_text, style="Field.TLabel").grid(
                row=row, column=col, sticky="w", pady=(0, 10)
            )
            combobox = ttkb.Combobox(
                self.communication_frame,
                textvariable=variable,
                values=values,
                state="readonly",
                bootstyle="info",
                width=18,
            )
            combobox.grid(row=row, column=col + 1, sticky="w", padx=grid_padx, pady=grid_pady)
            if label_text == "COM Port":
                self.port_combobox = combobox

        button_frame_comm = ttkb.Frame(self.communication_frame)
        button_frame_comm.grid(row=2, column=0, columnspan=3, pady=(16, 0), sticky="ew")
        button_frame_comm.columnconfigure(0, weight=1)
        button_frame_comm.columnconfigure(1, weight=1)
        button_frame_comm.columnconfigure(2, weight=1)

        self.connect_button = ttkb.Button(
            button_frame_comm,
            text="Connect",
            command=self.connect_reader,
            bootstyle="success",
        )
        self.connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 14))

        self.disconnect_button = ttkb.Button(
            button_frame_comm,
            text="Disconnect",
            command=self.disconnect_reader,
            bootstyle="danger",
            state="disabled",
        )
        self.disconnect_button.grid(row=0, column=1, sticky="ew", padx=(14, 14))

        status_frame = ttkb.Frame(button_frame_comm)
        status_frame.grid(row=0, column=2, sticky="w", padx=(14, 0))

        ttkb.Label(status_frame, text="Status:", style="Field.TLabel").pack(side="left", padx=(0, 4))
        ttkb.Label(status_frame, textvariable=self.status_var, style="Value.TLabel").pack(side="left")

    def populate_com_ports(self):
        ports = detect_com_ports()
        if not ports:
            ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
        if self.port_combobox:
            self.port_combobox.configure(values=ports)
        if self.port_var.get() not in ports:
            self.port_var.set(ports[0])

    def connect_reader(self):
        log_console = self.get_log_console()
        if self.reader.is_connected():
            write_log("Reader already connected", log_console)
            return

        selected_port = self.port_var.get()
        try:
            selected_baud = int(self.baud_var.get())
        except ValueError:
            selected_baud = 115200

        self.status_var.set("Connecting...")
        self.connect_button.configure(state="disabled")

        def _do_connect():
            success = self.reader.connect(
                port=selected_port,
                baudrate=selected_baud,
            )
            # Schedule GUI update on main thread for Tcl thread safety
            try:
                self.communication_frame.after(
                    0, lambda: self._on_connect_finished(success, selected_port, selected_baud)
                )
            except Exception:
                pass

        threading.Thread(target=_do_connect, daemon=True).start()

    def _on_connect_finished(self, success: bool, port: str, baud: int):
        log_console = self.get_log_console()
        if success:
            self.status_var.set("Connected")
            self.connect_button.configure(state="disabled")
            self.disconnect_button.configure(state="normal")
            write_log(f"Connected to {port} @ {baud}", log_console)
            if callable(self.on_connection_change_cb):
                self.on_connection_change_cb(True)
        else:
            self.status_var.set("Disconnected")
            self.connect_button.configure(state="normal")
            self.disconnect_button.configure(state="disabled")
            write_log(f"Failed to connect to {port}", log_console)
            if callable(self.on_connection_change_cb):
                self.on_connection_change_cb(False)

    def _on_async_disconnect(self):
        """Handle background thread disconnection gracefully on UI thread."""
        try:
            self.communication_frame.after(0, self._process_async_disconnect)
        except Exception:
            pass

    def _process_async_disconnect(self):
        self.status_var.set("Disconnected")
        self.connect_button.configure(state="normal")
        self.disconnect_button.configure(state="disabled")
        write_log("Reader connection lost or closed", self.get_log_console())
        if callable(self.on_connection_change_cb):
            self.on_connection_change_cb(False)

    def disconnect_reader(self):
        def _do_disconnect():
            self.reader.disconnect()
            try:
                self.communication_frame.after(0, self._process_async_disconnect)
            except Exception:
                pass

        threading.Thread(target=_do_disconnect, daemon=True).start()
