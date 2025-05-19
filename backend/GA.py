import random
import json
import ast
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np  # You forgot to import numpy! Needed for np.argsort
import copy  # Needed for deep copying schedules in mutation

from lib import metrics 

# Genetic Algorithm class for optimizing athlete training schedules
class GeneticAthleteOptimizer:
    def __init__(self, athlete_metrics, actions, position):
        """
        Initialize the optimizer with athlete's metrics, available actions, and position-specific data.
        """
        self.athlete = athlete_metrics  # Dictionary of athlete stats (e.g., injury history, chronic workload)
        self.actions = actions[position]  # Actions are split by player position (Defender, Midfielder, etc.)
        self.position = position

        # Genetic Algorithm Hyperparameters
        self.pop_size = 50          # Number of schedules in each generation
        self.generations = 100      # How many generations to run evolution
        self.mutation_rate = 0.15   # 15% chance to mutate each gene (day)
        self.elitism = 0.1          # Top 10% of schedules are carried forward unchanged

        # Fitness calculation weights:
        # These control how much we care about each part (performance, injury, constraint violations)
        self.weights = {
            'performance': 0.7,    # Higher performance = good
            'injury_risk': -0.3,   # Higher injury risk = bad (so negative weight)
            'constraints': -0.5    # Breaking training rules = bad
        }

    def generate_individual(self):
        """
        Generate a random 7-day schedule for an athlete.
        Each day is either 'train' or 'recover' randomly.
        """
        schedule = []
        categories = list(self.actions.keys())  # Training categories like Strength, Speed, etc.

        for day in range(7):  # For each day of the week
            if random.random() < 0.7:  # 70% chance to have a training session
                category = random.choice(categories)  # Random category
                exercise = random.choice(list(self.actions[category].keys()))  # Random exercise in that category
                intensity = random.randint(1, 5)  # Training intensity from 1 to 5
                duration = random.randint(30, 120)  # Duration between 30 to 120 minutes
                schedule.append(('train', category, exercise, intensity, duration))
            else:
                schedule.append(('recover', None, None, 0, 0))  # Recovery day

        return schedule

    def calculate_injury_risk(self, schedule):
        """
        Calculate the injury risk based on acute load, chronic workload, recovery days, etc.
        """
        # Acute Load = total duration of training this week
        acute_load = sum(duration for (t, _, _, _, duration) in schedule if t == 'train')
        chronic_load = self.athlete.get('chronic_workload', 300)  # Past month average workload (default 300)

        acwr = acute_load / chronic_load if chronic_load > 0 else 1.0  # Acute:Chronic Workload Ratio

        # Injury risk formula
        risk = (
            0.5 * min(max(acwr, 0.8), 1.5) +  # ACWR heavily weighted
            0.3 * (sum(intensity for (t, _, _, intensity, _) in schedule if t == 'train') / 35) +  # Training intensity
            0.1 * (4 - sum(1 for day in schedule if day[0] == 'recover')) +  # Few recovery days = more risk
            0.1 * (self.athlete['injury_history'] / 5)  # Athlete's injury history matters too
        )
        return min(max(risk, 0), 1.0)  # Clamp between 0 and 1

    def predict_performance(self, schedule):
        """
        Predict a performance score based on the training exercises completed.
        """
        deltas = defaultdict(float)  # How much each metric (like tackles, passing) improved

        for day in schedule:
            if day[0] == 'train':
                _, category, exercise, intensity, _ = day
                effects = self.actions[category][exercise].get(intensity, {})  # Effect of this exercise

                for metric, delta in effects.items():
                    deltas[metric] += delta

        # Calculate a total performance score
        performance = 0
        for metric, delta in deltas.items():
            # Different positions value different metrics more
            if metric in ['tackles_won', 'clearances'] and self.position == 'Defender':
                performance += delta * 0.3
            elif metric == 'passing_accuracy':
                performance += delta * 0.2
            # You can add more metrics for midfielders, attackers, etc.

        return performance

    def check_constraints(self, schedule):
        """
        Check if the schedule violates important constraints:
        - Must have at least 2 recovery days
        - Can't train more than 3 days in a row
        """
        violations = 0

        # 1. Check number of recovery days
        recovery_days = sum(1 for day in schedule if day[0] == 'recover')
        if recovery_days < 2:
            violations += (2 - recovery_days) * 0.5  # Penalty if not enough rest

        # 2. Check for too many consecutive training days
        consecutive_train = 0
        max_consecutive = 0
        for day in schedule:
            if day[0] == 'train':
                consecutive_train += 1
                max_consecutive = max(max_consecutive, consecutive_train)
            else:
                consecutive_train = 0  # Reset on recovery day
        if max_consecutive > 3:
            violations += (max_consecutive - 3) * 0.3  # Penalty for too much back-to-back training

        return violations

    def fitness(self, schedule):
        """
        Calculate a fitness score for the schedule.
        Higher fitness = better schedule.
        """
        injury_risk = self.calculate_injury_risk(schedule)
        performance = self.predict_performance(schedule)
        constraints = self.check_constraints(schedule)

        # Weighted sum of all parts
        return (
            self.weights['performance'] * performance +
            self.weights['injury_risk'] * injury_risk +
            self.weights['constraints'] * constraints
        )

    def crossover(self, parent1, parent2):
        """
        Combine two parents to create a new child schedule.
        For each day, randomly take from parent1 or parent2.
        """
        child = []
        for g1, g2 in zip(parent1, parent2):
            child.append(g1 if random.random() < 0.5 else g2)
        return child

    def mutate(self, schedule):
        """
        Apply random changes (mutations) to a schedule.
        Makes the population more diverse.
        """
        new_schedule = copy.deepcopy(schedule)  # Make a deep copy so we don't affect the original

        for i in range(len(new_schedule)):
            if random.random() < self.mutation_rate:
                mutation_type = random.choice([
                    'change_exercise',
                    'change_intensity',
                    'change_duration',
                    'swap_days',
                    'add_recovery'
                ])

                if mutation_type == 'change_exercise':
                    category = random.choice(list(self.actions.keys()))
                    exercise = random.choice(list(self.actions[category].keys()))
                    new_schedule[i] = ('train', category, exercise, new_schedule[i][3], new_schedule[i][4])

                elif mutation_type == 'change_intensity':
                    new_intensity = min(max(new_schedule[i][3] + random.choice([-2, -1, 1, 2]), 1), 5)
                    new_schedule[i] = (*new_schedule[i][:3], new_intensity, new_schedule[i][4])

                elif mutation_type == 'add_recovery' and new_schedule[i][0] == 'train':
                    new_schedule[i] = ('recover', None, None, 0, 0)

                # (Swap days and change duration not fully implemented yet)

        return new_schedule

    def evolve(self):
        """
        Run the Genetic Algorithm to evolve better schedules.
        """
        # 1. Start with random population
        population = [self.generate_individual() for _ in range(self.pop_size)]
        best_fitness = -float('inf')  # Best score so far
        best_schedule = None
        fitness_history = []  # Track fitness over generations

        for generation in range(self.generations):
            # 2. Calculate fitness for all individuals
            fitness_scores = [self.fitness(ind) for ind in population]

            # 3. Update best schedule found
            current_best = max(fitness_scores)
            if current_best > best_fitness:
                best_fitness = current_best
                best_schedule = population[fitness_scores.index(current_best)]

            fitness_history.append(best_fitness)

            # 4. Select parents
            elite_size = max(1, int(self.elitism * self.pop_size))
            elite_indices = np.argsort(fitness_scores)[-elite_size:]  # Best individuals
            elite = [population[i] for i in elite_indices]

            parents = []
            for _ in range(self.pop_size - elite_size):
                candidates = random.sample(range(len(population)), min(3, len(population)))
                winner = max(candidates, key=lambda x: fitness_scores[x])
                parents.append(population[winner])

            # 5. Create new population with crossover + mutation
            offspring = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    child1 = self.crossover(parents[i], parents[i+1])
                    child2 = self.crossover(parents[i+1], parents[i])
                    offspring.append(self.mutate(child1))
                    offspring.append(self.mutate(child2))
                else:
                    offspring.append(self.mutate(parents[i]))

            # 6. New generation
            population = elite + offspring

        # After all generations, return the best schedule and fitness history
        return best_schedule, fitness_history

    def visualize_progress(self):
        """Visualize fitness progress over generations."""
        plt.figure(figsize=(10, 6))
        plt.plot(self.best_fitness_history, label='Best Fitness')
        plt.plot(self.average_fitness_history, label='Average Fitness')
        plt.plot(self.worst_fitness_history, label='Worst Fitness')
        plt.title('Fitness Progress Over Generations')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend()
        plt.grid(True)
        plt.show()










