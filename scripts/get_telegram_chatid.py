"""
Helper para obtener chat_id de Telegram.
"""
import requests
import json

TOKEN = "8413964929:AAEcrozVHC6mkmNIwr65oTTs2Sjb-k2a_mQ"

import time

print("="*70)
print("OBTENIENDO CHAT_ID DE TELEGRAM (MODO AUTOMÁTICO)")
print("="*70)
print()
print("INSTRUCCIONES:")
print("1. Abre Telegram en tu celular")
print("2. Busca tu bot (@BotFather te dio el link)")
print("3. Envía el mensaje: /start")
print()
print("Esperando 120 segundos a que envíes el mensaje...")

chat_id = None
start_time = time.time()
found = False

while time.time() - start_time < 120:
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("result"):
                # Buscar chat_id en los updates
                for update in data["result"]:
                    if "message" in update:
                        chat_id = update["message"]["chat"]["id"]
                        found = True
                        break
        
        if found:
            break
            
    except Exception:
        pass
    
    time.sleep(2)
    elapsed = int(time.time() - start_time)
    if elapsed % 10 == 0:
        print(f"Buscando... ({elapsed}s/120s)")

if not found:
    print("\n❌ Tiempo agotado. No se encontró chat_id.")
    print("Asegúrate de enviar /start al bot.")
    exit(1)

print(f"\n✅ Chat ID encontrado: {chat_id}")

try:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.text}")
        exit(1)
    
    data = response.json()
    
    if not data.get("result"):
        print("❌ No se encontraron mensajes")
        print("Asegúrate de haber enviado /start al bot")
        exit(1)
    
    # Buscar chat_id en los updates
    chat_ids = set()
    for update in data["result"]:
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            chat_ids.add(chat_id)
    
    if not chat_ids:
        print("❌ No se encontró chat_id")
        exit(1)
    
    if len(chat_ids) == 1:
        chat_id = list(chat_ids)[0]
        print(f"✅ Chat ID encontrado: {chat_id}")
        
        # Guardar configuración automáticamente
        from pathlib import Path
        
        config = {
            "bot_token": TOKEN,
            "chat_id": str(chat_id)
        }
        
        config_path = Path("results/wfo/telegram_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuración guardada en: {config_path}")
        
        # Enviar mensaje de prueba
        print()
        print("Enviando mensaje de prueba...")
        
        test_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        test_data = {
            "chat_id": chat_id,
            "text": "🤖 *BOT8000 WFO*\n\n✅ Telegram configurado correctamente!\n\nRecibirás alertas aquí cuando:\n• El proceso se detenga\n• Haya problemas detectados\n• El WFO se complete",
            "parse_mode": "Markdown"
        }
        
        test_response = requests.post(test_url, data=test_data, timeout=10)
        
        if test_response.status_code == 200:
            print("✅ Mensaje de prueba enviado!")
            print("Revisa tu Telegram")
        else:
            print(f"⚠️ No se pudo enviar mensaje: {test_response.text}")
        
    else:
        print(f"⚠️ Se encontraron múltiples chat_ids: {chat_ids}")
        print("Por favor selecciona el correcto manualmente")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
