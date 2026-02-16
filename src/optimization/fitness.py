"""
Fitness function para Walk-Forward Optimization.
Spec: Codex PARTE 1 - "Fitness function (fitness) EXACTA"
"""
from dataclasses import dataclass
from typing import Dict, Any
import math
from src.optimization.param_space import ParamSpace


@dataclass
class SegmentMetrics:
    """
    Métricas de un segmento de backtest (SubTrain o ValTrain).
    """
    trades: int
    return_pct: float          # Return como decimal (0.20 = 20%)
    maxdd: float               # MaxDD como decimal (0.10 = 10%)
    sharpe: float
    pf: float                  # Profit Factor
    gross_profit: float
    gross_loss: float


def calculate_score_segment(metrics: SegmentMetrics) -> float:
    """
    Calcula score de un segmento.
    
    Spec: Codex PARTE 1.2
    
    Formula:
        TradeFactor = min(1.0, trades / 30)
        Calmar = Return / max(MaxDD, 0.05)
        Score = TradeFactor * (0.60 * Calmar + 0.40 * Sharpe)
    
    Args:
        metrics: Métricas del segmento
        
    Returns:
        Score (puede ser negativo si Return o Sharpe negativos)
    """
    # 1. TradeFactor = min(1.0, trades / 30.0)
    trade_factor = min(1.0, metrics.trades / 30.0)
    
    # 2. MaxDD_safe = max(metrics.maxdd, 0.05)  # Floor de 5%
    maxdd_safe = max(float(metrics.maxdd), 0.05)
    
    # 3. Calmar = metrics.return_pct / MaxDD_safe
    calmar = float(metrics.return_pct) / maxdd_safe
    
    # 4. Score = TradeFactor * (0.60 * Calmar + 0.40 * metrics.sharpe)
    score = trade_factor * (0.60 * calmar + 0.40 * float(metrics.sharpe))
    
    return score


def calculate_overfit_penalty(
    metrics_sub: SegmentMetrics,
    metrics_val: SegmentMetrics
) -> float:
    """
    Calcula penalty por overfitting (degradación Sub → Val).
    
    Spec: Codex PARTE 1.2 - "Penalización de overfit (EXACTA)"
    
    Formula:
        PF_degradation = PF_val / max(PF_sub, 0.01)
        Sharpe_degradation = (Sharpe_val + 2.0) / max(Sharpe_sub + 2.0, 0.1)
        
        Penalty = 2.0 * max(0, 0.70 - PF_degradation) + 
                  1.0 * max(0, 0.75 - Sharpe_degradation)
    
    Args:
        metrics_sub: Métricas de SubTrain
        metrics_val: Métricas de ValTrain
        
    Returns:
        Penalty >= 0 (0 = sin overfitting, mayor = más overfitting)
    """
    # 1. Manejar edge case: si gross_loss == 0, PF = 10.0 (assuming strict handling or pre-calculated)
    # The metrics input (SegmentMetrics) assumes PF is already calculated. 
    # Whatever value is passed in 'metrics.pf' is used.
    
    pf_sub = float(metrics_sub.pf)
    pf_val = float(metrics_val.pf)
    
    # 3. PF_degradation = PF_val / max(PF_sub, 0.01)
    pf_degradation = pf_val / max(pf_sub, 0.01)
    
    # 4. SharpeAdj(x) = x + 2.0
    # 5. Sharpe_degradation = SharpeAdj(Sharpe_val) / max(SharpeAdj(Sharpe_sub), 0.1)
    sharpe_adj_val = float(metrics_val.sharpe) + 2.0
    sharpe_adj_sub = float(metrics_sub.sharpe) + 2.0
    
    sharpe_degradation = sharpe_adj_val / max(sharpe_adj_sub, 0.1)
    
    # 6. Penalty por PF: 2.0 * max(0, 0.70 - PF_degradation)
    penalty_pf = 2.0 * max(0.0, 0.70 - pf_degradation)
    
    # 7. Penalty por Sharpe: 1.0 * max(0, 0.75 - Sharpe_degradation)
    penalty_sharpe = 1.0 * max(0.0, 0.75 - sharpe_degradation)
    
    # 8. Sumar ambas penalties
    return penalty_pf + penalty_sharpe


