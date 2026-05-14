import customtkinter as ctk
from ui.login import LoginPage
from ui.dashboard import Dashboard
from ui.ticket_page import TicketPage

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1200x700")
app.title("Tourist Ticketing System")

def go_dashboard():
    # Destroy current page if it exists
    for widget in app.winfo_children():
        if hasattr(widget, 'destroy'):
            widget.destroy()
    
    dashboard = Dashboard(app, go_ticket)
    dashboard.pack(fill="both", expand=True)


def go_ticket():
    # Destroy current page if it exists
    for widget in app.winfo_children():
        if hasattr(widget, 'destroy'):
            widget.destroy()
    
    ticket = TicketPage(app, go_dashboard)
    ticket.pack(fill="both", expand=True)


login = LoginPage(app, go_dashboard)

app.mainloop()