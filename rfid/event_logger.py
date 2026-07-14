from tkinter import scrolledtext
from datetime import datetime


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

    def append(self, message):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.configure(state="normal")
        self.insert("end", f"[{current_time}] {message}\n")
        self.see("end")
        self.configure(state="disabled")


def write_log(message, log_box=None):
    if log_box is None:
        return
    log_box.append(message)

