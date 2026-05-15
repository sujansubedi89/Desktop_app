import customtkinter as ctk
import tkinter as tk
from datetime import datetime
import random
import math

# ════════════════════════════════════════════════════════════════
#  THEME CONSTANTS
# ════════════════════════════════════════════════════════════════
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_VOID    = "#030B12"
BG_DEEP    = "#060F1A"
BG_PANEL   = "#0A1929"
BG_CARD    = "#0C2235"
BG_CARD2   = "#0E2A40"
ACCENT     = "#00D4FF"
ACCENT_DIM = "#007A99"
GREEN      = "#00E5A0"
GREEN_DIM  = "#007A55"
AMBER      = "#FFB830"
AMBER_DIM  = "#8A6200"
RED        = "#FF4D6D"
RED_DIM    = "#8A1A2E"
TEAL       = "#00F5D4"
BORDER     = "#132E47"
BORDER2    = "#1A3F5C"
TEXT_WHITE = "#E8F4FD"
TEXT_LIGHT = "#B0D4EC"
TEXT_MID   = "#5A8FAD"
TEXT_DIM   = "#2E5A78"
SIDEBAR_W  = "#061420"

FNT_LOGO   = ("Georgia", 32, "bold")
FNT_BIG    = ("Georgia", 42, "bold")
FNT_HEAD   = ("Trebuchet MS", 14, "bold")
FNT_LABEL  = ("Trebuchet MS", 11)
FNT_LABEL_B= ("Trebuchet MS", 11, "bold")
FNT_SMALL  = ("Trebuchet MS", 9)
FNT_MONO   = ("Courier New",  12, "bold")
FNT_MONO_S = ("Courier New",  10)
FNT_TICK   = ("Trebuchet MS", 10)


