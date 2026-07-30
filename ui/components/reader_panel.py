"""
DISABLED / COMMENTED COMPONENT: Reader Panel
The Reader Status and Scan controls component has been commented out per user request.
"""

# import tkinter as tk
# from tkinter import messagebox
# import ttkbootstrap as ttkb
# from logger import write_log
#
#
# class ReaderPanelFrame:
#     """Component managing Reader status and Scan control buttons."""
#
#     def __init__(self, parent_frame, reader, log_console_getter):
#         self.reader = reader
#         self.get_log_console = log_console_getter
#
#         self.reader_frame = tk.LabelFrame(
#             parent_frame,
#             text="Reader",
#             padx=18,
#             pady=18,
#             bg="#1f2937",
#             fg="#f8fafc",
#             font=("Segoe UI", 11, "bold"),
#         )
#         self.reader_frame.pack(side="left", fill="y", padx=(0, 10), expand=False)
#         self.reader_frame.configure(width=260)
#         self.reader_frame.columnconfigure(1, weight=1)
#         self.reader_frame.columnconfigure(3, weight=1)
#
#         self.reader_status = tk.StringVar(value="Idle")
#         self.tag_present = tk.StringVar(value="No")
#
#         self._build_widgets()
#
#     def _build_widgets(self):
#         ttkb.Label(self.reader_frame, text="Status:", style="Field.TLabel").grid(
#             row=0, column=0, sticky="w", pady=(0, 10)
#         )
#         ttkb.Label(
#             self.reader_frame, textvariable=self.reader_status, style="Value.TLabel"
#         ).grid(row=0, column=1, sticky="w", padx=(10, 36), pady=(0, 10))
#
#         ttkb.Label(self.reader_frame, text="Tag Present:", style="Field.TLabel").grid(
#             row=0, column=2, sticky="w", pady=(0, 10)
#         )
#         ttkb.Label(
#             self.reader_frame, textvariable=self.tag_present, style="Value.TLabel"
#         ).grid(row=0, column=3, sticky="w", padx=(10, 0), pady=(0, 10))
#
#         reader_button_frame = ttkb.Frame(self.reader_frame)
#         reader_button_frame.grid(row=1, column=0, columnspan=4, pady=(16, 0), sticky="ew")
#         reader_button_frame.columnconfigure(0, weight=1)
#         reader_button_frame.columnconfigure(1, weight=1)
#
#         self.start_scan_button = ttkb.Button(
#             reader_button_frame,
#             text="Start Scan",
#             command=self.start_scan,
#             bootstyle="info",
#             state="disabled",
#         )
#         self.start_scan_button.grid(row=0, column=0, sticky="ew", padx=(0, 14))
#
#         self.stop_scan_button = ttkb.Button(
#             reader_button_frame,
#             text="Stop Scan",
#             command=self.stop_scan,
#             bootstyle="secondary",
#             state="disabled",
#         )
#         self.stop_scan_button.grid(row=0, column=1, sticky="ew", padx=(14, 0))
#
#     def set_connection_state(self, connected: bool):
#         if connected:
#             self.start_scan_button.configure(state="normal")
#             self.stop_scan_button.configure(state="normal")
#         else:
#             self.reader_status.set("Idle")
#             self.tag_present.set("No")
#             self.start_scan_button.configure(state="disabled")
#             self.stop_scan_button.configure(state="disabled")
#
#     def reset_status(self):
#         self.reader_status.set("Idle")
#         self.tag_present.set("No")
#
#     def start_scan(self):
#         log_console = self.get_log_console()
#         if not self.reader.is_connected():
#             messagebox.showwarning("Start Scan", "Connect the reader before scanning.")
#             return
#         self.reader_status.set("Scanning")
#         if self.reader.write_line("SCAN\n"):
#             write_log("Start scan command sent", log_console)
#         else:
#             write_log("Failed to send scan command", log_console)
#
#     def stop_scan(self):
#         if not self.reader.is_connected():
#             return
#         self.reader_status.set("Idle")
#         write_log("Stop scan", self.get_log_console())
