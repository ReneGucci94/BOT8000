"""
Integration tests para WFO completo.
Mock del backtester + integración Windows + GA + Fitness.
"""
import pytest
from typing import List, Dict, Any
from src.core.market import Candle
from src.optimization.windows import generate_windows, WindowConfig
from src.optimization.param_space import get_default_param_space
from src.optimization.fitness import (
    calculate_fitness,
    SegmentMetrics
)
from src.optimization.genetic_algorithm import (
    GeneticAlgorithm,
    GAConfig
)


def mock_backtest(
    candles: List[Candle],
    params: Dict[str, Any]
) -> SegmentMetrics:
    """
    Mock de backtester que simula métricas.
    
    La "calidad" de los params determina las métricas:
    - Params cerca de defaults → mejores métricas
    - Params lejos de defaults → peores métricas
    
    Args:
        candles: Datos para backtest
        params: Parámetros del sistema
        
    Returns:
        Métricas simuladas
    """
    space = get_default_param_space()
    defaults = space.get_defaults()
    
    # Calcular "distancia" a defaults (normalized)
    distance = 0.0
    for name, value in params.items():
        param_def = space.params[name]
        default_val = defaults[name]
        range_val = param_def.max_value - param_def.min_value
        normalized_diff = abs(value - default_val) / range_val
        distance += normalized_diff ** 2
    
    distance = distance ** 0.5  # Euclidean distance
    
    # Métricas base (buenos params)
    base_trades = 50
    base_return = 0.25
    base_maxdd = 0.10
    base_sharpe = 1.8
    base_pf = 2.2
    
    # Degradar métricas según distancia
    degradation = max(0.3, 1.0 - distance * 0.5)  # 30% mínimo
    
    trades = int(base_trades * degradation)
    return_pct = base_return * degradation
    maxdd = base_maxdd / degradation  # Más DD si peores params
    sharpe = base_sharpe * degradation
    pf = base_pf * degradation
    
    # Calcular gross_profit/loss desde PF
    gross_loss = 10000.0
    gross_profit = gross_loss * pf
    
    return SegmentMetrics(
        trades=trades,
        return_pct=return_pct,
        maxdd=min(maxdd, 0.40),  # Cap DD a 40%
        sharpe=sharpe,
        pf=pf,
        gross_profit=gross_profit,
        gross_loss=gross_loss
    )


def test_mock_backtest_defaults_are_best():
    """
    Verifica que params=defaults producen mejores métricas.
    """
    space = get_default_param_space()
    
    # Mock candles (no se usan en mock)
    candles = []
    
    # Defaults
    params_default = space.get_defaults()
    metrics_default = mock_backtest(candles, params_default)
    
    # Params extremos (lejos de defaults)
    params_extreme = {
        name: param.max_value if i % 2 == 0 else param.min_value
        for i, (name, param) in enumerate(space.params.items())
    }
    metrics_extreme = mock_backtest(candles, params_extreme)
    
    # Defaults deben ser mejores
    assert metrics_default.return_pct > metrics_extreme.return_pct
    assert metrics_default.sharpe > metrics_extreme.sharpe
    assert metrics_default.pf > metrics_extreme.pf


def test_integration_single_window_optimization():
    """
    Test end-to-end de optimización de UNA window completa.
    
    Flujo:
    1. Generar window (train data)
    2. Split train en SubTrain/ValTrain
    3. GA optimiza usando fitness con mock backtest
    4. Verificar que mejores params fueron encontrados
    """
    space = get_default_param_space()
    
    # 1. Generar windows (usamos Window 1)
    # Mock candles: 2024 completo + warmup
    from tests.optimization.test_windows import generate_mock_candles_2024_4h
    full_data = generate_mock_candles_2024_4h()
    
    config_windows = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    
    windows = generate_windows(full_data, config_windows)
    window = windows[0]  # Jan-Apr train, May test
    
    # 2. Split train en SubTrain (Jan-Mar) + ValTrain (Apr)
    train_data = window.train_data
    n_months_train = 4
    subtrain_months = n_months_train - 1  # 3 meses
    
    # Calcular punto de split (final de Marzo)
    # Aproximación: 3/4 de train_data
    split_idx = len(train_data) * subtrain_months // n_months_train
    
    subtrain_data = train_data[:split_idx]
    valtrain_data = train_data[split_idx:]
    
    assert len(subtrain_data) > 0
    assert len(valtrain_data) > 0
    
    # 3. Crear fitness function que usa mock backtest
    def fitness_fn(params: Dict[str, Any]) -> float:
        """
        Fitness usando mock backtest.
        """
        metrics_sub = mock_backtest(subtrain_data, params)
        metrics_val = mock_backtest(valtrain_data, params)
        
        return calculate_fitness(
            params=params,
            metrics_sub=metrics_sub,
            metrics_val=metrics_val,
            param_space=space
        )
    
    # 4. Ejecutar GA
    config_ga = GAConfig(
        population_size=16,  # Pequeño para test rápido
        num_generations=5,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.15,
        mutation_sigma_pct=0.10,
        elitism_count=2,
        early_stopping_generations=3,
        seed=42
    )
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config_ga,
        fitness_function=fitness_fn
    )
    
    best_individual, history = ga.optimize()
    
    # 5. Verificaciones
    assert best_individual is not None
    assert best_individual.fitness is not None
    assert len(history) >= 1
    
    # Fitness debe ser positivo (params razonables)
    assert best_individual.fitness > 0.5
    
    # Debe haber mejorado desde gen 0
    first_gen_best = history[0]["best_fitness"]
    last_gen_best = history[-1]["best_fitness"]
    assert last_gen_best >= first_gen_best
    
    print(f"\n=== WINDOW OPTIMIZATION RESULTS ===")
    print(f"Window: {window.label}")
    print(f"Generations: {len(history)}")
    print(f"Best fitness: {best_individual.fitness:.4f}")
    print(f"Improvement: {last_gen_best - first_gen_best:.4f}")
    print(f"\nBest params (selection):")
    for name in ["alpha_threshold", "g_ob_quality", "stop_loss_atr_mult"]:
        print(f"  {name}: {best_individual.params[name]:.4f}")