def run_genetic():
    # Example athlete metrics
    athlete_metrics = {
        'position': 'Defender',
        'chronic_workload': 300,
        'injury_history': 1,
        'current_fatigue': 4,
        'recovery_index': 6
    }

    try:
        # Load actions from file
        with open('defender_actions_realistic.txt', 'r') as f:
            content = f.read()
            # Find where the dictionary starts and ends
            dict_start = content.find('{')
            dict_end = content.rfind('}') + 1
            dict_str = content[dict_start:dict_end]

            print("Attempting to parse actions dictionary...")
            actions = ast.literal_eval(dict_str)
            print("Successfully parsed actions dictionary!")

            # Verify we have Defender data
            if 'Defender' not in actions:
                print("Error: 'Defender' key not found in actions dictionary")
                return

    except Exception as e:
        print(f"Error loading actions file: {e}")
        return

    # Initialize the optimizer
    print("Initializing optimizer...")
    optimizer = GeneticAthleteOptimizer(athlete_metrics, actions, position='Defender')

 # Run the genetic algorithm
    print("Running genetic algorithm...")
    best_schedule, fitness_history = optimizer.evolve()

    if not best_schedule:
        print("Error: No schedule was generated")
        return

    # Print results
    print("\n=== OPTIMIZED WEEKLY TRAINING SCHEDULE ===")
    print("(Balancing performance gains with injury risk)")
    print("Day | Activity          | Exercise               | Intensity | Duration")
    print("-" * 65)

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(best_schedule):
        if day[0] == 'train':
            _, category, exercise, intensity, duration = day
            print(f"{day_names[i]:<8} | Training ({category:<8}) | {exercise:<20} | {intensity}/5     | {duration} min")
        else:
            print(f"{day_names[i]:<8} | Recovery Day         | -                    | -        | -")

    # Calculate metrics
    perf_score = optimizer.predict_performance(best_schedule)
    injury_risk = optimizer.calculate_injury_risk(best_schedule)
    constraints = optimizer.check_constraints(best_schedule)

    print("\n=== SCHEDULE METRICS ===")
    print(f"Predicted Performance Gain: {perf_score:.2f} (higher is better)")
    print(f"Injury Risk Score: {injury_risk:.2f}/1.0 (lower is better)")
    print(f"Constraint Violations: {constraints:.2f} (0 is perfect)")

    # Show fitness progression
    print("\n=== GENETIC ALGORITHM PROGRESS ===")
    print(f"Initial Fitness: {fitness_history[0]:.2f}")
    print(f"Final Fitness: {fitness_history[-1]:.2f}")
    print(f"Improvement: {(fitness_history[-1] - fitness_history[0])/abs(fitness_history[0])*100:.1f}%")

    # Plot fitness over generations
    plt.figure(figsize=(10, 5))
    plt.plot(fitness_history)
    plt.title('Fitness Progress Over Generations')
    plt.xlabel('Generation')
    plt.ylabel('Fitness Score')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    print("Starting genetic algorithm optimization...")
    run_genetic()
    print("Optimization complete!")
    
