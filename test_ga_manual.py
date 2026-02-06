"""
Test manual del GA con problema de optimización simple.
"""
from src.optimization.genetic_algorithm import GeneticAlgorithm, GAConfig
from src.optimization.param_space import get_default_param_space


def test_ga_rastrigin_function():
    """
    Optimiza función de Rastrigin simplificada.
    Mínimo en todos los params = sus valores default.
    """
    space = get_default_param_space()
    defaults = space.get_defaults()
    
    # Fitness = -(distancia cuadrática a defaults)
    # Máximo fitness = 0 cuando params == defaults
    def rastrigin_fitness(params):
        distance_sq = 0.0
        for name, value in params.items():
            param_def = space.params[name]
            default_val = defaults[name]
            range_val = param_def.max_value - param_def.min_value
            normalized_diff = (value - default_val) / range_val
            distance_sq += normalized_diff ** 2
        
        return -distance_sq  # Negativo porque queremos minimizar distancia
    
    config = GAConfig(
        population_size=32,
        num_generations=10,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.15,
        mutation_sigma_pct=0.10,
        elitism_count=2,
        early_stopping_generations=4,
        seed=42
    )
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config,
        fitness_function=rastrigin_fitness
    )
    
    best, history = ga.optimize()
    
    print("\n=== GA OPTIMIZATION RESULTS ===")
    print(f"Generations run: {len(history)}")
    print(f"Best fitness: {best.fitness:.6f}")
    print(f"Optimal fitness: 0.0 (params == defaults)")
    
    # Verificar convergencia
    first_gen = history[0]
    last_gen = history[-1]
    
    print(f"\nGen 0: best={first_gen['best_fitness']:.6f}, avg={first_gen['avg_fitness']:.6f}")
    print(f"Gen {len(history)-1}: best={last_gen['best_fitness']:.6f}, avg={last_gen['avg_fitness']:.6f}")
    
    # GA debe mejorar
    assert last_gen['best_fitness'] > first_gen['best_fitness']
    
    # Debe estar cerca del óptimo (fitness ≈ 0)
    assert best.fitness > -0.01  # Muy cerca de 0


if __name__ == "__main__":
    test_ga_rastrigin_function()
    print("\n✅ Manual GA test passed")