def test_integration_multiple_windows():
    """
    Test de múltiples windows (simulando WFO completo).
    
    Para cada window:
    1. Optimizar params en train
    2. "Backtest" en test (con params óptimos)
    3. Acumular resultados
    """
    space = get_default_param_space()
    
    # Generar windows
    from tests.optimization.test_windows import generate_mock_candles_2024_4h
    full_data = generate_mock_candles_2024_4h()
    
    config_windows = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    
    windows = generate_windows(full_data, config_windows)
    
    # Procesar SOLO las primeras 3 windows (test rápido)
    windows_to_test = windows[:3]
    
    results = []
    
    for window in windows_to_test:
        # Split train
        train_data = window.train_data
        n_months_train = 4
        subtrain_months = n_months_train - 1
        split_idx = len(train_data) * subtrain_months // n_months_train
        
        subtrain_data = train_data[:split_idx]
        valtrain_data = train_data[split_idx:]
        
        # Fitness function
        def fitness_fn(params: Dict[str, Any]) -> float:
            metrics_sub = mock_backtest(subtrain_data, params)
            metrics_val = mock_backtest(valtrain_data, params)
            return calculate_fitness(params, metrics_sub, metrics_val, space)
        
        # GA (config reducido para speed)
        config_ga = GAConfig(
            population_size=8,
            num_generations=3,
            seed=42
        )
        
        ga = GeneticAlgorithm(space, config_ga, fitness_fn)
        best_individual, history = ga.optimize()
        
        # "Backtest" en test con params óptimos
        test_data = window.test_data
        metrics_test = mock_backtest(test_data, best_individual.params)
        
        results.append({
            "window": window.label,
            "best_fitness_train": best_individual.fitness,
            "test_return": metrics_test.return_pct,
            "test_pf": metrics_test.pf,
            "test_sharpe": metrics_test.sharpe,
            "test_trades": metrics_test.trades
        })
    
    # Verificaciones
    assert len(results) == 3
    
    for result in results:
        # Cada window debe tener fitness positivo
        assert result["best_fitness_train"] > 0
        # Test metrics deben ser razonables
        assert result["test_pf"] > 1.0
        assert result["test_trades"] > 10
    
    print(f"\n=== MULTI-WINDOW WFO RESULTS ===")
    print(f"Windows processed: {len(results)}")
    for r in results:
        print(f"\n{r['window']}:")
        print(f"  Train fitness: {r['best_fitness_train']:.4f}")
        print(f"  Test PF: {r['test_pf']:.2f}")
        print(f"  Test Return: {r['test_return']:.1%}")
        print(f"  Test Trades: {r['test_trades']}")


def test_integration_fitness_rejects_bad_candidates():
    """
    Verifica que fitness function rechaza candidatos muy malos.
    """
    space = get_default_param_space()
    
    # Mock candles
    candles = []
    
    # Params extremadamente malos (todos al mínimo/máximo)
    params_bad = {
        name: param.min_value
        for name, param in space.params.items()
    }
    
    # Forzar métricas malas
    metrics_sub = SegmentMetrics(
        trades=50,
        return_pct=0.10,
        maxdd=0.15,
        sharpe=1.0,
        pf=1.5,
        gross_profit=7500,
        gross_loss=5000
    )
    
    # ValTrain con muy pocos trades (hard fail)
    metrics_val = SegmentMetrics(
        trades=5,  # < 10 (hard fail)
        return_pct=0.05,
        maxdd=0.10,
        sharpe=0.5,
        pf=1.2,
        gross_profit=6000,
        gross_loss=5000
    )
    
    fitness = calculate_fitness(params_bad, metrics_sub, metrics_val, space)
    
    # Debe retornar -inf (hard fail)
    assert fitness == float('-inf')


def test_integration_ga_converges_to_better_params():
    """
    Verifica que GA efectivamente converge a mejores parámetros.
    """
    space = get_default_param_space()
    defaults = space.get_defaults()
    
    # Mock candles
    candles = []
    
    # Fitness simple: penalizar distancia a defaults
    def simple_fitness_fn(params: Dict[str, Any]) -> float:
        distance = sum(
            ((params[name] - defaults[name]) / 
             (space.params[name].max_value - space.params[name].min_value)) ** 2
            for name in params
        )
        return -distance  # Maximizar (menos distancia = mejor)
    
    config_ga = GAConfig(
        population_size=16,
        num_generations=8,
        seed=42
    )
    
    ga = GeneticAlgorithm(space, config_ga, simple_fitness_fn)
    best_individual, history = ga.optimize()
    
    # Best params deben estar cerca de defaults
    for name in ["alpha_threshold", "g_ob_quality", "stop_loss_atr_mult"]:
        best_val = best_individual.params[name]
        default_val = defaults[name]
        diff_pct = abs(best_val - default_val) / default_val
        
        # Debe estar dentro del 25% del default
        assert diff_pct < 0.25, f"{name}: {best_val:.4f} vs {default_val:.4f}"
