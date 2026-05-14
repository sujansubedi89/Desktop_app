import customtkinter as ctk
from tkinter import messagebox
from qr.generate_qr import generate_qr

# ---------------- SETTINGS ---------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TicketPage(ctk.CTkFrame):

    def __init__(self, master, go_dashboard_callback):
        super().__init__(master)
        self.go_dashboard = go_dashboard_callback

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

        # TITLE
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="Tourist Ticketing\nSystem",
            font=("Arial", 20, "bold"),
            justify="center"
        )
        self.sidebar_title.pack(pady=(0, 40))

        # ---------------- BACK BUTTON (FIXED) ---------------- #
        self.dashboard_btn = ctk.CTkButton(
            self.sidebar,
            text="← Back to Dashboard",
            height=45,
            corner_radius=10,
            fg_color="#144870",
            hover_color="#15507D",
            command=self.go_dashboard
        )
        self.dashboard_btn.pack(pady=10, padx=20, fill="x")

        # CREATE TICKET BUTTON (just visual)
        self.ticket_btn = ctk.CTkButton(
            self.sidebar,
            text="Create Ticket",
            height=45,
            corner_radius=10,
            fg_color="#1F6AA5",
            hover_color="#15507D"
        )
        self.ticket_btn.pack(pady=10, padx=20, fill="x")

        # SCANNER
        self.scan_btn = ctk.CTkButton(
            self.sidebar,
            text="QR Scanner",
            height=45,
            corner_radius=10,
            fg_color="#144870",
            hover_color="#15507D"
        )
        self.scan_btn.pack(pady=10, padx=20, fill="x")

        # LOGOUT
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

        self.page_title = ctk.CTkLabel(
            self.topbar,
            text="Create Tourist Ticket",
            font=("Arial", 30, "bold")
        )
        self.page_title.pack(side="left", padx=25, pady=20)

        # ---------------- FORM ---------------- #
        self.form_card = ctk.CTkFrame(
            self.main_frame,
            width=700,
            height=600,
            fg_color="#102C3D",
            corner_radius=25
        )
        self.form_card.pack(pady=30)
        self.form_card.pack_propagate(False)

        self.form_title = ctk.CTkLabel(
            self.form_card,
            text="Tourist Information",
            font=("Arial", 28, "bold")
        )
        self.form_title.pack(pady=(30, 20))

        # NAME
        self.name = ctk.CTkEntry(self.form_card, placeholder_text="Tourist Full Name", width=500, height=40)
        self.name.pack(pady=10)

        # COUNTRY
        self.country = ctk.CTkEntry(self.form_card, placeholder_text="Country", width=500, height=40)
        self.country.pack(pady=10)

        # PASSPORT
        self.passport = ctk.CTkEntry(self.form_card, placeholder_text="Passport Number", width=500, height=40)
        self.passport.pack(pady=10)

        # TYPE
        self.ticket_type = ctk.CTkOptionMenu(
            self.form_card,
            values=["Normal Ticket", "VIP Ticket", "Group Ticket"],
            width=500
        )
        self.ticket_type.pack(pady=10)

        # CHECKPOINTS
        self.checkpoints = ctk.CTkOptionMenu(
            self.form_card,
            values=["6 Checkpoints", "7 Checkpoints", "8 Checkpoints"],
            width=500
        )
        self.checkpoints.pack(pady=10)

        # BUTTON
        self.generate_btn = ctk.CTkButton(
            self.form_card,
            text="Generate QR Ticket",
            width=500,
            height=45,
            fg_color="#00AEEF",
            hover_color="#008FCC",
            command=self.create_ticket
        )
        self.generate_btn.pack(pady=20)

        # STATUS
        self.status_label = ctk.CTkLabel(self.form_card, text="", text_color="#00E676")
        self.status_label.pack()

    # ---------------- CREATE TICKET ---------------- #
    def create_ticket(self):

        name = self.name.get()
        country = self.country.get()
        passport = self.passport.get()

        if name == "" or country == "" or passport == "":
            messagebox.showerror("Error", "Please fill all fields")
            return

        data = {
            "name": name,
            "country": country,
            "passport": passport,
            "type": self.ticket_type.get(),
            "checkpoints": self.checkpoints.get()
        }

        generate_qr(data)

        self.status_label.configure(text="QR Ticket Generated Successfully")

        messagebox.showinfo("Success", "Ticket Created")

        self.name.delete(0, "end")
        self.country.delete(0, "end")
        self.passport.delete(0, "end")