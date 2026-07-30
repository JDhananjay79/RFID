import threading
from datetime import datetime
from tkinter import scrolledtext

MAX_LOG_LINES = 1000


class LogConsole(scrolledtext.ScrolledText):
    """Custom ScrolledText widget for formatted, timestamped activity logging with auto-pruning."""

    def __init__(self, master=None, max_lines: int = MAX_LOG_LINES, **kwargs):
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
        self.file_path = None
        self.auto_save = False
        self.max_lines = max_lines
        self.line_count = 0
        self._lock = threading.Lock()

    def append(self, message: str):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{current_time}] {message}\n"

        self.configure(state="normal")
        self.insert("end", line)
        self.line_count += 1

        # Auto-prune old lines to maintain a flat memory footprint and high FPS
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