def calculate_reg_penalty(
    params: Dict[str, Any],
    param_space: ParamSpace
) -> float:
    """
    Calcula penalty por alejarse de defaults (regularización).
    
    Spec: Codex PARTE 1.2 - "Regularización hacia defaults (EXACTA)"
    
    Formula:
        L1_norm = sum_i | (p_i - p_default_i) / (p_max_i - p_min_i) |
        RegPenalty = 0.15 * L1_norm
    
    Args:
        params: Parámetros actuales
        param_space: Espacio de parámetros con defaults
        
    Returns:
        Penalty >= 0 (0 = en defaults, mayor = más alejado)
    """
    # 1. defaults = param_space.get_defaults()
    defaults = param_space.get_defaults()
    l1_norm = 0.0
    
    # 3. Para cada param en params:
    for name, value in params.items():
        if name not in param_space.params:
            continue
            
        param_def = param_space.params[name]
        default_val = defaults[name]
        
        # diff = params[name] - defaults[name]
        diff = float(value) - float(default_val)
        
        # range = param_space.params[name].max_value - min_value
        rng = float(param_def.max_value) - float(param_def.min_value)
        if rng == 0:
            continue
            
        # normalized_diff = abs(diff / range)
        normalized_diff = abs(diff / rng)
        
        # L1_norm += normalized_diff
        l1_norm += normalized_diff
        
    # 4. RegPenalty = 0.15 * L1_norm
    return 0.15 * l1_norm


def calculate_fitness(
    params: Dict[str, Any],
    metrics_sub: SegmentMetrics,
    metrics_val: SegmentMetrics,
    param_space: ParamSpace
) -> float:
    """
    Calcula fitness final de un candidato.
    
    Spec: Codex PARTE 1.2 - "Fitness final (a maximizar)"
    
    Formula:
        Fitness = 0.25*ScoreSub + 0.75*ScoreVal - OverfitPenalty - RegPenalty
    
    Hard failures (return -inf):
    - Si metrics_val.trades < 10
    - Si metrics_val.maxdd > 0.25
    - Si metrics_val.return_pct < -0.05
    
    Args:
        params: Parámetros del candidato
        metrics_sub: Métricas de SubTrain
        metrics_val: Métricas de ValTrain
        param_space: Espacio de parámetros
        
    Returns:
        Fitness (a maximizar). -inf si falla hard checks.
    """
    # 1. Hard checks (Codex PARTE 1.3):
    # Note: trades == 0 is handled by the gradual penalty below (factor = 0/10 = 0)
    # This avoids all-`-inf` populations that break GA optimization.
    if metrics_val.maxdd > 0.25:
        return float('-inf')
    if metrics_val.return_pct < -0.05:
        return float('-inf')
    
    # 2. Calcular ScoreSub = calculate_score_segment(metrics_sub)
    score_sub = calculate_score_segment(metrics_sub)
    
    # 3. Calcular ScoreVal = calculate_score_segment(metrics_val)
    score_val = calculate_score_segment(metrics_val)
    
    # 4. Calcular OverfitPenalty = calculate_overfit_penalty(metrics_sub, metrics_val)
    overfit_penalty = calculate_overfit_penalty(metrics_sub, metrics_val)
    
    # 5. Calcular RegPenalty = calculate_reg_penalty(params, param_space)
    reg_penalty = calculate_reg_penalty(params, param_space)
    
    # 6. Fitness = 0.25*ScoreSub + 0.75*ScoreVal - OverfitPenalty - RegPenalty
    fitness = (0.25 * score_sub) + (0.75 * score_val) - overfit_penalty - reg_penalty

    # New Gradual Penalty for Low Trades (Task 5)
    # Replaces previous hard check for trades < 10
    if metrics_val.trades < 10:
        trade_penalty_factor = metrics_val.trades / 10.0
        fitness *= trade_penalty_factor

    return fitness
