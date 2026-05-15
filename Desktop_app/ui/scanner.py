import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import json
import threading
import time
import os

# ── Try importing QR scanner dependencies; skip gracefully if not installed ──
try:
    import cv2
    SCANNER_AVAILABLE = True
except ImportError as e:
    cv2 = None
    SCANNER_AVAILABLE = False
    print("OpenCV not found – camera scanning disabled")
    print(f"Error: {e}")

# Set decode to None initially - will be imported only when needed
decode = None

# ════════════════════════════════════════════════════════════════
#  THEME
# ════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Palette
BG_DEEP    = "#050E18"
BG_PANEL   = "#0A1929"
BG_CARD    = "#0D2137"
ACCENT     = "#00D4FF"
ACCENT2    = "#FF6B35"
GOLD       = "#FFD700"
TEXT_DIM   = "#4A7FA5"
TEXT_MID   = "#7FB3D3"
TEXT_LIGHT = "#C8E6F5"
TEXT_WHITE = "#E8F4FD"
SUCCESS    = "#00E5A0"
ERROR      = "#FF4D6D"
WARNING    = "#FFB830"
BORDER     = "#1A3A5C"

FONT_TITLE  = ("Trebuchet MS", 28, "bold")
FONT_HEAD   = ("Trebuchet MS", 15, "bold")
FONT_LABEL  = ("Trebuchet MS", 11)
FONT_LABEL_B= ("Trebuchet MS", 11, "bold")
FONT_BIG    = ("Trebuchet MS", 22, "bold")
FONT_SMALL  = ("Trebuchet MS", 9)
FONT_MONO   = ("Courier New",  11, "bold")


# ════════════════════════════════════════════════════════════════
#  HELPERS – reusable styled widgets
# ════════════════════════════════════════════════════════════════
def section_label(parent, text):
    """A small all-caps section header with an accent underline feel."""
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=24, pady=(14, 2))
    ctk.CTkLabel(f, text=text.upper(), font=FONT_SMALL,
                 text_color=ACCENT).pack(anchor="w")
    sep = ctk.CTkFrame(f, height=1, fg_color=ACCENT)
    sep.pack(fill="x", pady=(3, 0))
    return f


