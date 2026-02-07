"""
Setup Telegram Alerts for WFO Monitor.
Interactive setup wizard.
"""
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


CONFIG_PATH = Path("results/wfo/telegram_config.json")


def test_bot_token(token: str) -> bool:
    """Test if bot token is valid."""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_name = data["result"]["username"]
                print(f"✅ Bot válido: @{bot_name}")
                return True
        print(f"❌ Token inválido: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def send_test_message(token: str, chat_id: str) -> bool:
    """Send test message."""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": "🤖 *BOT8000 WFO Monitor*\n\n✅ Configuración exitosa!\n\nRecibirás alertas aquí.",
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("="*70)
    print("CONFIGURACIÓN DE ALERTAS TELEGRAM")
    print("="*70)
    print()
    
    # Check existing config
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            existing = json.load(f)
        print(f"✅ Configuración existente encontrada")
        print(f"   Token: {existing['bot_token'][:20]}...")
        print(f"   Chat ID: {existing['chat_id']}")
        print()
        
        choice = input("¿Reconfigurar? (s/n): ").strip().lower()
        if choice != 's':
            print("Usando configuración existente.")
            return
    
    print()
    print("PASO 1: TOKEN DEL BOT")
    print("-"*40)
    print("Necesitas crear un bot en Telegram:")
    print("1. Abre Telegram y busca @BotFather")
    print("2. Envía /newbot")
    print("3. Sigue las instrucciones")
    print("4. Copia el token que te da")
    print()
    
    token = input("Pega tu bot token: ").strip()
    
    if not token:
        # Use default token
        token = "8413964929:AAEcrozVHC6mkmNIwr65oTTs2Sjb-k2a_mQ"
        print(f"Usando token predeterminado")
    
    if not test_bot_token(token):
        print("Token inválido. Verifica e intenta de nuevo.")
        return
    
    print()
    print("PASO 2: CHAT ID")
    print("-"*40)
    print("Ahora necesito tu Chat ID:")
    print("1. Abre Telegram")
    print("2. Busca tu bot y ábrelo")
    print("3. Envía el mensaje /start")
    print()
    
    input("Presiona Enter después de enviar /start al bot...")
    
    print()
    print("Buscando tu Chat ID...")
    
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return
        
        data = response.json()
        
        if not data.get("result"):
            print("❌ No se encontraron mensajes")
            print("Asegúrate de haber enviado /start al bot")
            
            # Manual entry
            chat_id = input("Ingresa tu Chat ID manualmente: ").strip()
        else:
            # Find chat_id
            chat_id = None
            for update in data["result"]:
                if "message" in update:
                    chat_id = str(update["message"]["chat"]["id"])
                    break
            
            if not chat_id:
                chat_id = input("Ingresa tu Chat ID manualmente: ").strip()
            else:
                print(f"✅ Chat ID encontrado: {chat_id}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        chat_id = input("Ingresa tu Chat ID manualmente: ").strip()
    
    if not chat_id:
        print("No se pudo obtener Chat ID")
        return
    
    # Save config
    config = {
        "bot_token": token,
        "chat_id": chat_id
    }
    
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    
    print()
    print(f"✅ Configuración guardada en: {CONFIG_PATH}")
    
    # Test message
    print()
    print("Enviando mensaje de prueba...")
    if send_test_message(token, chat_id):
        print("✅ Mensaje de prueba enviado! Revisa tu Telegram.")
    else:
        print("⚠️ No se pudo enviar mensaje de prueba")
    
    print()
    print("="*70)
    print("CONFIGURACIÓN COMPLETADA")
    print("="*70)
    print()
    print("Ahora puedes ejecutar el monitor con alertas:")
    print()
    print("  python scripts/monitor_wfo.py --pid <PID> --interval 300")
    print()


if __name__ == "__main__":
    main()
