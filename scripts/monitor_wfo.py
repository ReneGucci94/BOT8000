"""
WFO Monitor - Monitorea el proceso WFO y envía alertas via Telegram.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Telegram config
TELEGRAM_CONFIG_PATH = Path("results/wfo/telegram_config.json")
STATUS_FILE = Path("results/wfo/status.json")
ALERTS_LOG = Path("results/wfo/alerts.log")
LOG_FILE = Path("results/wfo/wfo_execution.log")


def load_telegram_config():
    """Load Telegram configuration."""
    if TELEGRAM_CONFIG_PATH.exists():
        with open(TELEGRAM_CONFIG_PATH) as f:
            return json.load(f)
    return None


def send_telegram_alert(message: str, config: dict = None):
    """Send alert via Telegram."""
    if config is None:
        config = load_telegram_config()
    
    if not config:
        print(f"[ALERT] (No Telegram) {message}")
        return False
    
    try:
        import requests
        url = f"https://api.telegram.org/bot{config['bot_token']}/sendMessage"
        data = {
            "chat_id": config['chat_id'],
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")
        return False


def log_alert(message: str):
    """Log alert to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALERTS_LOG, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")


def is_process_running(pid: int) -> bool:
    """Check if process is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def get_log_stats() -> dict:
    """Get statistics from log file."""
    stats = {
        "size": 0,
        "lines": 0,
        "current_window": 0,
        "last_fitness": None,
        "last_update": None,
        "errors": 0
    }
    
    if not LOG_FILE.exists():
        return stats
    
    stats["size"] = LOG_FILE.stat().st_size
    stats["last_update"] = datetime.fromtimestamp(LOG_FILE.stat().st_mtime)
    
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            stats["lines"] = len(lines)
            
            # Find current window
            window_matches = re.findall(r'WINDOW (\d+)/8', content)
            if window_matches:
                stats["current_window"] = int(window_matches[-1])
            
            # Find last fitness
            fitness_matches = re.findall(r'Best fitness.*?: ([0-9.\-]+)', content)
            if fitness_matches:
                stats["last_fitness"] = float(fitness_matches[-1])
            
            # Count errors
            stats["errors"] = content.count("ERROR")
            
    except Exception as e:
        print(f"[WARN] Error reading log: {e}")
    
    return stats


def save_status(status: dict):
    """Save current status to file."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, default=str)


def monitor_wfo(pid: int, interval: int = 300):
    """Main monitoring loop."""
    print("="*70)
    print("WFO MONITOR INICIADO")
    print("="*70)
    print(f"PID: {pid}")
    print(f"Intervalo: {interval}s")
    print(f"Log: {LOG_FILE}")
    print()
    
    telegram_config = load_telegram_config()
    if telegram_config:
        print("✅ Telegram configurado - alertas activadas")
        send_telegram_alert("🚀 *WFO Monitor Iniciado*\n\nMonitoreando proceso...", telegram_config)
    else:
        print("⚠️ Telegram no configurado - solo alertas locales")
    
    print()
    print("Monitoreando... (Ctrl+C para detener)")
    print("-"*70)
    
    last_log_size = 0
    stuck_count = 0
    
    try:
        while True:
            # Check process
            if not is_process_running(pid):
                message = "🔴 *ALERTA: Proceso WFO terminado*\n\nEl proceso ya no está corriendo."
                print(f"\n[ALERT] {message}")
                log_alert(message)
                send_telegram_alert(message, telegram_config)
                
                # Check if completed successfully
                stats = get_log_stats()
                if stats["current_window"] == 8:
                    complete_msg = "✅ *WFO COMPLETADO*\n\nEl proceso terminó exitosamente."
                    send_telegram_alert(complete_msg, telegram_config)
                
                break
            
            # Get stats
            stats = get_log_stats()
            
            # Check if stuck
            if stats["size"] == last_log_size and last_log_size > 0:
                stuck_count += 1
                if stuck_count >= 3:  # 3 intervals sin cambios
                    message = f"⚠️ *ALERTA: Proceso posiblemente atascado*\n\nLog sin cambios por {stuck_count * interval}s"
                    print(f"\n[WARN] {message}")
                    log_alert(message)
                    send_telegram_alert(message, telegram_config)
                    stuck_count = 0
            else:
                stuck_count = 0
                last_log_size = stats["size"]
            
            # Check for bad fitness
            if stats["last_fitness"] is not None and stats["last_fitness"] < -100:
                message = f"⚠️ *ALERTA: Fitness muy bajo*\n\nFitness: {stats['last_fitness']:.2f}"
                log_alert(message)
                # Don't spam Telegram for this
            
            # Update status
            status = {
                "timestamp": datetime.now().isoformat(),
                "pid": pid,
                "running": True,
                "window": stats["current_window"],
                "log_size_mb": stats["size"] / (1024*1024),
                "log_lines": stats["lines"],
                "last_fitness": stats["last_fitness"],
                "errors": stats["errors"],
                "last_update": stats["last_update"].isoformat() if stats["last_update"] else None
            }
            save_status(status)
            
            # Print status
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] Window {stats['current_window']}/8 | "
                  f"Log: {stats['size']/(1024*1024):.1f}MB | "
                  f"Lines: {stats['lines']} | "
                  f"Fitness: {stats['last_fitness'] if stats['last_fitness'] else 'N/A'}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitor detenido por usuario")
        send_telegram_alert("⏸️ *WFO Monitor Detenido*\n\nEl monitor fue detenido manualmente.", telegram_config)


def main():
    parser = argparse.ArgumentParser(description="WFO Monitor")
    parser.add_argument("--pid", type=int, required=True, help="PID del proceso WFO")
    parser.add_argument("--interval", type=int, default=300, help="Intervalo de monitoreo en segundos")
    
    args = parser.parse_args()
    monitor_wfo(args.pid, args.interval)


if __name__ == "__main__":
    main()
