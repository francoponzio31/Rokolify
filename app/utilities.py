import qrcode
from io import BytesIO


def generate_qr_img(qr_data):

    # Genera el código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")    

    # Guarda la imagen en un buffer de bytes y luego la envía al navegador
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format="PNG")
    # Se establece la posición del buffer en 0 con seek(0), lo que lo prepara para su posterior lectura
    img_buffer.seek(0)

    return img_buffer