# ════════════════════════════════════════════════════════════════
#  QR SCANNER PAGE
# ════════════════════════════════════════════════════════════════
class ScannerPage(ctk.CTkFrame):

    def __init__(self, master, go_dashboard_callback=None):
        super().__init__(master)
        self.go_dashboard = go_dashboard_callback or (lambda: None)

        self.pack(fill="both", expand=True)
        self.configure(fg_color=BG_DEEP)

        # Scanner state
        self.scanning = False
        self.cap = None
        self.scan_thread = None

        self._build_topbar()
        self._build_body()

    # ── TOP BAR ─────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=68, fg_color=BG_PANEL, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Logo + brand
        logo_block = ctk.CTkFrame(bar, fg_color="transparent")
        logo_block.pack(side="left", padx=28)
        ctk.CTkLabel(logo_block, text="NTNC", font=("Trebuchet MS", 26, "bold"),
                     text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(logo_block, text=" · QR Scanner",
                     font=FONT_LABEL, text_color=TEXT_MID).pack(side="left")

        # Right side meta
        meta = ctk.CTkFrame(bar, fg_color="transparent")
        meta.pack(side="right", padx=28)
        ctk.CTkLabel(meta, text="🔍  Ticket Verification",
                     font=FONT_MONO, text_color=ACCENT2).pack(anchor="e")

    # ── BODY (scanner + results) ────────────────────────────────
    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        body.grid_columnconfigure(0, weight=2)   # left – scanner
        body.grid_columnconfigure(1, weight=1)   # right – results
        body.grid_rowconfigure(0, weight=1)

        self._build_scanner_panel(body)
        self._build_results_panel(body)

    # ── LEFT PANEL: Camera Scanner ──────────────────────────────
    def _build_scanner_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                             border_width=1, border_color=BORDER)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Header strip
        header = ctk.CTkFrame(panel, fg_color=BG_CARD, corner_radius=18, height=56)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="📷  QR Code Scanner", font=FONT_TITLE,
                     text_color=TEXT_WHITE).pack(side="left", padx=22, pady=8)

        # Camera display area
        camera_frame = ctk.CTkFrame(panel, fg_color="#000000", corner_radius=12)
        camera_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Camera placeholder / display
        if SCANNER_AVAILABLE:
            self.camera_label = ctk.CTkLabel(
                camera_frame,
                text="📷\n\nCamera Feed\n\nClick 'Start Scan' to begin",
                font=("Trebuchet MS", 16),
                text_color=TEXT_DIM
            )
        else:
            self.camera_label = ctk.CTkLabel(
                camera_frame,
                text="⚠️\n\nCamera Scanning Unavailable\n\nInstall dependencies to enable camera scanning\n\nUse 'Upload QR Image' instead",
                font=("Trebuchet MS", 14),
                text_color=WARNING
            )
        self.camera_label.pack(expand=True)

        # Control buttons
        controls = ctk.CTkFrame(panel, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(0, 20))

        self.scan_btn = ctk.CTkButton(
            controls,
            text="▶  Start Scan",
            height=44, corner_radius=14,
            font=FONT_LABEL_B,
            fg_color=ACCENT if SCANNER_AVAILABLE else BG_CARD, 
            hover_color="#00A8CC" if SCANNER_AVAILABLE else BG_CARD,
            text_color=BG_DEEP if SCANNER_AVAILABLE else TEXT_DIM,
            command=self.toggle_scan,
            state="normal" if SCANNER_AVAILABLE else "disabled"
        )
        self.scan_btn.pack(fill="x", pady=(0, 10))

        # Alternative: Upload QR image
        upload_btn = ctk.CTkButton(
            controls,
            text="📁  Upload QR Image",
            height=40, corner_radius=14,
            font=FONT_LABEL,
            fg_color="transparent", border_width=2, border_color=ACCENT,
            hover_color="#071220",
            text_color=ACCENT,
            command=self.upload_qr_image,
        )
        upload_btn.pack(fill="x")

    # ── RIGHT PANEL: Scan Results ───────────────────────────────
    def _build_results_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                             border_width=1, border_color=BORDER)
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Header
        header = ctk.CTkFrame(panel, fg_color=BG_CARD, corner_radius=18, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="📋  Scan Results", font=FONT_HEAD,
                     text_color=TEXT_WHITE).pack(side="left", padx=22)

        # Results display
        results_frame = ctk.CTkFrame(panel, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=20, pady=16)

        # Status indicator
        self.status_frame = ctk.CTkFrame(results_frame, fg_color=BG_CARD, corner_radius=12, height=60)
        self.status_frame.pack(fill="x", pady=(0, 16))
        self.status_frame.pack_propagate(False)

        self.status_icon = ctk.CTkLabel(self.status_frame, text="⏸", font=("Trebuchet MS", 24))
        self.status_icon.pack(side="left", padx=16)

        self.status_text = ctk.CTkLabel(
            self.status_frame,
            text="Ready to scan",
            font=FONT_LABEL_B,
            text_color=TEXT_MID
        )
        self.status_text.pack(side="left", padx=12)

        # Ticket details display
        details_container = ctk.CTkFrame(results_frame, fg_color="transparent")
        details_container.pack(fill="both", expand=True)

        # Scrollable details
        scroll = ctk.CTkScrollableFrame(details_container, fg_color="transparent",
                                        scrollbar_button_color=BORDER,
                                        scrollbar_button_hover_color=ACCENT)
        scroll.pack(fill="both", expand=True)

        # Ticket info fields
        self.ticket_info = {}

        info_fields = [
            ("Ticket ID", "—"),
            ("Booking Reference", "—"),
            ("Visitor Name", "—"),
            ("Country", "—"),
            ("Destination", "—"),
            ("Visit Date", "—"),
            ("Ticket Type", "—"),
            ("Visitors", "—"),
            ("Total Price", "—"),
            ("Payment Method", "—"),
            ("Created At", "—"),
        ]

        for label, default in info_fields:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row, text=label + ":", font=FONT_LABEL_B,
                         text_color=TEXT_MID, width=120, anchor="w").pack(side="left")

            value_label = ctk.CTkLabel(row, text=default, font=FONT_LABEL,
                                       text_color=TEXT_LIGHT, anchor="w")
            value_label.pack(side="left", fill="x", expand=True)

            self.ticket_info[label.lower().replace(" ", "_")] = value_label

        # Action buttons
        actions = ctk.CTkFrame(results_frame, fg_color="transparent")
        actions.pack(fill="x", pady=(16, 0))

        validate_btn = ctk.CTkButton(
            actions,
            text="✓  Validate Ticket",
            height=40, corner_radius=14,
            font=FONT_LABEL_B,
            fg_color=SUCCESS, hover_color="#00A844",
            text_color=BG_DEEP,
            command=self.validate_ticket,
            state="disabled"
        )
        validate_btn.pack(fill="x", pady=(0, 8))
        self.validate_btn = validate_btn

        back_btn = ctk.CTkButton(
            actions,
            text="← Back to Dashboard",
            height=38, corner_radius=14,
            font=FONT_LABEL,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color="#071220",
            text_color=TEXT_DIM,
            command=self.go_dashboard,
        )
        back_btn.pack(fill="x")

    # ════════════════════════════════════════════════════════════
    #  SCANNER LOGIC
    # ════════════════════════════════════════════════════════════
    def toggle_scan(self):
        """Start or stop QR scanning."""
        if not SCANNER_AVAILABLE:
            messagebox.showerror("Scanner Unavailable", 
                               "QR scanner dependencies not installed.\n\n"
                               "Please install: pip install opencv-python pyzbar\n\n"
                               "You can still upload QR images manually.")
            return

        if self.scanning:
            self.stop_scan()
        else:
            self.start_scan()

    def start_scan(self):
        """Begin QR code scanning."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Camera Error", "Could not access camera. Please check camera permissions.")
                return

            self.scanning = True
            self.scan_btn.configure(text="⏹  Stop Scan", fg_color=ERROR, hover_color="#CC3344")
            self.status_icon.configure(text="🔍", text_color=ACCENT)
            self.status_text.configure(text="Scanning for QR codes...", text_color=ACCENT)

            # Start scanning thread
            self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.scan_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scanner: {str(e)}")

    def stop_scan(self):
        """Stop QR code scanning."""
        self.scanning = False
        if self.cap:
            self.cap.release()
        self.cap = None

        self.scan_btn.configure(text="▶  Start Scan", fg_color=ACCENT, hover_color="#00A8CC")
        self.status_icon.configure(text="⏸", text_color=TEXT_DIM)
        self.status_text.configure(text="Scan stopped", text_color=TEXT_DIM)

        # Reset camera display
        self.camera_label.configure(text="📷\n\nCamera Feed\n\nClick 'Start Scan' to begin")

    def _scan_loop(self):
        """Main scanning loop running in background thread."""
        global decode
        
        # Try to import pyzbar only when needed
        if decode is None:
            try:
                from pyzbar.pyzbar import decode
            except ImportError:
                self.after(0, lambda: messagebox.showerror("Scanner Unavailable", 
                                   "pyzbar not installed.\n\n"
                                   "Please install: pip install pyzbar"))
                self.after(0, self.stop_scan)
                return
        
        while self.scanning and self.cap:
            try:
                success, frame = self.cap.read()
                if not success:
                    continue

                # Decode QR codes
                decoded_objects = decode(frame)

                for obj in decoded_objects:
                    qr_data = obj.data.decode("utf-8")
                    self._process_qr_data(qr_data)
                    # Stop scanning after successful read
                    self.after(0, self.stop_scan)
                    return

                # Update camera display (simplified - just show scanning status)
                self.after(0, lambda: self.camera_label.configure(
                    text="📷\n\nScanning...\n\nPoint camera at QR code"
                ))

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

            except Exception as e:
                print(f"Scan error: {e}")
                break

    def upload_qr_image(self):
        """Upload and scan QR code from image file."""
        global decode
        
        if not SCANNER_AVAILABLE:
            messagebox.showerror("Scanner Unavailable", 
                               "OpenCV not installed.\n\n"
                               "Please install: pip install opencv-python")
            return

        # Try to import pyzbar only when needed
        if decode is None:
            try:
                from pyzbar.pyzbar import decode
            except ImportError:
                messagebox.showerror("Scanner Unavailable", 
                                   "pyzbar not installed.\n\n"
                                   "Please install: pip install pyzbar")
                return

        file_path = filedialog.askopenfilename(
            title="Select QR Code Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        if not file_path:
            return

        try:
            # Read image
            image = cv2.imread(file_path)
            if image is None:
                messagebox.showerror("Error", "Could not read image file.")
                return

            # Decode QR codes
            decoded_objects = decode(image)

            if not decoded_objects:
                messagebox.showwarning("No QR Code", "No QR code found in the selected image.")
                return

            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")
                self._process_qr_data(qr_data)
                break  # Process only first QR code

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")

    def _process_qr_data(self, qr_data):
        """Process decoded QR data and display ticket information."""
        try:
            # Parse JSON data
            ticket_data = json.loads(qr_data)

            # Update status
            self.status_icon.configure(text="✅", text_color=SUCCESS)
            self.status_text.configure(text="Ticket scanned successfully!", text_color=SUCCESS)

            # Update ticket information display
            field_mapping = {
                "ticket_id": "Ticket ID",
                "booking_ref": "Booking Reference",
                "name": "Visitor Name",
                "country": "Country",
                "destination": "Destination",
                "visit_date": "Visit Date",
                "ticket_type": "Ticket Type",
                "visitors": "Visitors",
                "total_price": "Total Price",
                "payment": "Payment Method",
                "created_at": "Created At",
            }

            for field_key, display_name in field_mapping.items():
                if field_key in ticket_data:
                    value = ticket_data[field_key]
                    if field_key == "total_price":
                        value = f"NPR {value:,}"
                    elif field_key == "destination" and "  " in str(value):
                        value = str(value).split("  ")[-1]
                    elif field_key == "payment" and "  " in str(value):
                        value = str(value).split("  ")[-1]

                    self.ticket_info[display_name.lower().replace(" ", "_")].configure(
                        text=str(value), text_color=TEXT_WHITE
                    )

            # Enable validation button
            self.validate_btn.configure(state="normal")

            # Store ticket data for validation
            self.current_ticket_data = ticket_data

        except json.JSONDecodeError:
            self.status_icon.configure(text="❌", text_color=ERROR)
            self.status_text.configure(text="Invalid QR code format", text_color=ERROR)
            messagebox.showerror("Invalid QR", "The scanned QR code does not contain valid ticket data.")

        except Exception as e:
            self.status_icon.configure(text="❌", text_color=ERROR)
            self.status_text.configure(text=f"Error processing QR: {str(e)}", text_color=ERROR)

    def validate_ticket(self):
        """Validate the scanned ticket."""
        if not hasattr(self, 'current_ticket_data'):
            return

        # Basic validation - check if ticket has required fields
        required_fields = ['ticket_id', 'name', 'destination', 'visit_date']
        missing_fields = [field for field in required_fields if field not in self.current_ticket_data]

        if missing_fields:
            messagebox.showerror("Invalid Ticket", f"Missing required fields: {', '.join(missing_fields)}")
            return

        # Check if visit date is in the future or today
        try:
            visit_date = datetime.strptime(self.current_ticket_data['visit_date'], "%Y-%m-%d")
            today = datetime.now().date()

            if visit_date.date() < today:
                messagebox.showwarning("Expired Ticket", "This ticket is for a past date and may be expired.")
            else:
                messagebox.showinfo("Valid Ticket", "✅ Ticket is valid and ready for use!")
        except:
            messagebox.showinfo("Valid Ticket", "✅ Ticket appears to be valid!")

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_scan()


# ════════════════════════════════════════════════════════════════
#  STANDALONE RUNNER
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("NTNC – QR Scanner")
    app.geometry("1400x800")
    app.minsize(1200, 700)
    ScannerPage(app, go_dashboard_callback=app.destroy)
    app.mainloop()