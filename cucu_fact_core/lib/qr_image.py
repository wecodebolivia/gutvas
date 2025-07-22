from io import BytesIO
import base64
import qrcode as qrcode


def generate_qr(string_url):
    qr = qrcode.QRCode(
        box_size=4,
        border=2,
    )

    qr.add_data(string_url)
    qr.make(fit=True)
    img = qr.make_image()

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
