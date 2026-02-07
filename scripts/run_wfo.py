"""
Ejecuta Walk-Forward Optimization completo.
8 windows, GA optimization, análisis de resultados.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
from pathlib import Path

from src.core.market import load_candles_from_csv
from src.agents.worker import OptimizerWorker
from src.optimization.windows import generate_windows, WindowConfig
from src.optimization.param_space import get_default_param_space
from src.optimization.fitness import calculate_fitness, SegmentMetrics
from src.optimization.genetic_algorithm import GeneticAlgorithm, GAConfig


def create_fitness_function(
    worker: OptimizerWorker,
    subtrain_data,
    valtrain_data,
    param_space
):
    """
    Crea función de fitness que usa Worker REAL.
    
    Esta función se llama 256 veces por window (GA evaluations).
    """
    def fitness_fn(params: Dict[str, Any]) -> float:
        """
        Evalúa params haciendo backtest en SubTrain y ValTrain.
        """
        try:
            # Backtest en SubTrain
            subtrain_months = extract_months_from_candles(subtrain_data)
            config_sub = {
                "pair": "BTCUSDT",
                "timeframe": "4h",
                "year": 2024,
                "months": subtrain_months,
                "backtest_run_id": "wfo_subtrain",
                "initial_balance": 10000.0,
                "stop_loss": 200,
                "take_profit_multiplier": 2.0,
                "fee_rate": 0.001,
                "risk_per_trade_pct": 2.0,
                "use_msc": True
            }
            
            result_sub = worker.run(
                config=config_sub,
                params=params,
                warmup_data=None,
                initial_balance=10000.0
            )
            
            # DEBUG LOGGING
            print(f"    SubTrain: {result_sub.get('total_trades', 0)} trades, "
                  f"PF={result_sub.get('profit_factor', 0):.2f}, "
                  f"Return={result_sub.get('return', 0) if result_sub.get('return') else 0.0:.1f}%")
            
            metrics_sub = SegmentMetrics(
                trades=result_sub.get("total_trades", 0),
                return_pct=result_sub.get("return", 0.0) / 100.0 if result_sub.get("return") else 0.0,
                maxdd=result_sub.get("max_drawdown", 0.0) / 100.0 if result_sub.get("max_drawdown") else 0.0,
                sharpe=result_sub.get("sharpe", 0.0),
                pf=result_sub.get("profit_factor", 0.0),
                gross_profit=result_sub.get("gross_profit", 0.0),
                gross_loss=result_sub.get("gross_loss", 0.0)
            )
            
            # DEBUG LOGGING
            print(f"    → SegmentMetrics: {metrics_sub.trades} trades")
            
            # Backtest en ValTrain
            valtrain_months = extract_months_from_candles(valtrain_data)
            config_val = {
                "pair": "BTCUSDT",
                "timeframe": "4h",
                "year": 2024,
                "months": valtrain_months,
                "backtest_run_id": "wfo_valtrain",
                "initial_balance": 10000.0,
                "stop_loss": 200,
                "take_profit_multiplier": 2.0,
                "fee_rate": 0.001,
                "risk_per_trade_pct": 2.0,
                "use_msc": True
            }
            
            result_val = worker.run(
                config=config_val,
                params=params,
                warmup_data=None,
                initial_balance=10000.0
            )
            
            metrics_val = SegmentMetrics(
                trades=result_val.get("total_trades", 0),
                return_pct=result_val.get("return", 0.0) / 100.0 if result_val.get("return") else 0.0,
                maxdd=result_val.get("max_drawdown", 0.0) / 100.0 if result_val.get("max_drawdown") else 0.0,
                sharpe=result_val.get("sharpe", 0.0),
                pf=result_val.get("profit_factor", 0.0),
                gross_profit=result_val.get("gross_profit", 0.0),
                gross_loss=result_val.get("gross_loss", 0.0)
            )
            
            # Calcular fitness
            fitness = calculate_fitness(
                params=params,
                metrics_sub=metrics_sub,
                metrics_val=metrics_val,
                param_space=param_space
            )
            
            return fitness
            
        except Exception as e:
            print(f"Error en fitness evaluation: {e}")
            return float('-inf')
    
    return fitness_fn


def extract_months_from_candles(candles) -> List[int]:
    """
    Extrae lista de meses únicos de un conjunto de candles.
    """
    if not candles:
        return []
    
    months = set()
    for candle in candles:
        # candle.timestamp is Unix timestamp in ms
        dt = datetime.fromtimestamp(candle.timestamp / 1000)
        months.add(dt.month)
    
    return sorted(list(months))


def split_train_data(train_data, n_months_train: int):
    """
    Split train data en SubTrain (primeros N-1 meses) y ValTrain (último mes).
    """
    subtrain_months = n_months_train - 1
    split_idx = len(train_data) * subtrain_months // n_months_train
    
    subtrain_data = train_data[:split_idx]
    valtrain_data = train_data[split_idx:]
    
    return subtrain_data, valtrain_data


def run_wfo():
    """
    Ejecuta Walk-Forward Optimization completo.
    """
    print("="*70)
    print("WALK-FORWARD OPTIMIZATION - BOT8000 v3")
    print("="*70)
    print()
    
    # Configuración
    param_space = get_default_param_space()
    
    config_windows = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    
    config_ga = GAConfig(
        population_size=32,
        num_generations=8,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.15,
        mutation_sigma_pct=0.10,
        elitism_count=2,
        early_stopping_generations=3,
        seed=42
    )
    
    print(f"WFO Configuration:")
    print(f"  Train months: {config_windows.train_months}")
    print(f"  Test months: {config_windows.test_months}")
    print(f"  Step months: {config_windows.step_months}")
    print(f"  Warmup bars: {config_windows.warmup_bars}")
    print()
    print(f"GA Configuration:")
    print(f"  Population: {config_ga.population_size}")
    print(f"  Generations: {config_ga.num_generations}")
    print(f"  Max evaluations per window: ~256")
    print()
    
    # Cargar datos completos
    print("Loading candles from CSV...")
    candles_path = "data/BTCUSDT_4h_2024.csv"
    
    if not os.path.exists(candles_path):
        print(f"ERROR: {candles_path} not found")
        print("Please ensure you have 2024 data available")
        return
    
    full_data = load_candles_from_csv(candles_path)
    print(f"Loaded {len(full_data)} candles")
    print()
    
    # Generar windows
    print("Generating windows...")
    windows = generate_windows(full_data, config_windows)
    print(f"Generated {len(windows)} windows")
    print()
    
    # Resultados
    results = []
    cumulative_balance = 10000.0
    
    # Procesar cada window
    for i, window in enumerate(windows):
        print("="*70)
        print(f"WINDOW {i+1}/{len(windows)}: {window.label}")
        print("="*70)
        print()
        
        start_time = time.time()
        
        # Split train
        print(f"  Train data: {len(window.train_data)} candles")
        subtrain_data, valtrain_data = split_train_data(
            window.train_data,
            config_windows.train_months
        )
        print(f"  SubTrain: {len(subtrain_data)} candles")
        print(f"  ValTrain: {len(valtrain_data)} candles")
        print()
        
        # Crear worker
        worker = OptimizerWorker(worker_id=f"wfo_w{i+1}")
        
        # Crear fitness function
        print(f"  Creating fitness function...")
        fitness_fn = create_fitness_function(
            worker=worker,
            subtrain_data=subtrain_data,
            valtrain_data=valtrain_data,
            param_space=param_space
        )
        
        # Ejecutar GA
        print(f"  Running GA optimization...")
        print(f"  This may take several hours...")
        print()
        
        ga = GeneticAlgorithm(
            param_space=param_space,
            config=config_ga,
            fitness_function=fitness_fn
        )
        
        best_individual, history = ga.optimize()
        
        elapsed = time.time() - start_time
        print()
        print(f"  GA completed in {elapsed/3600:.1f} hours")
        print(f"  Best fitness (train): {best_individual.fitness:.4f}")
        print(f"  Generations run: {len(history)}")
        print()
        
        # Backtest en Test OOS con params óptimos
        print(f"  Running OOS backtest with optimal params...")
        test_months = extract_months_from_candles(window.test_data)
        config_test = {
            "pair": "BTCUSDT",
            "timeframe": "4h",
            "year": 2024,
            "months": test_months,
            "backtest_run_id": f"wfo_test_w{i+1}",
            "initial_balance": cumulative_balance,
            "stop_loss": 200,
            "take_profit_multiplier": 2.0,
            "fee_rate": 0.001,
            "risk_per_trade_pct": 2.0,
            "use_msc": True
        }
        
        result_test = worker.run(
            config=config_test,
            params=best_individual.params,
            warmup_data=window.warmup_data,
            initial_balance=cumulative_balance
        )
        
        # Actualizar balance acumulado
        new_balance = result_test.get("final_balance", cumulative_balance)
        window_return = (new_balance - cumulative_balance) / cumulative_balance
        
        print(f"  Test Results:")
        print(f"    Trades: {result_test.get('trades', 0)}")
        print(f"    Win Rate: {result_test.get('win_rate', 0.0):.1f}%")
        print(f"    Profit Factor: {result_test.get('profit_factor', 0.0):.2f}")
        print(f"    Return: {window_return*100:.2f}%")
        print(f"    Balance: ${cumulative_balance:.2f} → ${new_balance:.2f}")
        print()
        
        # Guardar resultado
        window_result = {
            "window_id": i + 1,
            "label": window.label,
            "train_fitness": best_individual.fitness,
            "train_generations": len(history),
            "optimal_params": best_individual.params,
            "test_trades": result_test.get("total_trades", 0),
            "test_win_rate": result_test.get("win_rate", 0.0),
            "test_pf": result_test.get("profit_factor", 0.0),
            "test_return_pct": window_return * 100,
            "test_maxdd": result_test.get("max_drawdown", 0.0),
            "test_sharpe": result_test.get("sharpe", 0.0),
            "start_balance": cumulative_balance,
            "end_balance": new_balance,
            "elapsed_hours": elapsed / 3600
        }
        
        results.append(window_result)
        cumulative_balance = new_balance
    
    # Análisis agregado
    print()
    print("="*70)
    print("WFO COMPLETE - AGGREGATE RESULTS")
    print("="*70)
    print()
    
    final_balance = cumulative_balance
    total_return = (final_balance - 10000) / 10000
    
    avg_test_pf = sum(r["test_pf"] for r in results) / len(results)
    median_test_pf = sorted([r["test_pf"] for r in results])[len(results)//2]
    
    winning_windows = sum(1 for r in results if r["test_pf"] > 1.1)
    pass_rate = winning_windows / len(results)
    
    print(f"Initial Balance: $10,000")
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Total Return: {total_return*100:.2f}%")
    print()
    print(f"Test PF Statistics:")
    print(f"  Average: {avg_test_pf:.2f}")
    print(f"  Median: {median_test_pf:.2f}")
    print(f"  Pass Rate (PF > 1.1): {pass_rate*100:.0f}%")
    print()
    
    # Overfitting detection
    pf_values = [r["test_pf"] for r in results]
    import math
    log_pf_values = [math.log(max(pf, 0.01)) for pf in pf_values]
    std_log_pf = (sum((x - sum(log_pf_values)/len(log_pf_values))**2 for x in log_pf_values) / len(log_pf_values)) ** 0.5
    
    failing_windows = sum(1 for r in results if r["test_pf"] < 1.0)
    
    print(f"Overfitting Analysis:")
    print(f"  Std(log(PF)): {std_log_pf:.3f} {'⚠️ HIGH VARIANCE' if std_log_pf > 0.30 else '✅ OK'}")
    print(f"  Failing windows (PF < 1.0): {failing_windows}/8 {'⚠️ TOO MANY' if failing_windows >= 3 else '✅ OK'}")
    print()
    
    # Guardar resultados
    output_dir = Path("results/wfo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"wfo_results_{timestamp}.json"
    
    output = {
        "config": {
            "windows": len(windows),
            "ga_population": config_ga.population_size,
            "ga_generations": config_ga.num_generations
        },
        "summary": {
            "initial_balance": 10000.0,
            "final_balance": final_balance,
            "total_return_pct": total_return * 100,
            "avg_test_pf": avg_test_pf,
            "median_test_pf": median_test_pf,
            "pass_rate": pass_rate,
            "std_log_pf": std_log_pf,
            "failing_windows": failing_windows
        },
        "windows": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    print()
    print("="*70)
    print("WFO COMPLETE")
    print("="*70)
    
    # Decisión final
    print()
    print("NEXT STEPS:")
    print()
    
    if avg_test_pf > 1.2 and pass_rate > 0.67 and std_log_pf < 0.30:
        print("✅ SYSTEM READY FOR PAPER TRADING")
        print("   - Strong performance (avg PF > 1.2)")
        print("   - High pass rate (> 67%)")
        print("   - Low variance (stable)")
        print()
        print("   Proceed to 30-day paper trading validation")
    else:
        print("⚠️ SYSTEM NEEDS ADJUSTMENT")
        if avg_test_pf <= 1.2:
            print(f"   - Low average PF ({avg_test_pf:.2f})")
        if pass_rate <= 0.67:
            print(f"   - Low pass rate ({pass_rate*100:.0f}%)")
        if std_log_pf >= 0.30:
            print(f"   - High variance ({std_log_pf:.3f})")
        print()
        print("   Consider:")
        print("   - Adjust fitness function weights")
        print("   - Modify parameter ranges")
        print("   - Add more training data")
        print("   - Review worst-performing windows")


if __name__ == "__main__":
    run_wfo()
