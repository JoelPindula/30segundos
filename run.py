"""
30 Segundos v3.1 - Inicializador
"""

import uvicorn
import socket


def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    local_ip = get_local_ip()

    print("\n" + "=" * 60)
    print("🎲 30 SEGUNDOS v3.1 - Servidor Iniciado!")
    print("=" * 60)
    print(f"\n📍 Acesse localmente: http://localhost:8000")
    print(f"📱 Acesse na rede:    http://{local_ip}:8000")
    print(f"\n🎮 Admin: http://localhost:8000/admin")
    print("\n💡 Use o IP da rede para conectar celulares!")
    print("=" * 60 + "\n")

    uvicorn.run(
        "backend.main:app_with_socket",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
