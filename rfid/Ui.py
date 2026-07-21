import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from pathlib import Path
from PIL import Image, ImageTk
from config import PORT, BAUDRATE, LOG_DEFAULT_PATH
from logger import write_log
from rfid.event_logger import LogConsole
from rfid.serial_port import SerialReader

logging_enabled = False

reader = SerialReader(PORT, BAUDRATE)
reader.connect()

class UI:
    def __init__(self, master, value, name):
        self.master = master
        self.value = value
        self.name = name


root = ttkb.Window(themename="darkly")
root.geometry("2000x900")
root.minsize(1300, 900)
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
logo_path = BASE_DIR.parent / "assets" / "Acc_logo.png"
photo = None
if os.path.exists(logo_path):
    image = Image.open(logo_path)
    image = image.resize((120, 80))
    photo = ImageTk.PhotoImage(image)

if photo:
    logo_label = ttkb.Label(header_frame, image=photo, bootstyle="light")
    logo_label.image = photo
    logo_label.pack(side="left", padx=(15, 20), pady=(20, 20))

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
form_container.pack(side="left", anchor="nw", padx=15, pady=(0, 8))

form_grid = ttkb.Frame(form_container)
form_grid.pack(anchor="nw", padx=20, pady=15)

field_vars = {}
field_rows = [
    ("Tag ID Storage", "tag_id"),
    ("Serial Number Storage", "serial"),
    ("TA Certification Storage", "cert"),
    ("GVW/GCW Storage", "gvw"),
    ("VIN Storage", "vin"),
    ("Registration No.", "registration"),
    ("Axle Count Storage", "axle"),
    ("Insurance Information", "insurance"),
]

for label_text, var_name in field_rows:

    ttkb.Label(form_grid, text=label_text, style="Field.TLabel").pack(
        anchor="w", pady=(0, 5)
    )

    var = tk.StringVar()
    field_vars[var_name] = var

    ttkb.Entry(form_grid, textvariable=var, width=50, bootstyle="info").pack(
        anchor="w", pady=(0, 8)
    )

    form_grid.pack(anchor="nw", padx=20, pady=10)

button_row = ttkb.Frame(form_container)
button_row.pack(fill="x", pady=(10, 0))


def TagDataForm():
    write_log("Starting RFID writing...")
    tag_id = field_vars["tag_id"].get()
    serial = field_vars["serial"].get()
    cert = field_vars["cert"].get()
    gvw = field_vars["gvw"].get()
    vin_store = field_vars["vin"].get()
    reg = field_vars["registration"].get()
    axle = field_vars["axle"].get()
    insurance = field_vars["insurance"].get()

    if all([tag_id, serial, cert, gvw, vin_store, reg, axle, insurance]):
        messagebox.showinfo("Status", "Data Submitted")
    else:
        messagebox.showinfo("Error", "Please fill all the fields")


submit_button = ttkb.Button(
    button_row, text="Submit", command=TagDataForm, bootstyle="success-outline"
)
submit_button.grid(row=8, column=1, padx=(225, 10), pady=(0, 40), sticky="e")


right_panel = ttkb.Frame(content_frame)
right_panel.pack(side="right", fill="both", expand=True, padx=(10, 10), pady=(0, 10))

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
controls_row = ttkb.Frame(controls_frame)
controls_row.pack(fill="x", expand=True)

# Make both columns expand equally
controls_row.columnconfigure(0, weight=1)
controls_row.columnconfigure(1, weight=1)

search_var = tk.StringVar()


def search():
    write_log(f"Searching VIN: {search_var.get()}")
    if not search_var.get():
        messagebox.showinfo("Search", "Enter a VIN to search")

# Left section (Search VIN)
search_frame = ttkb.Frame(controls_row)
search_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

search_label = ttkb.Label(search_frame, text="Search VIN No.", style="Section.TLabel")
search_label.pack(anchor="w")

search_box = ttkb.Frame(search_frame)
search_box.pack(fill="x", pady=(6, 0))

search_entry = ttkb.Entry(search_box, textvariable=search_var, bootstyle="info")
search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

search_button = ttkb.Button(search_box, text="🔍", command=search, bootstyle="info")
search_button.pack(side="right")

selected_option = tk.StringVar(value="Choose Medium")


def on_select(event):
    write_log(f"Selected medium: {selected_option.get()}", log_console)

    if selected_option.get() == "UART":
        reader.connect(PORT, BAUDRATE)

# Right section (Medium)
medium_frame = ttkb.Frame(controls_row)
medium_frame.grid(row=0, column=1, sticky="nsew")

medium_label = ttkb.Label(
    medium_frame,
    text="Select Data Transmit Medium",
    style="Section.TLabel",
)
medium_label.pack(anchor="w", padx=(0, 2), pady=(6, 6))

dropdown = ttkb.Combobox(
    medium_frame,
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
log_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

# --- Auto-save controls for log file ---
controls_subframe = ttkb.Frame(log_frame)
controls_subframe.pack(fill="x", pady=(0, 8))

auto_save_var = tk.BooleanVar(value=False)
log_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "activity.log"))

def browse_log_path():
    path = filedialog.asksaveasfilename(
        parent=root,
        title="Select log file",
        defaultextension=".log",
        filetypes=[("Log files", "*.log"), ("All files", "*")],
    )
    if path:
        log_path_var.set(path)
        try:
            log_console.set_file_path(path)
        except Exception:
            pass

def toggle_auto_save():
    enabled = bool(auto_save_var.get())
    log_console.enable_auto_save(enabled)
    write_log(f"Auto-save {'enabled' if enabled else 'disabled'}", log_console)

auto_save_cb = ttkb.Checkbutton(
    controls_subframe,
    text="Auto Save Logs",
    variable=auto_save_var,
    command=toggle_auto_save,
    bootstyle="info",
)
auto_save_cb.pack(side="left", padx=(0, 8))

log_path_entry = ttkb.Entry(controls_subframe, textvariable=log_path_var, width=40, bootstyle="info")
log_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

browse_btn = ttkb.Button(controls_subframe, text="Browse", command=browse_log_path, bootstyle="secondary")
browse_btn.pack(side="left")

log_console = LogConsole(log_frame)
log_console.set_file_path(log_path_var.get())
log_console.pack(fill="both", expand=True)

write_log("RFID Communicator started", log_console)


def update_gui():

    while True:
        data = reader.get_data()

        if data is None:
            break

        write_log(f"UART RX : {data}", log_console)

    root.after(100, update_gui)


def on_close():
    try:
        reader.stop()
    except Exception:
        pass

    try:
        root.destroy()
    except Exception:
        pass


def toggle_logging(event=None):
    global logging_enabled

    logging_enabled = not logging_enabled

    if logging_enabled:
        write_log("Logging Started", log_console)
    else:
        write_log("Logging Stopped", log_console)


root.bind("<space>", toggle_logging)


update_gui()

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
