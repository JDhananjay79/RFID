import json
import os
import threading
from datetime import datetime
from tkinter import scrolledtext

MAX_LOG_LINES = 1000
JSON_LOG_FILE = os.path.join(os.getcwd(), "activity_records.json")


class LogConsole(scrolledtext.ScrolledText):
    """Custom ScrolledText widget for activity logging and JSON file persistence."""

    def __init__(self, master=None, max_lines: int = MAX_LOG_LINES, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            width=60,
            height=14,
            state="disabled",
            font=("Consolas", 10),
            wrap="word",
            bg="#111827",
            fg="#F9FAFB",
            insertbackground="#F9FAFB",
        )
        self.file_path = None
        self.auto_save = False
        self.max_lines = max_lines
        self.line_count = 0
        self.json_file_path = JSON_LOG_FILE
        self._lock = threading.Lock()

    def append(self, message: str):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        line = f"[{current_time}] {message}\n"

        self.configure(state="normal")
        self.insert("end", line)
        self.line_count += 1

        if self.line_count > self.max_lines:
            overflow = self.line_count - self.max_lines
            self.delete("1.0", f"{overflow + 1}.0")
            self.line_count = self.max_lines

        self.see("end")
        self.configure(state="disabled")

        if self.auto_save and self.file_path:
            try:
                with self._lock:
                    with open(self.file_path, "a", encoding="utf-8") as f:
                        f.write(line)
            except Exception:
                pass

    def append_json(self, name: str, operation: str, command_sent: str,
                    response_received: str = "", conversion: str = "",
                    medium: str = "UART") -> dict:
        """Record structured JSON entry directly to activity_records.json without printing raw JSON in console."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        record = {
            "Name": name,
            "Operation": operation,
            "Command Sent": command_sent,
            "Response Received": response_received,
            "Conversion": conversion,
            "Medium of transmission": medium,
            "Time Stamp": current_time,
        }

        # Save to activity_records.json
        try:
            with self._lock:
                records = []
                if os.path.exists(self.json_file_path):
                    try:
                        with open(self.json_file_path, "r", encoding="utf-8") as jf:
                            records = json.load(jf)
                            if not isinstance(records, list):
                                records = []
                    except Exception:
                        records = []

                records.append(record)
                with open(self.json_file_path, "w", encoding="utf-8") as jf:
                    json.dump(records, jf, indent=2)
        except Exception:
            pass

        return record

    def set_file_path(self, path: str):
        self.file_path = path

    def enable_auto_save(self, enable: bool):
        self.auto_save = bool(enable)

    def save_all(self, path: str = None) -> bool:
        p = path or self.file_path
        if not p:
            return False
        try:
            text = self.get("1.0", "end")
            with open(p, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception:
            return False

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.line_count = 0
        self.configure(state="disabled")


def write_log(message: str, log_box: LogConsole = None):
    if log_box is not None:
        log_box.append(message)
