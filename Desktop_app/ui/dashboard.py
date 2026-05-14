import customtkinter as ctk

# -------------------- SETTINGS -------------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Dashboard(ctk.CTkFrame):

    def __init__(self, master, open_ticket_callback):
        super().__init__(master)
        self.open_ticket_callback = open_ticket_callback

        self.pack(fill="both", expand=True)

        # ---------------- MAIN BACKGROUND ---------------- #
        self.configure(fg_color="#08141D")

        # ---------------- SIDEBAR ---------------- #
        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            fg_color="#102C3D",
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")

        # LOGO
        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="NTNC",
            font=("Arial", 38, "bold"),
            text_color="#00C2FF"
        )
        self.logo.pack(pady=(40, 10))

        # SYSTEM TITLE
        self.system_title = ctk.CTkLabel(
            self.sidebar,
            text="Tourist Ticketing\nSystem",
            font=("Arial", 20, "bold"),
            justify="center"
        )
        self.system_title.pack(pady=(0, 40))

        # MENU BUTTONS
        self.dashboard_btn = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            height=45,
            corner_radius=10,
            fg_color="#1F6AA5",
            hover_color="#15507D"
        )
        self.dashboard_btn.pack(pady=10, padx=20, fill="x")

        self.ticket_btn = ctk.CTkButton(
            self.sidebar,
            text="Ticket Page",
            height=45,
            corner_radius=10,
            fg_color="#144870",
            hover_color="#15507D",
            command=self.open_ticket_callback
        )
        self.ticket_btn.pack(pady=10, padx=20, fill="x")

        self.scan_btn = ctk.CTkButton(
            self.sidebar,
            text="QR Scanner",
            height=45,
            corner_radius=10,
            fg_color="#144870",
            hover_color="#15507D"
        )
        self.scan_btn.pack(pady=10, padx=20, fill="x")

        self.logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            height=45,
            corner_radius=10,
            fg_color="#A61E4D",
            hover_color="#82163C"
        )
        self.logout_btn.pack(side="bottom", pady=30, padx=20, fill="x")

        # ---------------- MAIN CONTENT ---------------- #
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#08141D"
        )
        self.main_frame.pack(side="right", fill="both", expand=True)

        # TOP BAR
        self.topbar = ctk.CTkFrame(
            self.main_frame,
            height=80,
            fg_color="#102C3D",
            corner_radius=15
        )
        self.topbar.pack(fill="x", padx=20, pady=20)

        self.dashboard_title = ctk.CTkLabel(
            self.topbar,
            text="Tourist Dashboard",
            font=("Arial", 30, "bold")
        )
        self.dashboard_title.pack(side="left", padx=25, pady=20)

        self.admin_label = ctk.CTkLabel(
            self.topbar,
            text="Welcome, Admin",
            font=("Arial", 16),
            text_color="gray80"
        )
        self.admin_label.pack(side="right", padx=25)

        # ---------------- STATISTICS SECTION ---------------- #
        self.stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.stats_frame.pack(pady=10, padx=20, fill="x")

        # CARD 1
        self.card1 = self.create_card(
            self.stats_frame,
            "Total Tickets",
            "1,250",
            "#00C2FF"
        )
        self.card1.grid(row=0, column=0, padx=15, pady=10)

        # CARD 2
        self.card2 = self.create_card(
            self.stats_frame,
            "Checked In",
            "875",
            "#00E676"
        )
        self.card2.grid(row=0, column=1, padx=15, pady=10)

        # CARD 3
        self.card3 = self.create_card(
            self.stats_frame,
            "Pending",
            "375",
            "#FFD54F"
        )
        self.card3.grid(row=0, column=2, padx=15, pady=10)

        # CARD 4
        self.card4 = self.create_card(
            self.stats_frame,
            "Checkpoints",
            "6 Active",
            "#FF6B6B"
        )
        self.card4.grid(row=0, column=3, padx=15, pady=10)

        # ---------------- RECENT ACTIVITY ---------------- #
        self.activity_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#102C3D",
            corner_radius=20
        )
        self.activity_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        self.activity_title = ctk.CTkLabel(
            self.activity_frame,
            text="Recent Tourist Activity",
            font=("Arial", 24, "bold")
        )
        self.activity_title.pack(anchor="w", padx=25, pady=(20, 10))

        # SAMPLE ACTIVITIES
        activities = [
            "✔ Tourist from USA checked in at Checkpoint 1",
            "✔ Tourist from Germany checked in at Checkpoint 2",
            "✔ QR Ticket verified successfully",
            "✔ New tourist ticket generated",
            "✔ Offline sync completed"
        ]

        for activity in activities:
            label = ctk.CTkLabel(
                self.activity_frame,
                text=activity,
                font=("Arial", 16),
                anchor="w"
            )
            label.pack(anchor="w", padx=30, pady=8)

    # ---------------- CARD FUNCTION ---------------- #
    def create_card(self, parent, title, value, color):

        card = ctk.CTkFrame(
            parent,
            width=220,
            height=140,
            fg_color="#102C3D",
            corner_radius=20
        )

        card.pack_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 18),
            text_color="gray80"
        )
        title_label.pack(pady=(25, 10))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 32, "bold"),
            text_color=color
        )
        value_label.pack()

        return card

    # ---------------- CARD FUNCTION ---------------- #