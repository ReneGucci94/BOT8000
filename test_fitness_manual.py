"""
Test manual de fitness con valores realistas.
"""
from src.optimization.fitness import (
    calculate_fitness, SegmentMetrics
)
from src.optimization.param_space import get_default_param_space


def test_realistic_good_candidate():
    """
    Candidato con buena performance y generalización.
    """
    space = get_default_param_space()
    params = space.get_defaults()
    params["alpha_threshold"] = 0.65  # Ajustado ligeramente
    
    # SubTrain: muy bueno
    metrics_sub = SegmentMetrics(
        trades=80,
        return_pct=0.35,
        maxdd=0.12,
        sharpe=2.1,
        pf=2.4,
        gross_profit=17500,
        gross_loss=7292
    )
    
    # ValTrain: bueno pero menor (generaliza bien)
    metrics_val = SegmentMetrics(
        trades=55,
        return_pct=0.28,
        maxdd=0.15,
        sharpe=1.7,
        pf=2.0,
        gross_profit=14000,
        gross_loss=7000
    )
    
    fitness = calculate_fitness(params, metrics_sub, metrics_val, space)
    
    print(f"\n=== GOOD CANDIDATE ===")
    print(f"Fitness: {fitness:.4f}")
    print(f"Expected: > 2.0 (high fitness)")
    
    assert fitness > 2.0


def test_realistic_overfitted_candidate():
    """
    Candidato overfitted (excelente en Sub, malo en Val).
    """
    space = get_default_param_space()
    params = space.get_defaults()
    params["g_ob_quality"] = 1.8  # Alejado de default
    params["g_momentum"] = 0.6
    
    # SubTrain: excelente
    metrics_sub = SegmentMetrics(
        trades=90,
        return_pct=0.50,
        maxdd=0.08,
        sharpe=3.0,
        pf=3.5,
        gross_profit=25000,
        gross_loss=7143
    )
    
    # ValTrain: pésimo (no generaliza)
    metrics_val = SegmentMetrics(
        trades=35,
        return_pct=-0.03,
        maxdd=0.22,
        sharpe=0.2,
        pf=0.95,
        gross_profit=9500,
        gross_loss=10000
    )
    
    fitness = calculate_fitness(params, metrics_sub, metrics_val, space)
    
    print(f"\n=== OVERFITTED CANDIDATE ===")
    print(f"Fitness: {fitness:.4f}")
    print(f"Expected: < 0.5 (low fitness, high penalties)")
    
    assert fitness < 0.5


if __name__ == "__main__":
    test_realistic_good_candidate()
    test_realistic_overfitted_candidate()
    print("\n✅ Manual tests passed")
