"""
Tests para fitness function.
Spec: Codex PARTE 1 - Fitness exacta
"""
import pytest
from decimal import Decimal
from src.optimization.fitness import (
    calculate_fitness,
    calculate_score_segment,
    calculate_overfit_penalty,
    calculate_reg_penalty,
    SegmentMetrics
)
from src.optimization.param_space import get_default_param_space


def test_calculate_score_segment_normal_case():
    """
    Score = TradeFactor * (0.60 * Calmar + 0.40 * Sharpe)
    Spec: Codex PARTE 1.2
    """
    metrics = SegmentMetrics(
        trades=50,
        return_pct=0.20,      # 20% return
        maxdd=0.10,           # 10% DD
        sharpe=1.5,
        pf=1.8,
        gross_profit=10000,
        gross_loss=5555
    )
    
    score = calculate_score_segment(metrics)
    
    # TradeFactor = min(1.0, 50/30) = 1.0
    # Calmar = 0.20 / max(0.10, 0.05) = 0.20 / 0.10 = 2.0
    # Score = 1.0 * (0.60 * 2.0 + 0.40 * 1.5)
    #       = 1.0 * (1.2 + 0.6) = 1.8
    
    expected = 1.8
    assert abs(score - expected) < 0.001


def test_calculate_score_segment_low_trades():
    """
    TradeFactor penaliza si trades < 30.
    """
    metrics = SegmentMetrics(
        trades=15,  # Menos de 30
        return_pct=0.30,
        maxdd=0.10,
        sharpe=2.0,
        pf=2.0,
        gross_profit=10000,
        gross_loss=5000
    )
    
    score = calculate_score_segment(metrics)
    
    # TradeFactor = min(1.0, 15/30) = 0.5
    # Calmar = 0.30 / 0.10 = 3.0
    # Score = 0.5 * (0.60 * 3.0 + 0.40 * 2.0)
    #       = 0.5 * (1.8 + 0.8) = 1.3
    
    expected = 1.3
    assert abs(score - expected) < 0.001


def test_calculate_score_segment_zero_maxdd():
    """
    Si MaxDD = 0, usar floor de 0.05 (5%).
    """
    metrics = SegmentMetrics(
        trades=40,
        return_pct=0.15,
        maxdd=0.0,  # Sin drawdown
        sharpe=1.8,
        pf=3.0,
        gross_profit=15000,
        gross_loss=5000
    )
    
    score = calculate_score_segment(metrics)
    
    # Calmar = 0.15 / max(0.0, 0.05) = 0.15 / 0.05 = 3.0
    expected_calmar = 3.0
    # Score = 1.0 * (0.60 * 3.0 + 0.40 * 1.8) = 2.52
    
    expected = 2.52
    assert abs(score - expected) < 0.001


def test_calculate_score_segment_negative_sharpe():
    """
    Sharpe puede ser negativo.
    """
    metrics = SegmentMetrics(
        trades=35,
        return_pct=-0.05,
        maxdd=0.15,
        sharpe=-0.5,  # Negativo
        pf=0.8,
        gross_profit=8000,
        gross_loss=10000
    )
    
    score = calculate_score_segment(metrics)
    
    # Calmar = -0.05 / 0.15 = -0.333
    # Score = 1.0 * (0.60 * -0.333 + 0.40 * -0.5)
    #       = 1.0 * (-0.2 - 0.2) = -0.4
    
    assert score < 0  # Debe ser negativo


def test_calculate_overfit_penalty_good_generalization():
    """
    Si Sub y Val tienen performance similar, penalty baja.
    """
    metrics_sub = SegmentMetrics(
        trades=50, return_pct=0.20, maxdd=0.10, 
        sharpe=1.5, pf=2.0, gross_profit=10000, gross_loss=5000
    )
    
    metrics_val = SegmentMetrics(
        trades=40, return_pct=0.18, maxdd=0.12,
        sharpe=1.4, pf=1.8, gross_profit=9000, gross_loss=5000
    )
    
    penalty = calculate_overfit_penalty(metrics_sub, metrics_val)
    
    # PF_degradation = 1.8 / 2.0 = 0.90 (> 0.70, no penalty)
    # Sharpe_degradation = (1.4+2)/(1.5+2) = 3.4/3.5 = 0.97 (> 0.75, no penalty)
    # Penalty ≈ 0
    
    assert penalty < 0.1


def test_calculate_overfit_penalty_strong_overfitting():
    """
    Si Val degrada mucho vs Sub, penalty alta.
    """
    metrics_sub = SegmentMetrics(
        trades=60, return_pct=0.40, maxdd=0.08,
        sharpe=2.5, pf=3.0, gross_profit=20000, gross_loss=6667
    )
    
    metrics_val = SegmentMetrics(
        trades=30, return_pct=-0.10, maxdd=0.25,
        sharpe=-0.5, pf=0.6, gross_profit=6000, gross_loss=10000
    )
    
    penalty = calculate_overfit_penalty(metrics_sub, metrics_val)
    
    # PF_degradation = 0.6 / 3.0 = 0.20 (< 0.70)
    # Sharpe_degradation = (-0.5+2)/(2.5+2) = 1.5/4.5 = 0.33 (< 0.75)
    # Penalty = 2.0 * max(0, 0.70 - 0.20) + 1.0 * max(0, 0.75 - 0.33)
    #         = 2.0 * 0.50 + 1.0 * 0.42 = 1.0 + 0.42 = 1.42
    
    assert penalty > 1.0


