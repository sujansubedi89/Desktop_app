# utils/qr_generator.py
#
# Generates a QR code image for a ticket.
# The QR code contains the ticket number — when staff scan it
# at a checkpost, they read the ticket number from the QR.
#
# The image is saved as a .png file in a folder called "qrcodes/"

import qrcode
import os

# Where QR code images get saved
QR_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'qrcodes')


def generate_qr(ticket_number):
    """
    Creates a QR code image for the given ticket number.
    Saves it as qrcodes/TKT-2024-000001.png

    Parameters:
        ticket_number (str): e.g. "TKT-2024-000001"

    Returns:
        str → full path to the saved image file

    Example:
        path = generate_qr("TKT-2024-000001")
        # path = "/your/project/qrcodes/TKT-2024-000001.png"
        # Your friend shows this image in the UI
    """
    # Create the output folder if it doesn't exist yet
    os.makedirs(QR_OUTPUT_DIR, exist_ok=True)

    # Create the QR code
    # The QR code stores just the ticket number as text
    qr = qrcode.QRCode(
        version=1,                              # size of QR (1 = smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # HIGH — survives damage
        box_size=10,                            # pixels per square
        border=4,                               # white border squares
    )
    qr.add_data(ticket_number)
    qr.make(fit=True)

    # Make it black on white
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the file
    file_path = os.path.join(QR_OUTPUT_DIR, f"{ticket_number}.png")
    img.save(file_path)

    print(f"✅ QR code saved: {file_path}")
    return file_path


def get_qr_path(ticket_number):
    """
    Returns the path to an existing QR code file.
    Use this to retrieve a QR that was already generated.

    Returns:
        str  → file path if it exists
        None → if not yet generated
    """
    file_path = os.path.join(QR_OUTPUT_DIR, f"{ticket_number}.png")
    return file_path if os.path.exists(file_path) else None