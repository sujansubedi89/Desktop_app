import customtkinter as ctk
from PIL import Image

# ------------------- SETTINGS ------------------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginPage(ctk.CTkFrame):

    def __init__(self, master, go_dashboard):
        super().__init__(master)
        self.go_dashboard = go_dashboard

        # FULL WINDOW
        self.pack(fill="both", expand=True)

        # ---------------- BACKGROUND ---------------- #
        self.bg_frame = ctk.CTkFrame(
            self,
            fg_color="#0B1D2A"
        )
        self.bg_frame.pack(fill="both", expand=True)

        # ---------------- LEFT SIDE ---------------- #
        self.left_frame = ctk.CTkFrame(
            self.bg_frame,
            fg_color="#102C3D",
            corner_radius=0
        )
        self.left_frame.pack(side="left", fill="both", expand=True)

        # ---------------- LOGO ---------------- #
        self.logo_label = ctk.CTkLabel(
            self.left_frame,
            text="NTNC",
            font=("Arial", 55, "bold"),
            text_color="#00D2FF"
        )
        self.logo_label.pack(pady=(120, 10))

        # ---------------- SYSTEM TITLE ---------------- #
        self.system_title = ctk.CTkLabel(
            self.left_frame,
            text="Tourist Checkpoint\nTicketing System",
            font=("Arial", 32, "bold"),
            justify="center"
        )
        self.system_title.pack(pady=10)

        # ---------------- SUBTITLE ---------------- #
        self.subtitle = ctk.CTkLabel(
            self.left_frame,
            text="National Trust for Nature Conservation",
            font=("Arial", 18),
            text_color="gray80"
        )
        self.subtitle.pack(pady=5)

        # ---------------- INFO LABEL ---------------- #
        self.info_label = ctk.CTkLabel(
            self.left_frame,
            text=(
                "Secure Tourist Verification System\n"
                "Offline QR Validation • Multi Checkpoints\n"
                "Built for Tourism Management"
            ),
            font=("Arial", 16),
            justify="center",
            text_color="gray70"
        )
        self.info_label.pack(pady=40)

        # ---------------- RIGHT SIDE ---------------- #
        self.right_frame = ctk.CTkFrame(
            self.bg_frame,
            width=450,
            fg_color="#07131D",
            corner_radius=0
        )
        self.right_frame.pack(side="right", fill="y")

        # ---------------- LOGIN CARD ---------------- #
        self.login_card = ctk.CTkFrame(
            self.right_frame,
            width=350,
            height=500,
            corner_radius=25,
            fg_color="#102C3D",
            border_width=1,
            border_color="#1F6AA5"
        )

        self.login_card.place(relx=0.5, rely=0.5, anchor="center")

        # ---------------- LOGIN TITLE ---------------- #
        self.login_title = ctk.CTkLabel(
            self.login_card,
            text="Welcome Back",
            font=("Arial", 30, "bold")
        )
        self.login_title.pack(pady=(45, 10))

        # ---------------- LOGIN SUBTITLE ---------------- #
        self.login_subtitle = ctk.CTkLabel(
            self.login_card,
            text="Login to Continue",
            font=("Arial", 15),
            text_color="gray70"
        )
        self.login_subtitle.pack(pady=(0, 25))

        # ---------------- USERNAME ENTRY ---------------- #
        self.username = ctk.CTkEntry(
            self.login_card,
            placeholder_text="Enter Username",
            width=240,
            height=40,
            corner_radius=10,
            font=("Arial", 14),
            border_width=1,
            border_color="#1F6AA5"
        )
        self.username.pack(pady=(15, 10))

        # ---------------- PASSWORD ENTRY ---------------- #
        self.password = ctk.CTkEntry(
            self.login_card,
            placeholder_text="Enter Password",
            show="●",
            width=240,
            height=40,
            corner_radius=10,
            font=("Arial", 14),
            border_width=1,
            border_color="#1F6AA5"
        )
        self.password.pack(pady=10)

        # ---------------- OPTIONS FRAME ---------------- #
        self.options_frame = ctk.CTkFrame(
            self.login_card,
            fg_color="transparent"
        )
        self.options_frame.pack(fill="x", padx=55, pady=(5, 15))

        # ---------------- REMEMBER ME ---------------- #
        self.remember = ctk.CTkCheckBox(
            self.options_frame,
            text="Remember",
            checkbox_width=18,
            checkbox_height=18,
            font=("Arial", 12)
        )
        self.remember.pack(side="left")

        # ---------------- FORGOT PASSWORD ---------------- #
        self.forgot_btn = ctk.CTkButton(
            self.options_frame,
            text="Forgot Password?",
            fg_color="transparent",
            hover=False,
            text_color="#00AEEF",
            font=("Arial", 12, "underline"),
            width=20,
            command=self.forgot_password
        )
        self.forgot_btn.pack(side="right")

        # ---------------- LOGIN BUTTON ---------------- #
        self.login_btn = ctk.CTkButton(
            self.login_card,
            text="LOGIN",
            width=240,
            height=42,
            corner_radius=12,
            font=("Arial", 15, "bold"),
            fg_color="#00AEEF",
            hover_color="#008FCC",
            command=self.login
        )
        self.login_btn.pack(pady=18)

        # ---------------- STATUS LABEL ---------------- #
        self.status_label = ctk.CTkLabel(
            self.login_card,
            text="",
            font=("Arial", 13),
            text_color="red"
        )
        self.status_label.pack(pady=8)

        # ---------------- FOOTER ---------------- #
        self.footer = ctk.CTkLabel(
            self.login_card,
            text="© 2026 NTNC Tourist System",
            font=("Arial", 11),
            text_color="gray60"
        )
        self.footer.pack(side="bottom", pady=20)

    # ---------------- LOGIN FUNCTION ---------------- #
    def login(self):
        username = self.username.get()
        password = self.password.get()

        if username == "admin" and password == "admin":
            self.go_dashboard()
        else:
            self.status_label.configure(
                text="Invalid Username or Password"
            )

    # ---------------- FORGOT PASSWORD FUNCTION ---------------- #
    def forgot_password(self):

        self.status_label.configure(
            text="Please contact system administrator"
        )