import customtkinter as ctk
from tkinter import messagebox
import uuid
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

# ── Try importing QR generator; skip gracefully if not installed ──
try:
    from qr.generate_qr import generate_qr
except ImportError:
    def generate_qr(data):
        print("QR generator not found – skipping:", data)

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


def form_entry(parent, placeholder, width=310):
    e = ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        width=width,
        height=40,
        corner_radius=10,
        border_color=BORDER,
        fg_color="#071220",
        text_color=TEXT_WHITE,
        placeholder_text_color=TEXT_DIM,
        font=FONT_LABEL,
    )
    e.pack(padx=24, pady=5, anchor="w")
    return e


def form_option(parent, values, width=310):
    m = ctk.CTkOptionMenu(
        parent,
        values=values,
        width=width,
        height=40,
        corner_radius=10,
        fg_color="#071220",
        button_color=BG_CARD,
        button_hover_color=ACCENT,
        dropdown_fg_color=BG_CARD,
        dropdown_hover_color="#1A4A6E",
        text_color=TEXT_LIGHT,
        dropdown_text_color=TEXT_LIGHT,
        font=FONT_LABEL,
    )
    m.pack(padx=24, pady=5, anchor="w")
    return m


# ════════════════════════════════════════════════════════════════
#  TICKET PAGE
# ════════════════════════════════════════════════════════════════
class TicketPage(ctk.CTkFrame):

    PRICE_MAP = {
        "Normal Ticket": 500,
        "VIP Ticket":    1500,
        "Group Ticket":  300,
    }

    DESTINATIONS = [
        "Mustang",
        "Annapurna Base Camp",
        "Lake Rara",
        "Sagarmatha (Everest) National Park",
    ]

    def __init__(self, master, go_dashboard_callback=None):
        super().__init__(master)
        self.go_dashboard = go_dashboard_callback or (lambda: None)

        self.pack(fill="both", expand=True)
        self.configure(fg_color=BG_DEEP)

        # ── Auto-generated IDs ──────────────────────────────────
        self.ticket_id   = "TKT-" + str(random.randint(10000, 99999))
        self.booking_ref = "BR-"  + uuid.uuid4().hex[:8].upper()

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
        ctk.CTkLabel(logo_block, text=" · Tourist Ticketing System",
                     font=FONT_LABEL, text_color=TEXT_MID).pack(side="left")

        # Right side meta
        meta = ctk.CTkFrame(bar, fg_color="transparent")
        meta.pack(side="right", padx=28)
        ctk.CTkLabel(meta, text=f"Ticket ID  {self.ticket_id}",
                     font=FONT_MONO, text_color=ACCENT2).pack(anchor="e")
        ctk.CTkLabel(meta, text=f"Ref        {self.booking_ref}",
                     font=FONT_MONO, text_color=TEXT_DIM).pack(anchor="e")

    # ── BODY (two horizontal panels) ────────────────────────────
    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        body.grid_columnconfigure(0, weight=3)   # left – form
        body.grid_columnconfigure(1, weight=2)   # right – summary
        body.grid_rowconfigure(0, weight=1)

        self._build_left_panel(body)
        self._build_right_panel(body)

    # ── LEFT PANEL: Form ─────────────────────────────────────────
    def _build_left_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                             border_width=1, border_color=BORDER)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Header strip
        header = ctk.CTkFrame(panel, fg_color=BG_CARD, corner_radius=18, height=56)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="✦  Create Tourist Ticket", font=FONT_TITLE,
                     text_color=TEXT_WHITE).pack(side="left", padx=22, pady=8)

        # Scrollable inner area
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent",
                                        scrollbar_button_color=BORDER,
                                        scrollbar_button_hover_color=ACCENT)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # ── VISITOR INFO ────────────────────────────────────────
        section_label(scroll, "Visitor Information")

        self.name    = form_entry(scroll, "Full Name")
        self.country = form_entry(scroll, "Country / Nationality")

        ctk.CTkLabel(scroll, text="Number of Visitors", font=FONT_LABEL_B,
                     text_color=TEXT_MID).pack(anchor="w", padx=24, pady=(6, 0))
        self.visitors = form_option(scroll, ["1", "2", "3", "4", "5"])
        self.visitors.set("1")

        # ── DESTINATION ─────────────────────────────────────────
        section_label(scroll, "Destination")

        ctk.CTkLabel(scroll, text="Select Site", font=FONT_LABEL_B,
                     text_color=TEXT_MID).pack(anchor="w", padx=24, pady=(6, 0))
        self.destination = form_option(scroll, self.DESTINATIONS)
        self.destination.set(self.DESTINATIONS[0])

        ctk.CTkLabel(scroll, text="Visit Date", font=FONT_LABEL_B,
                     text_color=TEXT_MID).pack(anchor="w", padx=24, pady=(6, 0))
        self.visit_date = form_entry(scroll, "YYYY-MM-DD")
        # Prefill today
        self.visit_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # ── TICKET TYPE ──────────────────────────────────────────
        section_label(scroll, "Ticket & Payment")

        # Ticket-type radio-style buttons
        self.ticket_type_var = ctk.StringVar(value="Normal Ticket")
        type_row = ctk.CTkFrame(scroll, fg_color="transparent")
        type_row.pack(fill="x", padx=24, pady=6)
        for ttype, price in self.PRICE_MAP.items():
            b = ctk.CTkRadioButton(
                type_row, text=f"{ttype}\nNPR {price}",
                variable=self.ticket_type_var, value=ttype,
                command=self.update_price,
                font=FONT_LABEL, text_color=TEXT_LIGHT,
                radiobutton_width=18, radiobutton_height=18,
                fg_color=ACCENT, border_color=BORDER,
            )
            b.pack(side="left", expand=True)

        ctk.CTkLabel(scroll, text="Payment Method", font=FONT_LABEL_B,
                     text_color=TEXT_MID).pack(anchor="w", padx=24, pady=(10, 0))
        self.payment_method = form_option(scroll, ["💵  Cash", "💳  Card",
                                                    "📱  eSewa", "📱  Khalti"])
        self.payment_method.set("💵  Cash")

        ctk.CTkLabel(scroll, text="Discount Code / %", font=FONT_LABEL_B,
                     text_color=TEXT_MID).pack(anchor="w", padx=24, pady=(6, 0))
        self.discount = form_entry(scroll, "0 – 100  (optional)")
        self.discount.bind("<KeyRelease>", lambda e: self.update_price())

        # ── SPECIAL REQUESTS / NOTES ────────────────────────────
        section_label(scroll, "Additional Notes")

        ctk.CTkLabel(scroll, text="Special Requests or Comments", font=FONT_LABEL_B,
                     text_color=TEXT_MID).pack(anchor="w", padx=24, pady=(6, 0))

        # Text area with enhanced styling
        self.notes = ctk.CTkTextbox(
            scroll,
            width=290,
            height=100,
            corner_radius=12,
            border_width=2,
            border_color=BORDER,
            fg_color="#071220",
            text_color=TEXT_WHITE,
            font=("Trebuchet MS", 13),
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT,
        )
        self.notes.pack(padx=24, pady=8)

        # Add placeholder-like behavior and hover effects
        self._setup_textarea_hover()

        # Visitors change → re-price
        self.visitors.configure(command=lambda v: self.update_price())

        # Bottom padding
        ctk.CTkFrame(scroll, fg_color="transparent", height=12).pack()

    # ── RIGHT PANEL: Summary + Actions ──────────────────────────
    def _build_right_panel(self, parent):
        panel = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=20,
                             border_width=1, border_color=BORDER)
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # ── Decorative top gradient band ────────────────────────
        band = ctk.CTkFrame(panel, fg_color=BG_CARD, corner_radius=18, height=56)
        band.pack(fill="x")
        band.pack_propagate(False)
        ctk.CTkLabel(band, text="📋  Booking Summary", font=FONT_HEAD,
                     text_color=TEXT_WHITE).pack(side="left", padx=22)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Ticket visual card ────────────────────────────────
        card = ctk.CTkFrame(inner, fg_color=BG_CARD, corner_radius=18,
                            border_width=2, border_color=ACCENT)
        card.pack(fill="x", pady=(0, 16))

        # Coloured top stripe
        stripe = ctk.CTkFrame(card, height=8, fg_color=ACCENT, corner_radius=18)
        stripe.pack(fill="x")

        ctk.CTkLabel(card, text="✈  NTNC  TICKET", font=("Courier New", 13, "bold"),
                     text_color=ACCENT).pack(pady=(10, 2))

        self.sum_id  = ctk.CTkLabel(card, text=f"ID  {self.ticket_id}",
                                    font=FONT_MONO, text_color=TEXT_MID)
        self.sum_id.pack()
        self.sum_ref = ctk.CTkLabel(card, text=f"REF  {self.booking_ref}",
                                    font=FONT_MONO, text_color=TEXT_DIM)
        self.sum_ref.pack(pady=(0, 10))

        # Dashed divider
        ctk.CTkLabel(card,
                     text="- - - - - - - - - - - - - - - - - - - - - -",
                     font=("Courier New", 9), text_color=BORDER).pack()

        # Summary rows
        self.sum_rows_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.sum_rows_frame.pack(fill="x", padx=18, pady=10)

        self._sum_labels = {}
        for key in ["Name", "Country", "Visitors", "Destination",
                    "Type", "Date", "Payment"]:
            row = ctk.CTkFrame(self.sum_rows_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=key, font=FONT_SMALL,
                         text_color=TEXT_DIM, width=80, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(row, text="—", font=FONT_LABEL,
                               text_color=TEXT_LIGHT, anchor="w")
            lbl.pack(side="left")
            self._sum_labels[key] = lbl

        # Dashed divider
        ctk.CTkLabel(card,
                     text="- - - - - - - - - - - - - - - - - - - - - -",
                     font=("Courier New", 9), text_color=BORDER).pack()

        # Price
        price_row = ctk.CTkFrame(card, fg_color="transparent")
        price_row.pack(fill="x", padx=18, pady=(8, 14))
        ctk.CTkLabel(price_row, text="TOTAL", font=FONT_LABEL_B,
                     text_color=ACCENT2).pack(side="left")
        self.price_label = ctk.CTkLabel(price_row, text="NPR 0",
                                        font=FONT_BIG, text_color=GOLD)
        self.price_label.pack(side="right")

        # Bottom accent stripe
        ctk.CTkFrame(card, height=6, fg_color=ACCENT2, corner_radius=18).pack(fill="x")

        # ── Stats row ──────────────────────────────────────────
        stats = ctk.CTkFrame(inner, fg_color=BG_CARD, corner_radius=14)
        stats.pack(fill="x", pady=(0, 16))
        stats.grid_columnconfigure((0, 1, 2), weight=1)

        stat_data = [("🏷", "Ticket Type", "Normal"), ("👥", "Visitors", "1"),
                     ("💰", "Discount", "0 %")]
        self.stat_widgets = {}
        for i, (icon, label, val) in enumerate(stat_data):
            f = ctk.CTkFrame(stats, fg_color="transparent")
            f.grid(row=0, column=i, padx=10, pady=10)
            ctk.CTkLabel(f, text=icon, font=("", 22)).pack()
            ctk.CTkLabel(f, text=label, font=FONT_SMALL,
                         text_color=TEXT_DIM).pack()
            lbl = ctk.CTkLabel(f, text=val, font=FONT_LABEL_B,
                               text_color=TEXT_WHITE)
            lbl.pack()
            self.stat_widgets[label] = lbl

        # ── Buttons ────────────────────────────────────────────
        btn_generate = ctk.CTkButton(
            inner,
            text="⚡  Generate Ticket + QR",
            height=50, corner_radius=14,
            font=("Trebuchet MS", 14, "bold"),
            fg_color=ACCENT, hover_color="#00A8CC",
            text_color=BG_DEEP,
            command=self.create_ticket,
        )
        btn_generate.pack(fill="x", pady=(0, 10))

        btn_preview = ctk.CTkButton(
            inner,
            text="👁  Preview Summary",
            height=44, corner_radius=14,
            font=FONT_LABEL_B,
            fg_color="transparent", border_width=2, border_color=ACCENT,
            hover_color="#071220",
            text_color=ACCENT,
            command=self.refresh_summary,
        )
        btn_preview.pack(fill="x", pady=(0, 10))

        # Status
        self.status_label = ctk.CTkLabel(inner, text="", font=FONT_SMALL,
                                         text_color=SUCCESS)
        self.status_label.pack(pady=8)

        # Footer row with explicit confirm/cancel actions
        footer = ctk.CTkFrame(inner, fg_color="transparent")
        footer.pack(fill="x", pady=(10, 10), side="bottom")

        btn_cancel = ctk.CTkButton(
            footer,
            text="✖ Cancel",
            height=40, corner_radius=14,
            font=FONT_LABEL,
            fg_color="#1A1E29", hover_color="#161B24",
            text_color=TEXT_DIM,
            border_width=1, border_color=BORDER,
            command=self.go_dashboard,
        )
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 6))

        btn_confirm = ctk.CTkButton(
            footer,
            text="🖨 Confirm & Print",
            height=40, corner_radius=14,
            font=FONT_LABEL_B,
            fg_color="#1A4A6E", hover_color="#0D7A99",
            text_color=TEXT_WHITE,
            command=self.print_ticket,
        )
        btn_confirm.pack(side="right", expand=True, fill="x", padx=(6, 0))

        # Init price
        self.update_price()

    # ════════════════════════════════════════════════════════════
    #  LOGIC
    # ════════════════════════════════════════════════════════════
    def _setup_textarea_hover(self):
        """Add hover effects to the notes text area."""
        def on_enter(event):
            self.notes.configure(border_color=ACCENT)

        def on_leave(event):
            self.notes.configure(border_color=BORDER)

        self.notes.bind("<Enter>", on_enter)
        self.notes.bind("<Leave>", on_leave)

    def update_price(self, *_):
        ttype   = self.ticket_type_var.get()
        base    = self.PRICE_MAP.get(ttype, 0)
        qty     = int(self.visitors.get())
        total   = base * qty
        disc_str = self.discount.get().strip()
        disc_pct = 0
        if disc_str.isdigit():
            disc_pct = min(int(disc_str), 100)
            total -= total * disc_pct / 100
        self.total_price = int(total)
        self.price_label.configure(text=f"NPR {self.total_price:,}")

        # Update stat widgets
        self.stat_widgets["Ticket Type"].configure(text=ttype.split()[0])
        self.stat_widgets["Visitors"].configure(text=str(qty))
        self.stat_widgets["Discount"].configure(text=f"{disc_pct} %")

    def refresh_summary(self):
        """Push current form values into the right-panel summary card."""
        self.update_price()
        dest_raw = self.destination.get()
        pay_raw  = self.payment_method.get()

        updates = {
            "Name":        self.name.get() or "—",
            "Country":     self.country.get() or "—",
            "Visitors":    self.visitors.get(),
            "Destination": dest_raw.split("  ")[-1] if "  " in dest_raw else dest_raw,
            "Type":        self.ticket_type_var.get(),
            "Date":        self.visit_date.get() or "—",
            "Payment":     pay_raw.split("  ")[-1] if "  " in pay_raw else pay_raw,
        }
        for key, val in updates.items():
            self._sum_labels[key].configure(text=val)

        self.status_label.configure(text="✓ Summary refreshed", text_color=SUCCESS)

    def create_ticket(self):
        name    = self.name.get().strip()
        country = self.country.get().strip()

        if not name or not country:
            messagebox.showerror("Missing Info",
                                 "Please enter Full Name and Country before generating.")
            return

        self.refresh_summary()

        data = {
            "ticket_id":   self.ticket_id,
            "booking_ref": self.booking_ref,
            "name":        name,
            "country":     country,
            "visitors":    self.visitors.get(),
            "destination": self.destination.get(),
            "ticket_type": self.ticket_type_var.get(),
            "visit_date":  self.visit_date.get(),
            "payment":     self.payment_method.get(),
            "total_price": self.total_price,
            "notes":       self.notes.get("1.0", "end").strip(),
            "created_at":  str(datetime.now()),
        }

        generate_qr(data)

        self.status_label.configure(
            text=f"✦ Ticket #{self.ticket_id} generated!", text_color=SUCCESS)
        messagebox.showinfo("Success ✔",
                            f"Ticket Created Successfully!\n\n"
                            f"ID : {self.ticket_id}\n"
                            f"Ref: {self.booking_ref}\n"
                            f"Total: NPR {self.total_price:,}")

    def print_ticket(self):
        """Confirmed print: generates QR + creates printable ticket with QR and sends to printer."""
        name    = self.name.get().strip()
        country = self.country.get().strip()

        if not name or not country:
            messagebox.showerror("Missing Info",
                                 "Please enter Full Name and Country before printing.")
            return

        # Ensure totals are up-to-date
        self.refresh_summary()

        data = {
            "ticket_id":   self.ticket_id,
            "booking_ref": self.booking_ref,
            "name":        name,
            "country":     country,
            "visitors":    self.visitors.get(),
            "destination": self.destination.get(),
            "ticket_type": self.ticket_type_var.get(),
            "visit_date":  self.visit_date.get(),
            "payment":     self.payment_method.get(),
            "total_price": self.total_price,
            "notes":       self.notes.get("1.0", "end").strip(),
            "created_at":  str(datetime.now()),
        }

        # Generate QR image used by the printable document
        generate_qr(data)

        # Create printable ticket image (embeds QR from ticket_qr.png)
        self._create_print_document(data)

        self.status_label.configure(
            text="✓ Ticket sent to printer", text_color=SUCCESS)
        messagebox.showinfo(
            "Print ✔",
            f"Ticket and QR code sent to printer!\n\nTicket ID: {self.ticket_id}")

    def _create_print_document(self, data):
        """Create and print a formatted ticket with QR code."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            messagebox.showerror("Error", "PIL library not found. Please install pillow.")
            return

        # Create a larger image for printing (A6 size in pixels at 300 DPI)
        img_width, img_height = 600, 800
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)

        try:
            # Try to use better fonts
            title_font = ImageFont.truetype("arial.ttf", 24)
            header_font = ImageFont.truetype("arial.ttf", 14)
            normal_font = ImageFont.truetype("arial.ttf", 12)
            small_font = ImageFont.truetype("arial.ttf", 10)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        y_pos = 30

        # Header
        draw.text((img_width // 2, y_pos), "NTNC TOURIST TICKET",
                  font=title_font, fill='black', anchor='mm')
        y_pos += 50

        # Divider line
        draw.line([(30, y_pos), (img_width - 30, y_pos)], fill='black', width=2)
        y_pos += 15

        # Ticket details
        details = [
            ("Ticket ID:", data['ticket_id']),
            ("Booking Ref:", data['booking_ref']),
            ("Name:", data['name']),
            ("Country:", data['country']),
            ("Destination:", data['destination'].split("  ")[-1] if "  " in data['destination'] else data['destination']),
            ("Visit Date:", data['visit_date']),
            ("Visitors:", data['visitors']),
            ("Ticket Type:", data['ticket_type']),
            ("Payment Method:", data['payment'].split("  ")[-1] if "  " in data['payment'] else data['payment']),
            ("Total Price:", f"NPR {data['total_price']:,}"),
        ]

        for label, value in details:
            draw.text((40, y_pos), label, font=header_font, fill='black')
            draw.text((250, y_pos), str(value), font=normal_font, fill='#333333')
            y_pos += 30

        # Another divider
        y_pos += 10
        draw.line([(30, y_pos), (img_width - 30, y_pos)], fill='black', width=2)
        y_pos += 20

        # Add QR code if it exists
        qr_path = os.path.join(os.getcwd(), "ticket_qr.png")
        if os.path.exists(qr_path):
            try:
                qr_img = Image.open(qr_path)
                qr_size = 200
                qr_img = qr_img.resize((qr_size, qr_size))
                qr_x = (img_width - qr_size) // 2
                img.paste(qr_img, (qr_x, y_pos))
                y_pos += qr_size + 20
            except Exception as e:
                print(f"Error adding QR code: {e}")

        # Footer
        draw.line([(30, y_pos), (img_width - 30, y_pos)], fill='black', width=1)
        y_pos += 10
        draw.text((img_width // 2, y_pos),
                  f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                  font=small_font, fill='#666666', anchor='mm')

        # Save the ticket image
        ticket_path = os.path.join(os.getcwd(), f"ticket_{data['ticket_id']}.png")
        img.save(ticket_path)

        # Print the ticket (Windows)
        try:
            if os.name == 'nt':  # Windows
                os.startfile(ticket_path, "print")
            else:  # Linux/Mac
                subprocess.run(['lp', ticket_path])
        except Exception:
            messagebox.showinfo(
                "Print Ready",
                f"Ticket saved to: {ticket_path}\n\n"
                f"Please print manually from your printer.")


# ════════════════════════════════════════════════════════════════
#  STANDALONE RUNNER
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("NTNC – Tourist Ticketing System")
    app.geometry("1180x740")
    app.minsize(960, 660)
    TicketPage(app, go_dashboard_callback=app.destroy)
    app.mainloop()

