from tkinter import scrolledtext
from datetime import datetime
import threading


class LogConsole(scrolledtext.ScrolledText):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            width=60,
            height=14,
            state="disabled",
            font=("Segoe UI", 10),
            wrap="word",
            bg="#1f2937",
            fg="#f8fafc",
            insertbackground="#F9FAFB",
        )
        # autosave settings
        self.file_path = None
        self.auto_save = False
        self._lock = threading.Lock()

    def append(self, message):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{current_time}] {message}\n"

        self.configure(state="normal")
        self.insert("end", line)
        self.see("end")
        self.configure(state="disabled")

        if self.auto_save and self.file_path:
            try:
                with self._lock:
                    with open(self.file_path, "a", encoding="utf-8") as f:
                        f.write(line)
            except Exception:
                pass

    def set_file_path(self, path: str):
        self.file_path = path

    def enable_auto_save(self, enable: bool):
        self.auto_save = bool(enable)

    def save_all(self, path: str = None):
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


def write_log(message, log_box=None):
    if log_box is None:
        return
    log_box.append(message)

