"""
Genetic Algorithm para optimización de parámetros.
Spec: Codex PARTE 2
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional, Tuple
import random
import copy
import math
from src.optimization.param_space import ParamSpace, ParamType
from src.optimization.constraints import project_constraints


@dataclass
class Individual:
    """
    Individuo en la población del GA.
    """
    params: Dict[str, Any]
    fitness: Optional[float] = None


@dataclass
class GAConfig:
    """
    Configuración del Genetic Algorithm.
    Spec: Codex PARTE 2.1
    """
    population_size: int = 32
    num_generations: int = 8
    tournament_size: int = 3
    crossover_rate: float = 0.8
    mutation_rate: float = 0.15
    mutation_sigma_pct: float = 0.10
    elitism_count: int = 2
    early_stopping_generations: int = 3
    seed: Optional[int] = None


def population_initialize(
    param_space: ParamSpace,
    population_size: int,
    seed: Optional[int] = None
) -> List[Individual]:
    """
    Inicializa población aleatoria.
    
    Spec: Codex PARTE 2.2
    
    Args:
        param_space: Espacio de parámetros
        population_size: Tamaño de población
        seed: Random seed
        
    Returns:
        Lista de individuos con params aleatorios, fitness=None
    """
    if seed is not None:
        random.seed(seed)
        
    population = []
    
    for _ in range(population_size):
        # Generar params aleatorios
        # Nota: sample_random ya usa random, así que el seed global aplica
        params = param_space.sample_random(seed=None)  
        
        # Proyectar a espacio válido (constraints)
        params = project_constraints(params, param_space)
        
        # Crear individuo
        ind = Individual(params=params, fitness=None)
        population.append(ind)
        
    return population


def tournament_selection(
    population: List[Individual],
    tournament_size: int,
    seed: Optional[int] = None
) -> Individual:
    """
    Selección por torneo.
    
    Spec: Codex PARTE 2.3
    
    Elige tournament_size individuos al azar,
    retorna el de mejor fitness.
    
    Args:
        population: Población actual
        tournament_size: Número de competidores
        seed: Random seed
        
    Returns:
        Individuo ganador del torneo
    """
    if seed is not None:
        random.seed(seed)
        
    # Validar que todos tengan fitness calculado
    # (En teoría siempre deberían tenerlo en este punto)
    
    # Seleccionar competidores al azar
    competitors = random.sample(population, tournament_size)
    
    # Ganador es el que tiene mayor fitness
    # Nota: Si fitness es None, fallará. Asumimos fitness válido.
    winner = max(competitors, key=lambda ind: ind.fitness if ind.fitness is not None else float('-inf'))
    
    return winner


def crossover_uniform(
    parent1: Individual,
    parent2: Individual,
    param_space: ParamSpace,
    seed: Optional[int] = None
) -> Individual:
    """
    Crossover uniforme.
    
    Spec: Codex PARTE 2.4
    
    Para cada parámetro, elige aleatoriamente de parent1 o parent2.
    
    Args:
        parent1: Padre 1
        parent2: Padre 2
        param_space: Espacio de parámetros
        seed: Random seed
        
    Returns:
        Hijo con genes mezclados, fitness=None
    """
    if seed is not None:
        random.seed(seed)
        
    child_params = {}
    
    for param_name in param_space.params:
        if random.random() < 0.5:
            child_params[param_name] = parent1.params[param_name]
        else:
            child_params[param_name] = parent2.params[param_name]
            
    # Asegurar constraints (aunque si vienen de padres válidos, deberían serlo)
    child_params = project_constraints(child_params, param_space)
    
    return Individual(params=child_params, fitness=None)


def mutate_gaussian(
    individual: Individual,
    param_space: ParamSpace,
    mutation_rate: float,
    sigma_pct: float,
    seed: Optional[int] = None
) -> Individual:
    """
    Mutación gaussiana.
    
    Spec: Codex PARTE 2.5
    
    Para cada parámetro:
    - Con probabilidad mutation_rate:
      - Añadir ruido gaussiano: N(0, sigma)
      - sigma = sigma_pct * (max - min)
    
    Args:
        individual: Individuo a mutar
        param_space: Espacio de parámetros
        mutation_rate: Probabilidad de mutar cada param
        sigma_pct: Desviación estándar como % del rango
        seed: Random seed
        
    Returns:
        Individuo mutado, fitness=None
    """
    if seed is not None:
        random.seed(seed)
        
    mutated_params = copy.deepcopy(individual.params)
    
    for param_name, param_def in param_space.params.items():
        if param_name not in mutated_params:
            continue
            
        if random.random() < mutation_rate:
            # Calcular sigma
            rng = float(param_def.max_value) - float(param_def.min_value)
            sigma = sigma_pct * rng
            
            # Ruido gaussiano
            noise = random.gauss(0, sigma)
            
            # Aplicar ruido
            mutated_params[param_name] += noise
            
    # Proyectar para clip y constraints (importante tras mutación)
    mutated_params = project_constraints(mutated_params, param_space)
    
    return Individual(params=mutated_params, fitness=None)


class GeneticAlgorithm:
    """
    Genetic Algorithm para optimización de hiperparámetros.
    
    Spec: Codex PARTE 2
    """
    
    def __init__(
        self,
        param_space: ParamSpace,
        config: GAConfig,
        fitness_function: Callable[[Dict[str, Any]], float]
    ):
        """
        Args:
            param_space: Espacio de parámetros
            config: Configuración del GA
            fitness_function: Función que dado params retorna fitness
        """
        self.param_space = param_space
        self.config = config
        self.fitness_function = fitness_function
        
        if config.seed is not None:
            random.seed(config.seed)
    
    def evaluate_individual(self, individual: Individual) -> None:
        """
        Evalúa fitness de un individuo (in-place).
        
        Args:
            individual: Individuo a evaluar
        """
        # Si ya tiene fitness, podríamos saltar, pero por ahora re-calculamos
        # para asegurar consistencia si la función es estocástica (usualmente no)
        fitness = self.fitness_function(individual.params)
        individual.fitness = fitness
    
    def optimize(self) -> Tuple[Individual, List[Dict]]:
        """
        Ejecuta el GA y retorna el mejor individuo encontrado.
        
        Spec: Codex PARTE 2.6
        
        Returns:
            (best_individual, history)
            
            history: List de dicts con info de cada generación:
                {
                    "gen": int,
                    "best_fitness": float,
                    "avg_fitness": float,
                    "evaluations": int
                }
        """
        history = []
        
        # 1. Inicialización (Gen 0)
        population = population_initialize(
            self.param_space,
            self.config.population_size,
            seed=self.config.seed
        )
        
        # 2. Evaluar población inicial
        for ind in population:
            self.evaluate_individual(ind)
            
        evaluations_count = len(population)
        
        # Stats Gen 0
        current_best = max(population, key=lambda ind: ind.fitness if ind.fitness is not None else float('-inf'))
        finite_fitnesses = [ind.fitness for ind in population if ind.fitness is not None and math.isfinite(ind.fitness)]
        avg_fitness = sum(finite_fitnesses) / len(finite_fitnesses) if finite_fitnesses else float('-inf')
        
        best_ever = copy.deepcopy(current_best)
        
        history.append({
            "gen": 0,
            "best_fitness": current_best.fitness,
            "avg_fitness": avg_fitness,
            "evaluations": evaluations_count
        })
        
        best_str = f"{current_best.fitness:.4f}" if math.isfinite(current_best.fitness) else "-inf"
        avg_str = f"{avg_fitness:.4f}" if math.isfinite(avg_fitness) else "-inf"
        print(f"Generation 0: Best Fitness={best_str}, Avg={avg_str}")
        
        generations_without_improvement = 0
        
        # Loop de generaciones (1 a N-1)
        for gen in range(1, self.config.num_generations):
            
            # C) Elitism (usamos pop anterior)
            sorted_pop = sorted(
                population, 
                key=lambda ind: ind.fitness if ind.fitness is not None else float('-inf'), 
                reverse=True
            )
            
            elites = sorted_pop[:self.config.elitism_count]
            # Deepcopy para seguridad
            elites = [copy.deepcopy(elite) for elite in elites]
            
            # D) Offspring
            offspring = []
            needed = self.config.population_size - len(elites)
            
            while len(offspring) < needed:
                # Selection from PREVIOUS population
                parent1 = tournament_selection(population, self.config.tournament_size)
                parent2 = tournament_selection(population, self.config.tournament_size)
                
                # Crossover
                if random.random() < self.config.crossover_rate:
                    child = crossover_uniform(parent1, parent2, self.param_space)
                else:
                    child = Individual(params=copy.deepcopy(parent1.params), fitness=None)
                
                # Mutation
                child = mutate_gaussian(
                    child, 
                    self.param_space,
                    self.config.mutation_rate,
                    self.config.mutation_sigma_pct
                )
                
                offspring.append(child)
            
            # E) Evaluar Offspring
            for child in offspring:
                self.evaluate_individual(child)
                evaluations_count += 1
                
            # F) Nueva población
            population = elites + offspring
            
            # A) Stats de la NUEVA población
            current_best = max(population, key=lambda ind: ind.fitness if ind.fitness is not None else float('-inf'))
            finite_fitnesses = [ind.fitness for ind in population if ind.fitness is not None and math.isfinite(ind.fitness)]
            avg_fitness = sum(finite_fitnesses) / len(finite_fitnesses) if finite_fitnesses else float('-inf')
            
            history.append({
                "gen": gen,
                "best_fitness": current_best.fitness,
                "avg_fitness": avg_fitness,
                "evaluations": evaluations_count
            })
            
            best_str = f"{current_best.fitness:.4f}" if math.isfinite(current_best.fitness) else "-inf"
            avg_str = f"{avg_fitness:.4f}" if math.isfinite(avg_fitness) else "-inf"
            print(f"Generation {gen}: Best Fitness={best_str}, Avg={avg_str}")
            
            # B) Early Stopping Check & Updates
            if current_best.fitness > best_ever.fitness:
                best_ever = copy.deepcopy(current_best)
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
                
            if generations_without_improvement >= self.config.early_stopping_generations:
                # Stop early
                break
            
        return best_ever, history
