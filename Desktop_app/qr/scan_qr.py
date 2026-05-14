import cv2
from pyzbar.pyzbar import decode

def scan_qr():

    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()

        for code in decode(frame):
            data = code.data.decode("utf-8")
            print("QR Data:", data)

        cv2.imshow("Scanner", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()