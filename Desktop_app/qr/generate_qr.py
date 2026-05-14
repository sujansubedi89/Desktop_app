import qrcode
import json

def generate_qr(data):

    qr_data = json.dumps(data)

    qr = qrcode.make(qr_data)

    qr.save("ticket_qr.png")

    print("QR Generated Successfully")