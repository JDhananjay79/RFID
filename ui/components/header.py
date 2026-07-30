from pathlib import Path
from PIL import Image, ImageTk
import ttkbootstrap as ttkb


def build_header_frame(parent_frame, base_dir: Path) -> ttkb.Frame:
    """Build and return the application header frame with logo, title, and version label."""
    header_frame = ttkb.Frame(parent_frame)
    header_frame.pack(fill="x", pady=(0, 15), padx=15)

    logo_path = base_dir / "assets" / "Acc_logo.png"
    photo = None
    if logo_path.exists():
        try:
            image = Image.open(logo_path)
            image = image.resize((120, 80))
            photo = ImageTk.PhotoImage(image)
        except Exception:
            photo = None

    if photo:
        logo_label = ttkb.Label(header_frame, image=photo, bootstyle="light")
        logo_label.image = photo  # Keep reference
        logo_label.pack(side="left", padx=(0, 20), pady=(10, 10))

    header_text = ttkb.Label(
        header_frame,
        text="Event-Based Parameter Reader & Writer",
        style="Title.TLabel",
    )
    header_text.pack(side="left", pady=10)

    version_label = ttkb.Label(
        header_frame,
        text="Version: 1.0.0",
        style="Field.TLabel",
    )
    version_label.pack(side="right", pady=10)

    return header_frame
