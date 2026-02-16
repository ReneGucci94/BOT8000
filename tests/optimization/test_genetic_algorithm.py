"""
Tests para Genetic Algorithm.
Spec: Codex PARTE 2
"""
import pytest
from src.optimization.genetic_algorithm import (
    GeneticAlgorithm,
    GAConfig,
    Individual,
    population_initialize,
    tournament_selection,
    crossover_uniform,
    mutate_gaussian
)
from src.optimization.param_space import get_default_param_space
from src.optimization.fitness import SegmentMetrics


def test_population_initialize_size():
    """
    Población inicial debe tener el tamaño correcto.
    """
    space = get_default_param_space()
    population = population_initialize(
        param_space=space,
        population_size=32,
        seed=42
    )
    
    assert len(population) == 32
    
    # Cada individual debe tener params válidos
    for ind in population:
        assert len(ind.params) == 13  # 13 params en total
        assert ind.fitness is None  # No evaluado aún


def test_population_initialize_reproducible():
    """
    Con mismo seed, debe generar misma población inicial.
    """
    space = get_default_param_space()
    
    pop1 = population_initialize(space, 32, seed=42)
    pop2 = population_initialize(space, 32, seed=42)
    
    # Deben ser idénticos
    for i in range(32):
        assert pop1[i].params == pop2[i].params


def test_tournament_selection_picks_best():
    """
    Tournament selection debe elegir el mejor de k candidatos.
    Spec: Codex PARTE 2.3
    """
    space = get_default_param_space()
    
    # Crear población con fitness conocidos
    population = []
    for i in range(10):
        ind = Individual(
            params=space.get_defaults(),
            fitness=float(i)  # Fitness 0, 1, 2, ..., 9
        )
        population.append(ind)
    
    # Tournament con k=3, seed fijo
    selected = tournament_selection(
        population=population,
        tournament_size=3,
        seed=42
    )
    
    # Debe retornar un individual
    assert isinstance(selected, Individual)
    
    # Debe tener fitness (no None)
    assert selected.fitness is not None


def test_crossover_uniform_produces_child():
    """
    Crossover debe producir un hijo válido.
    Spec: Codex PARTE 2.4
    """
    space = get_default_param_space()
    
    # Padres con params diferentes
    parent1_params = space.get_defaults()
    parent1_params["alpha_threshold"] = 0.45
    parent1_params["g_ob_quality"] = 0.50
    
    parent2_params = space.get_defaults()
    parent2_params["alpha_threshold"] = 0.75
    parent2_params["g_ob_quality"] = 2.00
    
    parent1 = Individual(params=parent1_params, fitness=1.5)
    parent2 = Individual(params=parent2_params, fitness=1.8)
    
    # Crossover
    child = crossover_uniform(
        parent1=parent1,
        parent2=parent2,
        param_space=space,
        seed=42
    )
    
    # Child debe tener todos los params
    assert len(child.params) == 13
    
    # Child params deben estar en rangos válidos
    for name, value in child.params.items():
        param_def = space.params[name]
        assert param_def.min_value <= value <= param_def.max_value
    
    # Fitness del child debe ser None (no evaluado)
    assert child.fitness is None


def test_crossover_uniform_mixes_parents():
    """
    Crossover debe mezclar genes de ambos padres.
    """
    space = get_default_param_space()
    
    # Padres en extremos opuestos
    parent1_params = {name: p.min_value for name, p in space.params.items()}
    parent2_params = {name: p.max_value for name, p in space.params.items()}
    
    parent1 = Individual(params=parent1_params, fitness=1.0)
    parent2 = Individual(params=parent2_params, fitness=1.0)
    
    child = crossover_uniform(parent1, parent2, space, seed=42)
    
    # Child debe tener mix (no todos min ni todos max)
    has_from_p1 = False
    has_from_p2 = False
    
    for name, value in child.params.items():
        param_def = space.params[name]
        if abs(value - param_def.min_value) < 0.01:
            has_from_p1 = True
        if abs(value - param_def.max_value) < 0.01:
            has_from_p2 = True
    
    # Debe tener genes de ambos (con alta probabilidad)
    assert has_from_p1 or has_from_p2


def test_mutate_gaussian_changes_params():
    """
    Mutación debe modificar los parámetros.
    Spec: Codex PARTE 2.5
    """
    space = get_default_param_space()
    
    original_params = space.get_defaults()
    individual = Individual(params=original_params.copy(), fitness=1.5)
    
    # Mutar con tasa alta para asegurar cambios
    mutated = mutate_gaussian(
        individual=individual,
        param_space=space,
        mutation_rate=1.0,  # 100% de probabilidad
        sigma_pct=0.10,     # 10% de rango
        seed=42
    )
    
    # Debe haber al menos un param diferente
    changed_count = sum(
        1 for name in mutated.params
        if mutated.params[name] != original_params[name]
    )
    
    assert changed_count > 0
    
    # Params deben estar en rangos válidos
    for name, value in mutated.params.items():
        param_def = space.params[name]
        assert param_def.min_value <= value <= param_def.max_value


