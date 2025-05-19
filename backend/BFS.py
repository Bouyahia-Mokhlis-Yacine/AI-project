from lib import Node , Training_Problem , metrics
from collections import deque


class BFS:
    def __init__(self , initial_state):
        self.initial_state = initial_state
        self.state = initial_state
        self.problem = Training_Problem(initial_state)
        self.path = []

    def set_initial_state(self, state):
        self.state = state

    def get_initial_state(self):
            return self.state
    def search(self):
        # Initialize with starting state
        initial_state = self.state
        initial_perf = self.problem.evaluate_performance(initial_state)
        # Immediate goal check for initial state
        if initial_perf >= initial_perf * 1.05:
            return initial_state, self.path
        
        # BFS infrastructure


        frontier_states = set()
        frontier = deque([(initial_state, self.path)])
        frontier_states.add(initial_state)
        explored = set()

        while frontier:
            if frontier_states == 0:
                break
            current_state, current_path = frontier.popleft()
            frontier_states.remove(current_state)
            explored.add(current_state)

            # Generate and process neighbors
            neighbors = self.problem.generate_neighbors(current_state)
            for neighbor in neighbors:
                # Skip already queued/explored states
                if neighbor in frontier_states or neighbor in explored:
                    continue

                # Goal check for 5% improvement
                neighbor_perf = self.problem.evaluate_performance(neighbor)
                if neighbor_perf >= initial_perf * 1.01:
                    self.state = neighbor
                    self.path = current_path + [neighbor.action]
                    print(f"Found solution with performance: {neighbor_perf} and path is : {self.path}")
                    return neighbor

                # Add to frontier
                new_path = current_path + [neighbor.action]
                frontier.append((neighbor, new_path))
                frontier_states.add(neighbor)

        # No solution found
        print("No path achieving 5% improvement found")
        return None
    


player = Node(
    position="Goalkeeper",
    metrics=metrics.copy(),  # Your metrics dict
    action=None
)

problem = Training_Problem(player)
search = BFS(player)

final_state = search.search()
print("Final State: ", final_state)
print("Final Performance: ", search.get_final_performance())
print("Final Injury Risk: ", search.get_final_injury_risk())
print("Initial Metrics: ", search.get_initial_metrics())
print("Final Metrics: ", search.get_final_metrics())
print("Path: ", search.get_path())





from flask import Flask, request, session, redirect, url_for, render_template

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    result =   search.get_path()
    session['result'] = result
    return '', 204  # No content, just redirect client

@app.route('/page2')
def page2():
    result = session.get('result', 'No result found')
    return render_template('page2.html', result=result)