def test_calculate_reg_penalty_at_defaults():
    """
    Si params == defaults, penalty = 0.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    penalty = calculate_reg_penalty(params, space)
    
    assert penalty == 0.0


def test_calculate_reg_penalty_far_from_defaults():
    """
    Si params están lejos de defaults, penalty > 0.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    # Modificar algunos params al extremo
    params["g_ob_quality"] = 2.0      # default ~1.0
    params["g_momentum"] = 0.5        # default ~1.0
    params["alpha_threshold"] = 0.75  # default ~0.60
    params["stop_loss_atr_mult"] = 3.5  # default ~2.0
    
    penalty = calculate_reg_penalty(params, space)
    
    # L1_norm = sum |normalized_diff|
    # RegPenalty = 0.15 * L1_norm
    
    assert penalty > 0.1  # Debe haber penalty significativo


def test_calculate_fitness_full_pipeline():
    """
    Test completo de fitness con todos los componentes.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    metrics_sub = SegmentMetrics(
        trades=50, return_pct=0.25, maxdd=0.10,
        sharpe=1.8, pf=2.2, gross_profit=12500, gross_loss=5682
    )
    
    metrics_val = SegmentMetrics(
        trades=35, return_pct=0.20, maxdd=0.12,
        sharpe=1.5, pf=1.9, gross_profit=10000, gross_loss=5263
    )
    
    fitness = calculate_fitness(
        params=params,
        metrics_sub=metrics_sub,
        metrics_val=metrics_val,
        param_space=space
    )
    
    # Fitness = 0.25*ScoreSub + 0.75*ScoreVal - OverfitPenalty - RegPenalty
    # - ScoreSub debería ser ~2.16
    # - ScoreVal debería ser ~1.92
    # - OverfitPenalty debería ser ~0 (buena generalización)
    # - RegPenalty = 0 (params == defaults)
    # Fitness ≈ 0.25*2.16 + 0.75*1.92 - 0 - 0 = 0.54 + 1.44 = 1.98
    
    assert 1.5 < fitness < 2.5  # Rango razonable


def test_calculate_fitness_hard_fail_low_val_trades():
    """
    Si ValTrain tiene < 10 trades, fitness gets a gradual penalty (not -inf).
    trades=5 → penalty factor = 5/10 = 0.5 → fitness is halved.
    Spec: Updated behavior (removed hard -inf for trades < 10).
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    metrics_sub = SegmentMetrics(
        trades=50, return_pct=0.20, maxdd=0.10,
        sharpe=1.5, pf=2.0, gross_profit=10000, gross_loss=5000
    )
    
    metrics_val = SegmentMetrics(
        trades=5,  # < 10 → gradual penalty factor = 0.5
        return_pct=0.10, maxdd=0.05,
        sharpe=1.0, pf=1.5, gross_profit=5000, gross_loss=3333
    )
    
    fitness = calculate_fitness(
        params=params,
        metrics_sub=metrics_sub,
        metrics_val=metrics_val,
        param_space=space
    )
    
    # Should be finite (penalized) not -inf
    assert fitness != float('-inf')
    assert fitness > 0  # With 5 trades and decent metrics, should be positive
    

def test_calculate_fitness_zero_val_trades_is_not_negative_inf():
    """
    0 val trades should get gradual penalty (fitness=0), not -inf.
    The gradual penalty factor = 0/10 = 0 → fitness * 0 = 0.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    metrics_sub = SegmentMetrics(
        trades=50, return_pct=0.20, maxdd=0.10,
        sharpe=1.5, pf=2.0, gross_profit=10000, gross_loss=5000
    )
    
    metrics_val = SegmentMetrics(
        trades=0,  # 0 trades → factor = 0/10 = 0 → fitness * 0 = 0
        return_pct=0.0, maxdd=0.0,
        sharpe=0.0, pf=0.0, gross_profit=0, gross_loss=0
    )
    
    fitness = calculate_fitness(
        params=params,
        metrics_sub=metrics_sub,
        metrics_val=metrics_val,
        param_space=space
    )
    
    assert fitness != float('-inf')
    assert fitness == 0.0


def test_calculate_fitness_hard_fail_high_val_dd():
    """
    Si ValTrain MaxDD > 25%, fitness = -inf.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    metrics_sub = SegmentMetrics(
        trades=50, return_pct=0.30, maxdd=0.15,
        sharpe=2.0, pf=2.5, gross_profit=15000, gross_loss=6000
    )
    
    metrics_val = SegmentMetrics(
        trades=40, return_pct=0.10, 
        maxdd=0.30,  # > 0.25 (HARD FAIL)
        sharpe=0.5, pf=1.2, gross_profit=6000, gross_loss=5000
    )
    
    fitness = calculate_fitness(
        params=params,
        metrics_sub=metrics_sub,
        metrics_val=metrics_val,
        param_space=space
    )
    
    assert fitness == float('-inf')


def test_calculate_fitness_hard_fail_negative_val_return():
    """
    Si ValTrain Return < -5%, fitness = -inf.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    
    metrics_sub = SegmentMetrics(
        trades=60, return_pct=0.25, maxdd=0.12,
        sharpe=1.8, pf=2.3, gross_profit=12500, gross_loss=5435
    )
    
    metrics_val = SegmentMetrics(
        trades=35, 
        return_pct=-0.08,  # < -0.05 (HARD FAIL)
        maxdd=0.18, sharpe=-0.8, pf=0.7,
        gross_profit=4000, gross_loss=5714
    )
    
    fitness = calculate_fitness(
        params=params,
        metrics_sub=metrics_sub,
        metrics_val=metrics_val,
        param_space=space
    )
    
    assert fitness == float('-inf')
