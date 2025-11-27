"""Serviço de geração de QR Codes"""

import io
import base64

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("[QRService] Biblioteca qrcode não instalada")


class QRService:
    """Gera QR Codes para acesso dos jogadores"""

    def generate_qr_base64(self, url: str) -> str:
        """Gera QR Code e retorna como base64"""
        if not HAS_QRCODE:
            return ""

        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"

        except Exception as e:
            print(f"[QRService] Erro: {e}")
            return ""


# Instância global
qr_service = QRService()
