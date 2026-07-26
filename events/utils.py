import io
import random
import string
import qrcode
from django.core.files.base import ContentFile
from django.utils import timezone


def generate_order_code():
    date_str = timezone.now().strftime('%Y%m%d')
    rand = ''.join(random.choices(string.digits, k=4))
    return f"EVT-{date_str}-{rand}"


def generate_ticket_code():
    date_str = timezone.now().strftime('%Y%m%d')
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"TKT-{date_str}-{rand}"


def generate_qr_code_image(ticket_code):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(ticket_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f"{ticket_code}.png")
