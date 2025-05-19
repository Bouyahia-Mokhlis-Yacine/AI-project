from lib import Node , Training_Problem , metrics

class Greedy_search :
    def __init__(self , initial_state):
        self.initial_state = initial_state
        self.state = initial_state
        self.problem = Training_Problem(initial_state)
        self.path = []


    def search(self):
        current_state = self.state
        best_score = 0.0
        i = 0
        for i in range(30):
            neighbors = self.problem.generate_neighbors(current_state)
            best_neighbor = None
            best_score = float('-inf')
            i = i + 1
            for neighbor in neighbors:
                score = self.heuristic(neighbor)
                if score > best_score:
                    best_score = score
                    best_neighbor = neighbor
                    print(f"{i}  Best Neighbor: {best_neighbor.action} with score: {best_score} injury risk: {self.problem.evaluate_injury_risk(best_neighbor)} performance: {self.problem.evaluate_performance(best_neighbor)}")
            current_state = best_neighbor
            self.path.append(current_state.action)
        self.state = current_state
        return current_state


    def heuristic(self, state):
        """Balances injury risk and performance gain with realistic weights."""
        injury = self.problem.evaluate_injury_risk(state)
        initial_perf = self.problem.evaluate_performance(self.initial_state)
        current_perf = self.problem.evaluate_performance(state)
        performance_gain = current_perf - initial_perf
        
        # Injury penalty (quadratic scaling for high risk)
        injury_penalty = 0
        if injury < 10:
            injury_penalty = -injury
        elif 10 <= injury < 30:
            injury_penalty = -injury*2  # Moderate penalty for moderate risk
        else:  # 30%+ injury risk
            injury_penalty = -injury *2  # Strong penalty for high risk
        
        # Performance reward (diminishing returns)
        performance_reward = 0
        if performance_gain > 0:
            performance_reward = performance_gain*50  # Log scale
        
        # Combine with weights
        return injury_penalty + performance_reward


    def get_path(self):
        return self.path
    def get_final_state(self):
        return self.state
    def get_initial_metrics(self):
        return self.initial_state.metrics
    def get_final_performance(self):
        return self.problem.evaluate_performance(self.state)
    def get_final_injury_risk(self):
        return self.problem.evaluate_injury_risk(self.state)
    def get_final_metrics(self):
        return self.state.metrics



player = Node(
    position="Goalkeeper",
    metrics=metrics.copy(),  # Your metrics dict
    action=None
)



problem = Training_Problem(player)
search = Greedy_search(player)

final_state = search.search()
print("Final State: ", final_state)
print("Final Performance: ", search.get_final_performance())
print("Final Injury Risk: ", search.get_final_injury_risk())
print("Initial Metrics: ", search.get_initial_metrics())
print("Final Metrics: ", search.get_final_metrics())
print("Path: ", search.get_path())
state = Node("Goalkeeper", metrics )
problem = Training_Problem(state)