# ════════════════════════════════════════════════════════════════
#  HELPER: Lighten hex color
# ════════════════════════════════════════════════════════════════
def hex_to_lighter(hex_color, factor=0.3):
    """Convert hex color to a lighter shade for transparency effect."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f'#{r:02x}{g:02x}{b:02x}'


# ════════════════════════════════════════════════════════════════
#  ANIMATED STAT CARD
# ════════════════════════════════════════════════════════════════
class StatCard(ctk.CTkFrame):
    """Card that counts up to its value on first render."""

    def __init__(self, parent, icon, title, target_value, unit,
                 accent_color, trend=None, **kwargs):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=18,
                         border_width=1, border_color=BORDER2, **kwargs)
        self._target = target_value
        self._current = 0
        self._unit = unit
        self._accent = accent_color

        # Top colour bar
        bar = ctk.CTkFrame(self, height=4, fg_color=accent_color, corner_radius=18)
        bar.pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)

        # Icon + title row
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=icon, font=("", 20)).pack(side="left")
        ctk.CTkLabel(top, text=title, font=FNT_LABEL,
                     text_color=TEXT_MID).pack(side="left", padx=8)

        # Trend badge
        if trend:
            arrow = "▲" if trend > 0 else "▼"
            col   = GREEN if trend > 0 else RED
            ctk.CTkLabel(top, text=f"{arrow} {abs(trend)}%",
                         font=FNT_SMALL, text_color=col).pack(side="right")

        # Big number
        self._val_lbl = ctk.CTkLabel(body, text="0",
                                     font=FNT_BIG, text_color=accent_color)
        self._val_lbl.pack(anchor="w", pady=(4, 0))

        # Unit sub-label
        ctk.CTkLabel(body, text=unit, font=FNT_SMALL,
                     text_color=TEXT_DIM).pack(anchor="w")

        # Sparkline canvas
        self._spark = tk.Canvas(body, height=28, bg=BG_CARD,
                                highlightthickness=0)
        self._spark.pack(fill="x", pady=(6, 0))
        self._spark_data = [random.randint(20, 100) for _ in range(18)]
        self.after(120, self._draw_spark)

        # Start count-up
        self.after(200, self._count_up)

    def _count_up(self):
        step = max(1, self._target // 40)
        self._current = min(self._current + step, self._target)
        self._val_lbl.configure(text=f"{self._current:,}")
        if self._current < self._target:
            self.after(28, self._count_up)
        else:
            self._val_lbl.configure(text=f"{self._target:,}")

    def _draw_spark(self):
        c = self._spark
        c.update_idletasks()
        w, h = c.winfo_width(), c.winfo_height()
        if w < 2:
            self.after(100, self._draw_spark)
            return
        c.delete("all")
        data = self._spark_data
        mn, mx = min(data), max(data)
        rng = mx - mn or 1
        pts = [(i * w / (len(data)-1),
                h - (d - mn) / rng * (h - 4) - 2)
               for i, d in enumerate(data)]
        # Fill polygon
        poly = [0, h] + [x for p in pts for x in p] + [w, h]
        c.create_polygon(poly, fill=hex_to_lighter(self._accent), outline="")
        # Line
        flat = [x for p in pts for x in p]
        c.create_line(flat, fill=self._accent, width=1.5, smooth=True)


# ════════════════════════════════════════════════════════════════
#  LIVE ACTIVITY FEED ROW
# ════════════════════════════════════════════════════════════════
class ActivityRow(ctk.CTkFrame):
    def __init__(self, parent, icon, text, timestamp, color, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self.pack(fill="x", padx=18, pady=3)

        dot = ctk.CTkFrame(self, width=10, height=10,
                           fg_color=color, corner_radius=5)
        dot.pack(side="left", padx=(0, 12))
        dot.pack_propagate(False)

        ctk.CTkLabel(self, text=icon + "  " + text,
                     font=FNT_LABEL, text_color=TEXT_LIGHT,
                     anchor="w").pack(side="left", expand=True, fill="x")

        ctk.CTkLabel(self, text=timestamp, font=FNT_MONO_S,
                     text_color=TEXT_DIM).pack(side="right")


# ════════════════════════════════════════════════════════════════
#  MINI PROGRESS BAR
# ════════════════════════════════════════════════════════════════
class MiniProgress(ctk.CTkFrame):
    def __init__(self, parent, label, pct, color, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text=label, font=FNT_LABEL,
                     text_color=TEXT_LIGHT).pack(side="left")
        ctk.CTkLabel(row, text=f"{pct}%", font=FNT_SMALL,
                     text_color=color).pack(side="right")
        bar_bg = ctk.CTkFrame(self, height=6, fg_color=BORDER, corner_radius=4)
        bar_bg.pack(fill="x", pady=(3, 0))
        fill_w = max(1, int(pct / 100 * 280))
        ctk.CTkFrame(bar_bg, height=6, width=fill_w,
                     fg_color=color, corner_radius=4).place(x=0, y=0)


# ════════════════════════════════════════════════════════════════
#  CHECKPOINT STATUS BADGE
# ════════════════════════════════════════════════════════════════
class CheckpointBadge(ctk.CTkFrame):
    def __init__(self, parent, name, status, count, **kw):
        super().__init__(parent, fg_color=BG_CARD2,
                         corner_radius=12, border_width=1,
                         border_color=BORDER2, **kw)
        color = GREEN if status == "Active" else AMBER
        ctk.CTkLabel(self, text=name, font=FNT_LABEL_B,
                     text_color=TEXT_WHITE).pack(padx=14, pady=(10, 2), anchor="w")
        bot = ctk.CTkFrame(self, fg_color="transparent")
        bot.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkFrame(bot, width=8, height=8, fg_color=color,
                     corner_radius=4).pack(side="left")
        ctk.CTkLabel(bot, text=f" {status}", font=FNT_SMALL,
                     text_color=color).pack(side="left")
        ctk.CTkLabel(bot, text=f"{count} checked",
                     font=FNT_SMALL, text_color=TEXT_DIM).pack(side="right")


# ════════════════════════════════════════════════════════════════
#  SIDEBAR NAV BUTTON
# ════════════════════════════════════════════════════════════════
def nav_button(parent, icon, label, active=False, command=None):
    bg   = "#112840" if active else "transparent"
    bord = ACCENT    if active else BG_PANEL
    bord_w = 1 if active else 0
    tcol = ACCENT    if active else TEXT_MID
    f = ctk.CTkFrame(parent, fg_color=bg, corner_radius=12,
                     border_width=bord_w, border_color=bord,
                     cursor="hand2")
    f.pack(fill="x", padx=14, pady=4)
    inner = ctk.CTkFrame(f, fg_color="transparent")
    inner.pack(padx=16, pady=10)
    ctk.CTkLabel(inner, text=icon, font=("", 18)).pack(side="left")
    ctk.CTkLabel(inner, text="  " + label, font=FNT_LABEL_B,
                 text_color=tcol).pack(side="left")
    if command:
        f.bind("<Button-1>", lambda e: command())
        inner.bind("<Button-1>", lambda e: command())
        for child in inner.winfo_children():
            child.bind("<Button-1>", lambda e: command())
    return f


# ════════════════════════════════════════════════════════════════
#  DASHBOARD
# ════════════════════════════════════════════════════════════════
class Dashboard(ctk.CTkFrame):

    ACTIVITIES = [
        ("🛂", "USA tourist cleared Gate A",          "Active",  GREEN),
        ("🎫", "VIP ticket #TKT-47821 generated",     "Active",  ACCENT),
        ("📷", "QR scan verified — Lumbini entry",    "Active",  TEAL),
        ("🇩🇪", "German group of 4 checked in",       "Active",  AMBER),
        ("🔄", "Offline sync — 12 records uploaded",  "Pending", TEXT_MID),
        ("🛕", "Pashupatinath gate: 43 visitors",     "Active",  GREEN),
        ("⚠️", "Checkpoint 3 scanner timeout",        "Alert",   RED),
        ("💳", "eSewa payment confirmed — NPR 6,000", "Active",  GREEN),
    ]

    CHECKPOINTS = [
        ("Gate A — Pashupatinath", "Active",  143),
        ("Gate B — Bhaktapur",     "Active",   89),
        ("Gate C — Pokhara",       "Active",  201),
        ("Gate D — Lumbini",       "Standby",  37),
        ("VIP Lane — Himalaya",    "Active",   22),
        ("Exit / Depart",          "Active",   58),
    ]

    def __init__(self, master, open_ticket_callback=None, open_scanner_callback=None):
        super().__init__(master)
        self.open_ticket = open_ticket_callback or (lambda: None)
        self.open_scanner = open_scanner_callback or (lambda: None)
        self.pack(fill="both", expand=True)
        self.configure(fg_color=BG_VOID)

        self._build_sidebar()
        self._build_main()
        self._start_clock()
        self._pulse_activity()

    # ── SIDEBAR ─────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=220, fg_color=SIDEBAR_W, corner_radius=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        # Logo block
        logo_f = ctk.CTkFrame(sb, fg_color=BG_CARD, corner_radius=0, height=90)
        logo_f.pack(fill="x")
        logo_f.pack_propagate(False)
        ctk.CTkLabel(logo_f, text="NTNC", font=FNT_LOGO,
                     text_color=ACCENT).pack(pady=(18, 0))
        ctk.CTkLabel(logo_f, text="Tourist Ticketing", font=FNT_SMALL,
                     text_color=TEXT_DIM).pack()

        # Thin accent line
        ctk.CTkFrame(sb, height=2, fg_color=ACCENT).pack(fill="x")

        # Admin avatar block
        av = ctk.CTkFrame(sb, fg_color="transparent")
        av.pack(fill="x", padx=14, pady=16)
        circle = ctk.CTkFrame(av, width=44, height=44,
                              fg_color=ACCENT_DIM, corner_radius=22)
        circle.pack(side="left")
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text="A", font=("Georgia", 20, "bold"),
                     text_color=BG_DEEP).pack(expand=True)
        info = ctk.CTkFrame(av, fg_color="transparent")
        info.pack(side="left", padx=10)
        ctk.CTkLabel(info, text="Admin User", font=FNT_LABEL_B,
                     text_color=TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(info, text="● Online", font=FNT_SMALL,
                     text_color=GREEN).pack(anchor="w")

        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", padx=14)

        # Nav items
        ctk.CTkLabel(sb, text="NAVIGATION", font=("Courier New", 8, "bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=28, pady=(14, 4))

        nav_button(sb, "⊞", "Dashboard",     active=True)
        nav_button(sb, "🎫", "Ticket Page",   command=self.open_ticket)
        nav_button(sb, "📷", "QR Scanner",    command=self.open_scanner)
        nav_button(sb, "📊", "Analytics")
        nav_button(sb, "🗺", "Checkpoints")
        nav_button(sb, "⚙️", "Settings")

        # System health
        ctk.CTkFrame(sb, height=1, fg_color=BORDER).pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(sb, text="SYSTEM", font=("Courier New", 8, "bold"),
                     text_color=TEXT_DIM).pack(anchor="w", padx=28, pady=(0, 8))
        for label, pct, col in [("Server Load", 42, GREEN),
                                 ("DB Usage",    67, AMBER),
                                 ("Network",     88, ACCENT)]:
            f = ctk.CTkFrame(sb, fg_color="transparent")
            f.pack(fill="x", padx=18, pady=3)
            ctk.CTkLabel(f, text=label, font=FNT_SMALL,
                         text_color=TEXT_DIM).pack(side="left")
            ctk.CTkLabel(f, text=f"{pct}%", font=FNT_SMALL,
                         text_color=col).pack(side="right")
            bar_bg = ctk.CTkFrame(sb, height=4, fg_color=BORDER, corner_radius=3)
            bar_bg.pack(fill="x", padx=18, pady=(0, 4))
            fw = max(1, int(pct / 100 * 182))
            ctk.CTkFrame(bar_bg, height=4, width=fw,
                         fg_color=col, corner_radius=3).place(x=0, y=0)

        # Logout at bottom
        ctk.CTkButton(
            sb, text="⏻  Logout", height=40, corner_radius=12,
            fg_color="#1A0A14", hover_color=RED_DIM,
            text_color=RED, border_width=1, border_color=RED_DIM,
            font=FNT_LABEL_B,
        ).pack(side="bottom", pady=20, padx=14, fill="x")

    # ── MAIN AREA ────────────────────────────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=BG_DEEP)
        main.pack(side="right", fill="both", expand=True)

        self._build_topbar(main)

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(main, fg_color="transparent",
                                        scrollbar_button_color=BORDER,
                                        scrollbar_button_hover_color=ACCENT_DIM)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_stat_cards(scroll)
        self._build_middle_row(scroll)
        self._build_bottom_row(scroll)

        # Footer padding
        ctk.CTkFrame(scroll, fg_color="transparent", height=20).pack()

    # ── TOPBAR ───────────────────────────────────────────────────
    def _build_topbar(self, parent):
        bar = ctk.CTkFrame(parent, height=72, fg_color=BG_PANEL, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.pack(side="left", padx=24, fill="y")
        ctk.CTkLabel(left, text="Tourist Dashboard",
                     font=("Georgia", 22, "bold"), text_color=TEXT_WHITE).pack(side="left")
        ctk.CTkLabel(left, text="  /  Overview", font=FNT_LABEL,
                     text_color=TEXT_DIM).pack(side="left", pady=(6, 0))

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.pack(side="right", padx=24, fill="y")

        # Live clock
        self._clock_lbl = ctk.CTkLabel(right, text="",
                                       font=FNT_MONO, text_color=ACCENT)
        self._clock_lbl.pack(side="right", padx=(12, 0))

        # Date
        today = datetime.now().strftime("%d %b %Y")
        ctk.CTkLabel(right, text=today, font=FNT_SMALL,
                     text_color=TEXT_DIM).pack(side="right")

        # Notification bell
        ctk.CTkLabel(right, text="🔔", font=("", 16)).pack(side="right", padx=16)
        notif = ctk.CTkFrame(right, width=8, height=8,
                             fg_color=RED, corner_radius=4)
        notif.place(relx=1.0, rely=0.0)

    # ── STAT CARDS ───────────────────────────────────────────────
    def _build_stat_cards(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=22, pady=(20, 8))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        cards = [
            ("🎫", "Total Tickets",  1250, "issued today",   ACCENT, +12),
            ("✅", "Checked In",      875, "verified",        GREEN,  +8),
            ("⏳", "Pending",         375, "awaiting entry",  AMBER,  -3),
            ("🗺", "Active Gates",      6, "checkpoints",     TEAL,   None),
        ]
        for i, (icon, title, val, unit, col, trend) in enumerate(cards):
            card = StatCard(frame, icon, title, val, unit, col, trend=trend)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")

    # ── MIDDLE ROW: Activity + Checkpoints ───────────────────────
    def _build_middle_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=8)
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        # ── Activity feed ──────────────────────────────────────
        feed = ctk.CTkFrame(row, fg_color=BG_PANEL, corner_radius=18,
                            border_width=1, border_color=BORDER2)
        feed.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        feed_top = ctk.CTkFrame(feed, fg_color=BG_CARD, corner_radius=16, height=48)
        feed_top.pack(fill="x")
        feed_top.pack_propagate(False)
        ctk.CTkLabel(feed_top, text="⚡  Live Activity Feed",
                     font=FNT_HEAD, text_color=TEXT_WHITE).pack(side="left", padx=18)
        # Live indicator
        li = ctk.CTkFrame(feed_top, fg_color="transparent")
        li.pack(side="right", padx=18)
        ctk.CTkFrame(li, width=8, height=8, fg_color=GREEN,
                     corner_radius=4).pack(side="left")
        ctk.CTkLabel(li, text=" LIVE", font=FNT_SMALL,
                     text_color=GREEN).pack(side="left")

        self._feed_frame = ctk.CTkFrame(feed, fg_color="transparent")
        self._feed_frame.pack(fill="both", expand=True, pady=8)
        self._activity_index = 0
        self._render_activities()

        # ── Checkpoints ───────────────────────────────────────
        cp_panel = ctk.CTkFrame(row, fg_color=BG_PANEL, corner_radius=18,
                                border_width=1, border_color=BORDER2)
        cp_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        cp_top = ctk.CTkFrame(cp_panel, fg_color=BG_CARD, corner_radius=16, height=48)
        cp_top.pack(fill="x")
        cp_top.pack_propagate(False)
        ctk.CTkLabel(cp_top, text="🗺  Checkpoint Status",
                     font=FNT_HEAD, text_color=TEXT_WHITE).pack(side="left", padx=18)

        gp = ctk.CTkFrame(cp_panel, fg_color="transparent")
        gp.pack(fill="both", expand=True, padx=12, pady=12)
        gp.grid_columnconfigure((0, 1), weight=1)
        for i, (name, status, cnt) in enumerate(self.CHECKPOINTS):
            b = CheckpointBadge(gp, name, status, cnt)
            b.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="nsew")

    # ── BOTTOM ROW: Destination chart + Quick Actions ────────────
    def _build_bottom_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=8)
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        # ── Destination breakdown ──────────────────────────────
        dest = ctk.CTkFrame(row, fg_color=BG_PANEL, corner_radius=18,
                            border_width=1, border_color=BORDER2)
        dest.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        d_top = ctk.CTkFrame(dest, fg_color=BG_CARD, corner_radius=16, height=48)
        d_top.pack(fill="x")
        d_top.pack_propagate(False)
        ctk.CTkLabel(d_top, text="📍  Visitor Breakdown by Destination",
                     font=FNT_HEAD, text_color=TEXT_WHITE).pack(side="left", padx=18)

        destinations = [
            ("Mustang",         420, ACCENT),
            ("Annapurna Base Camp",  310, TEAL),
            ("Lake Rara",           290, GREEN),
            ("Sagarmatha (Everest) National Park",              230, AMBER),
        ]
        total = sum(v for _, v, _ in destinations)
        body_d = ctk.CTkFrame(dest, fg_color="transparent")
        body_d.pack(fill="both", expand=True, padx=20, pady=14)

        for name, val, col in destinations:
            pct = int(val / total * 100)
            f = ctk.CTkFrame(body_d, fg_color="transparent")
            f.pack(fill="x", pady=6)
            ctk.CTkLabel(f, text=name, font=FNT_LABEL,
                         text_color=TEXT_LIGHT, width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=f"{val}", font=FNT_LABEL_B,
                         text_color=col).pack(side="right")
            ctk.CTkLabel(f, text=f"{pct}%", font=FNT_SMALL,
                         text_color=TEXT_DIM).pack(side="right", padx=12)
            bar_bg = ctk.CTkFrame(body_d, height=8, fg_color=BORDER,
                                  corner_radius=5)
            bar_bg.pack(fill="x", pady=(0, 2))
            bar_bg.update_idletasks()
            fw = int(pct / 100 * bar_bg.winfo_reqwidth())
            ctk.CTkFrame(bar_bg, height=8, fg_color=col,
                         corner_radius=5).place(x=0, y=0, relwidth=pct/100)

        # ── Quick actions ──────────────────────────────────────
        qa = ctk.CTkFrame(row, fg_color=BG_PANEL, corner_radius=18,
                          border_width=1, border_color=BORDER2)
        qa.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        qa_top = ctk.CTkFrame(qa, fg_color=BG_CARD, corner_radius=16, height=48)
        qa_top.pack(fill="x")
        qa_top.pack_propagate(False)
        ctk.CTkLabel(qa_top, text="⚙️  Quick Actions",
                     font=FNT_HEAD, text_color=TEXT_WHITE).pack(side="left", padx=18)

        actions = [
            ("🎫  Create New Ticket",     ACCENT,   BG_CARD, self.open_ticket),
            ("📷  Open QR Scanner",       TEAL,     BG_CARD, None),
            ("📊  Export Report",         GREEN,    BG_CARD, None),
            ("🔄  Sync Offline Data",     AMBER,    BG_CARD, None),
            ("⚠️  View Alerts  (1 new)", RED,      BG_CARD, None),
        ]
        body_qa = ctk.CTkFrame(qa, fg_color="transparent")
        body_qa.pack(fill="both", expand=True, padx=14, pady=14)
        for label, fg, bg, cmd in actions:
            btn = ctk.CTkButton(
                body_qa, text=label, height=42, corner_radius=12,
                fg_color="transparent", border_width=1, border_color=fg,
                hover_color="#071220", text_color=fg,
                font=FNT_LABEL_B, command=cmd or (lambda: None),
                anchor="w",
            )
            btn.pack(fill="x", pady=5)

        # Today summary chip row
        chips = ctk.CTkFrame(body_qa, fg_color="transparent")
        chips.pack(fill="x", pady=(8, 0))
        for icon, val, col in [("💵", "NPR 3.2L", GREEN),
                                ("🌐", "18 Nations", ACCENT),
                                ("🎟", "47 VIP", AMBER)]:
            c = ctk.CTkFrame(chips, fg_color=BG_CARD2, corner_radius=10)
            c.pack(side="left", expand=True, fill="x", padx=3)
            ctk.CTkLabel(c, text=icon, font=("", 14)).pack(pady=(6, 0))
            ctk.CTkLabel(c, text=val, font=FNT_SMALL,
                         text_color=col).pack(pady=(0, 6))

    # ── CLOCK ───────────────────────────────────────────────────
    def _start_clock(self):
        def tick():
            self._clock_lbl.configure(
                text=datetime.now().strftime("%H:%M:%S"))
            self.after(1000, tick)
        tick()

    # ── LIVE ACTIVITY FEED ──────────────────────────────────────
    def _render_activities(self):
        for w in self._feed_frame.winfo_children():
            w.destroy()

        # Show 6 activities cycling
        shown = (self.ACTIVITIES * 2)[self._activity_index:
                                      self._activity_index + 6]
        for icon, text, status, color in shown:
            ts = datetime.now().strftime("%H:%M")
            ActivityRow(self._feed_frame, icon, text, ts, color)

    def _pulse_activity(self):
        self._activity_index = (self._activity_index + 1) % len(self.ACTIVITIES)
        self._render_activities()
        self.after(4000, self._pulse_activity)


# ════════════════════════════════════════════════════════════════
#  STANDALONE RUNNER
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("NTNC – Tourist Ticketing System")
    app.geometry("1300x800")
    app.minsize(1100, 700)
    Dashboard(app, open_ticket_callback=lambda: print("Open ticket page"))
    app.mainloop()