"""
WFO Dashboard - Visualización en tiempo real del progreso WFO.
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("results/wfo/wfo_execution.log")
STATUS_FILE = Path("results/wfo/status.json")


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def parse_log_file() -> dict:
    """Parse log file for detailed status."""
    data = {
        "windows": [],
        "current_window": 0,
        "current_gen": 0,
        "total_gens": 8,
        "evaluations": 0,
        "last_fitness": None,
        "best_fitness": None,
        "start_time": None,
        "current_status": "Unknown",
        "errors": 0,
        "trades_subtrain": 0,
        "trades_valtrain": 0,
        "last_lines": []
    }
    
    if not LOG_FILE.exists():
        data["current_status"] = "Waiting for log file..."
        return data
    
    try:
        with open(LOG_FILE, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            data["last_lines"] = lines[-20:]
        
        # Errors
        data["errors"] = content.count("ERROR")
        
        # Window progress
        window_matches = re.findall(r'WINDOW (\d+)/8: ([\w\-]+)', content)
        if window_matches:
            data["current_window"] = int(window_matches[-1][0])
            for match in window_matches:
                data["windows"].append({
                    "id": int(match[0]),
                    "label": match[1]
                })
        
        # Generation progress
        gen_matches = re.findall(r'Generation (\d+)', content)
        if gen_matches:
            data["current_gen"] = int(gen_matches[-1])
        
        # Fitness values
        fitness_matches = re.findall(r'Best fitness.*?: ([0-9.\-]+)', content)
        if fitness_matches:
            values = [float(x) for x in fitness_matches]
            data["last_fitness"] = values[-1]
            data["best_fitness"] = max(values)
        
        # Evaluation count (approximate from backtest logs)
        backtest_count = content.count("Backtest finished")
        data["evaluations"] = backtest_count // 2  # SubTrain + ValTrain per eval
        
        # Current status
        if "WFO COMPLETE" in content:
            data["current_status"] = "✅ COMPLETE"
        elif "GA completed" in content.split("WINDOW")[-1] if "WINDOW" in content else False:
            data["current_status"] = "Running OOS backtest..."
        elif "Running GA" in content:
            data["current_status"] = f"GA Generation {data['current_gen']}"
        elif "Creating fitness" in content:
            data["current_status"] = "Setting up fitness function..."
        elif "Loading candles" in content:
            data["current_status"] = "Loading data..."
        else:
            data["current_status"] = "Processing..."
        
        # Win rates from backtests
        winrate_matches = re.findall(r'WinRate: ([0-9.]+)%', content)
        if winrate_matches:
            data["last_winrate"] = float(winrate_matches[-1])
        
    except Exception as e:
        data["current_status"] = f"Error parsing log: {e}"
    
    return data


def format_time_elapsed(start: datetime) -> str:
    """Format elapsed time."""
    delta = datetime.now() - start
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def draw_progress_bar(current: int, total: int, width: int = 40) -> str:
    """Draw ASCII progress bar."""
    if total == 0:
        return "[" + "-" * width + "]"
    
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = 100 * current / total
    return f"[{bar}] {pct:.1f}%"


def render_dashboard(data: dict):
    """Render dashboard to terminal."""
    clear_screen()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("╔" + "═"*68 + "╗")
    print("║" + "  🤖 BOT8000 WFO DASHBOARD  ".center(68) + "║")
    print("╠" + "═"*68 + "╣")
    print(f"║  Last Update: {now}".ljust(69) + "║")
    print("╠" + "═"*68 + "╣")
    
    # Window Progress
    print("║  WINDOW PROGRESS".ljust(69) + "║")
    window_bar = draw_progress_bar(data["current_window"], 8)
    print(f"║  {window_bar} Window {data['current_window']}/8".ljust(69) + "║")
    
    # Generation Progress (within current window)
    print("║".ljust(69) + "║")
    print("║  GA GENERATIONS".ljust(69) + "║")
    gen_bar = draw_progress_bar(data["current_gen"], data["total_gens"])
    print(f"║  {gen_bar} Gen {data['current_gen']}/{data['total_gens']}".ljust(69) + "║")
    
    print("╠" + "═"*68 + "╣")
    
    # Stats
    print("║  METRICS".ljust(69) + "║")
    fitness_str = f"{data['last_fitness']:.4f}" if data['last_fitness'] else "N/A"
    best_str = f"{data['best_fitness']:.4f}" if data['best_fitness'] else "N/A"
    winrate_str = f"{data.get('last_winrate', 0):.1f}%" if data.get('last_winrate') else "N/A"
    
    print(f"║  Last Fitness: {fitness_str}  |  Best: {best_str}  |  WinRate: {winrate_str}".ljust(69) + "║")
    print(f"║  Evaluations: ~{data['evaluations']}  |  Errors: {data['errors']}".ljust(69) + "║")
    
    print("╠" + "═"*68 + "╣")
    
    # Status
    status_color = "🟢" if "COMPLETE" in data["current_status"] else "🟡"
    print(f"║  STATUS: {status_color} {data['current_status']}".ljust(69) + "║")
    
    print("╠" + "═"*68 + "╣")
    
    # Recent log lines
    print("║  RECENT ACTIVITY".ljust(69) + "║")
    print("║" + "-"*68 + "║")
    
    for line in data["last_lines"][-5:]:
        # Truncate long lines
        if len(line) > 65:
            line = line[:62] + "..."
        # Clean up line
        line = line.replace("\n", "").strip()
        if line:
            print(f"║  {line}".ljust(69) + "║")
    
    print("╚" + "═"*68 + "╝")
    print()
    print("Press Ctrl+C to exit")


def main():
    parser = argparse.ArgumentParser(description="WFO Dashboard")
    parser.add_argument("--refresh", type=int, default=10, help="Refresh interval in seconds")
    
    args = parser.parse_args()
    
    print("Starting WFO Dashboard...")
    print(f"Refresh interval: {args.refresh}s")
    print()
    
    try:
        while True:
            data = parse_log_file()
            render_dashboard(data)
            
            if "COMPLETE" in data["current_status"]:
                print("\n✅ WFO Completed! Dashboard will stop.")
                break
            
            time.sleep(args.refresh)
            
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


if __name__ == "__main__":
    main()