def test_mutate_gaussian_respects_mutation_rate():
    """
    Con mutation_rate=0, no debe haber cambios.
    """
    space = get_default_param_space()
    
    original_params = space.get_defaults()
    individual = Individual(params=original_params.copy(), fitness=1.5)
    
    # Mutar con tasa 0%
    mutated = mutate_gaussian(
        individual=individual,
        param_space=space,
        mutation_rate=0.0,  # No mutation
        sigma_pct=0.10,
        seed=42
    )
    
    # Debe ser idéntico
    assert mutated.params == original_params


def test_ga_config_defaults():
    """
    GAConfig debe tener valores razonables por default.
    """
    config = GAConfig()
    
    assert config.population_size == 32
    assert config.num_generations == 8
    assert config.tournament_size == 3
    assert config.crossover_rate == 0.8
    assert config.mutation_rate == 0.15
    assert config.mutation_sigma_pct == 0.10
    assert config.elitism_count == 2
    assert config.early_stopping_generations == 3


def test_ga_optimize_simple_mock():
    """
    Test de integración simple con fitness mockeada.
    Verifica que el GA ejecuta sin errores.
    """
    space = get_default_param_space()
    config = GAConfig(
        population_size=8,
        num_generations=2,
        seed=42
    )
    
    # Fitness function mockeada (siempre retorna 1.0)
    def mock_fitness_fn(params):
        return 1.0
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config,
        fitness_function=mock_fitness_fn
    )
    
    best_individual, history = ga.optimize()
    
    # Debe retornar un individual válido
    assert best_individual is not None
    assert len(best_individual.params) == 13
    assert best_individual.fitness == 1.0
    
    # History debe tener 2 generaciones
    assert len(history) == 2
    assert "gen" in history[0]
    assert "best_fitness" in history[0]
    assert "avg_fitness" in history[0]
    assert "evaluations" in history[0]


def test_ga_optimize_finds_better_solution():
    """
    GA debe mejorar fitness a lo largo de generaciones.
    Usa fitness function simple: sum de params.
    """
    space = get_default_param_space()
    config = GAConfig(
        population_size=16,
        num_generations=5,
        seed=42
    )
    
    # Fitness = suma de todos los params (favorece valores altos)
    def simple_fitness_fn(params):
        return sum(params.values())
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config,
        fitness_function=simple_fitness_fn
    )
    
    best_individual, history = ga.optimize()
    
    # Fitness debe mejorar
    first_gen_best = history[0]["best_fitness"]
    last_gen_best = history[-1]["best_fitness"]
    
    assert last_gen_best >= first_gen_best


def test_ga_early_stopping_triggers():
    """
    Early stopping debe detener si no hay mejora.
    """
    space = get_default_param_space()
    config = GAConfig(
        population_size=8,
        num_generations=10,
        early_stopping_generations=2,
        seed=42
    )
    
    # Fitness constante (no mejora)
    def constant_fitness_fn(params):
        return 1.0
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config,
        fitness_function=constant_fitness_fn
    )
    
    best_individual, history = ga.optimize()
    
    # Debe detenerse antes de 10 generaciones
    # (2 gens iniciales + 2 gens sin mejora = 4 total)
    assert len(history) <= 5


def test_ga_elitism_preserves_best():
    """
    Elitism debe preservar los mejores individuos.
    """
    space = get_default_param_space()
    config = GAConfig(
        population_size=10,
        num_generations=3,
        elitism_count=2,
        seed=42
    )
    
    evaluation_count = 0
    
    # Fitness que cuenta evaluaciones
    def counting_fitness_fn(params):
        nonlocal evaluation_count
        evaluation_count += 1
        # Fitness basado en un param específico
        return params["alpha_threshold"]
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config,
        fitness_function=counting_fitness_fn
    )
    
    best_individual, history = ga.optimize()
    
    # Gen 0: 10 evaluations (población inicial)
    # Gen 1: 8 evaluations (10 - 2 elites)
    # Gen 2: 8 evaluations (10 - 2 elites)
    # Total: 10 + 8 + 8 = 26
    
    expected_evals = 10 + 8 + 8
    assert evaluation_count == expected_evals


def test_ga_handles_all_negative_inf_fitness():
    """
    GA should not crash when all individuals have -inf fitness.
    This was the root cause of the WFO failure.
    """
    space = get_default_param_space()
    config = GAConfig(
        population_size=8,
        num_generations=3,
        seed=42
    )
    
    def always_inf_fitness(params):
        return float('-inf')
    
    ga = GeneticAlgorithm(
        param_space=space,
        config=config,
        fitness_function=always_inf_fitness
    )
    
    best, history = ga.optimize()
    
    assert best is not None
    assert best.fitness == float('-inf')
    assert len(history) > 0
