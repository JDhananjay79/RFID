import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from pathlib import Path
from PIL import Image, ImageTk
from event_logger import write_log, LogConsole
import ttkbootstrap as ttk


class UI:
    def __init__(self, master, value, name):
        self.master = master
        self.value = value
        self.name = name


root = ttkb.Window(themename="darkly")
root.geometry("1280x760")
root.minsize(1150, 700)
root.title("RFID Communicator")

style = ttkb.Style(theme="darkly")
style.configure("Card.TFrame", background="#223446")
style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#F8FAFC")
style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#E2E8F0")
style.configure("Field.TLabel", font=("Segoe UI", 10), foreground="#E2E8F0")
style.configure("Log.TFrame", background="#111827")

main_frame = ttkb.Frame(root)
main_frame.pack(fill="both", expand=True)

BASE_DIR = Path(__file__).resolve().parent
icon_path = BASE_DIR.parent / "assets" / "Acc_logo.ico"

root.iconbitmap(str(icon_path))


header_frame = ttkb.Frame(main_frame)
header_frame.pack(fill="x", pady=(0, 15))

BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR.parent / "Acc_logo.png"
photo = None
if os.path.exists(logo_path):
    image = Image.open(logo_path)
    image = image.resize((120, 80))
    photo = ImageTk.PhotoImage(image)

if photo:
    logo_label = ttkb.Label(header_frame, image=photo, bootstyle="light")
    logo_label.image = photo
    logo_label.pack(side="left", padx=(15, 20), pady=(20,20))

header_text = ttkb.Label(header_frame, text="RFID Tag Writer", style="Title.TLabel")
header_text.pack(side="left", pady=10)

content_frame = ttkb.Frame(main_frame)
content_frame.pack(fill="both", expand=True)

form_container = tk.LabelFrame(
    content_frame,
    text="Tag Data",
    padx=20,
    pady=20,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 12, "bold"),
)
form_container.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=(0, 10))

form_grid = ttkb.Frame(form_container)
form_grid.pack(fill="both", expand=True)

field_vars = {}
field_rows = [
    ("Tag ID Storage", "tag_id"),
    ("Serial Number Storage", "serial"),
    ("TA Certification Storage", "cert"),
    ("GVW/GCW Storage", "gvm"),
    ("VIN Storage", "vin"),
    ("Registration No.", "registration"),
    ("Axle Count Storage", "axle"),
    ("Insurance Information", "insurance"),
]

for index, (label_text, var_name) in enumerate(field_rows):
    row = index // 2
    col = index % 2
    label = ttkb.Label(form_grid, text=label_text, style="Field.TLabel")
    label.grid(row=row * 2, column=col, sticky="w", padx=(0, 15), pady=(0, 5))
    var = tk.StringVar()
    field_vars[var_name] = var
    entry = ttkb.Entry(form_grid, textvariable=var, bootstyle="info")
    entry.grid(row=row * 2 + 1, column=col, sticky="ew", padx=(0, 15), pady=(0, 12))

form_grid.columnconfigure(0, weight=1)
form_grid.columnconfigure(1, weight=1)

button_row = ttkb.Frame(form_container)
button_row.pack(fill="x", pady=(10, 0))


def TagDataForm():
    write_log("Starting RFID writing...")
    tag_id = field_vars["tag_id"].get()
    serial = field_vars["serial"].get()
    cert = field_vars["cert"].get()
    gvm = field_vars["gvm"].get()
    vin_store = field_vars["vin"].get()
    reg = field_vars["registration"].get()
    axle = field_vars["axle"].get()
    insurance = field_vars["insurance"].get()

    if all([tag_id, serial, cert, gvm, vin_store, reg, axle, insurance]):
        messagebox.showinfo("Status", "Data Submitted")
    else:
        messagebox.showinfo("Error", "Please fill all the fields")


submit_button = ttkb.Button(
    button_row, text="Submit", command=TagDataForm, bootstyle="success-outline"
)
submit_button.pack(side="right", pady=(0, 330))

right_panel = ttkb.Frame(content_frame)
right_panel.pack(side="right", fill="y")

controls_frame = tk.LabelFrame(
    right_panel,
    text="Controls",
    padx=(12),
    pady=(12),
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
controls_frame.pack(fill="x", padx=(0, 10), pady=(0, 20))

search_var = tk.StringVar()


def search():
    write_log(f"Searching VIN: {search_var.get()}")
    if not search_var.get():
        messagebox.showinfo("Search", "Enter a VIN to search")


search_label = ttkb.Label(controls_frame, text="Search VIN No.", style="Section.TLabel")
search_label.pack(anchor="w")

search_box = ttkb.Frame(controls_frame)
search_box.pack(fill="x", pady=(6, 0))

search_entry = ttkb.Entry(search_box, textvariable=search_var, bootstyle="info")
search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

search_button = ttkb.Button(search_box, text="🔍", command=search, bootstyle="info")
search_button.pack(side="right")

selected_option = tk.StringVar(value="Choose Medium")


def on_select(event):
    write_log(f"Selected medium: {selected_option.get()}")


medium_label = ttkb.Label(
    controls_frame, text="Select Data Transmit Medium", style="Section.TLabel"
)
medium_label.pack(anchor="w", pady=(12, 6))

dropdown = ttkb.Combobox(
    controls_frame,
    textvariable=selected_option,
    values=["UART", "PCAN"],
    state="readonly",
    bootstyle="info",
)
dropdown.pack(fill="x")
dropdown.bind("<<ComboboxSelected>>", on_select)

log_frame = tk.LabelFrame(
    right_panel,
    text="Activity Log",
    padx=10,
    pady=10,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
log_frame.pack(fill="both", expand=True)

log_console = LogConsole(log_frame)
log_console.pack(fill="both", expand=True)

write_log("RFID Communicator started", log_console)

root.mainloop()
