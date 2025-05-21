import json
import itertools
import heapq
from collections import defaultdict
from copy import copy
import time
from lib import metrics 
import os

current_dir = os.path.dirname(__file__)


file_path = os.path.join(current_dir, "..", "project", "defender_actions_realistic.txt")


# Load actions from file
with open(file_path) as f:
    actions_data = f.read()
actions = eval(actions_data)["Defender"]  # If you're sure the data is safe; otherwise use json

# Extract all training sessions
def get_all_sessions(actions):
    sessions = []
    for category in actions:
        for subcategory in actions[category]:
            for level in actions[category][subcategory]:
                sessions.append((category, subcategory, level))
    return sessions

# Get the effects of a session
def get_session_effect(session, actions):
    category, subcategory, level = session
    return actions[category][subcategory][level]

# Scoring function
def session_score(effects):
    return (
        effects.get("tackles_won", 0)
        + effects.get("clearances", 0)
        + effects.get("passing_accuracy", 0)
        + effects.get("duels_won_percent", 0)
        - 2 * effects.get("errors_leading_to_shots_goals", 0)
    )

# Fatigue cost function
def session_fatigue(effects):
    return (
        effects.get("mental_fatigue", 0)
        + effects.get("training_load.session_intensity", 0)
    )

# Create possible session plans for a day (0, 1, or 2 sessions)
def generate_domain(sessions):
    domain = [()]  # rest day
    domain += [(s,) for s in sessions]
    domain += list(itertools.combinations(sessions, 2))
    return domain

# Evaluate full day plan
def evaluate_day(plan, actions):
    total_score = 0
    total_fatigue = 0
    for session in plan:
        effects = get_session_effect(session, actions)
        total_score += session_score(effects)
        total_fatigue += session_fatigue(effects)
    return total_score, total_fatigue

# CSP Optimizer Class
class OptimizedTrainingCSP:
    def __init__(self, variables, domains, max_fatigue=45):
        self.variables = variables
        self.domains = domains
        self.max_fatigue = max_fatigue
        self.best_solution = None
        self.best_score = -1

    def solve(self, timeout=30):
        start_time = time.time()
        counter = 0
        queue = []

        initial_state = {
            'assignment': {},
            'remaining': set(self.variables),
            'total_score': 0,
            'total_fatigue': 0,
            'categories': set()
        }
        heapq.heappush(queue, (-initial_state['total_score'], counter, initial_state))
        counter += 1

        while queue and (time.time() - start_time) < timeout:
            _, _, current = heapq.heappop(queue)

            if len(current['assignment']) == len(self.variables):
                if len(current['categories']) >= 3:
                    self.best_solution = current['assignment']
                    self.best_score = current['total_score']
                continue

            var = min(current['remaining'], key=lambda v: len(self.domains[v]))

            for value in self.domains[var]:
                new_assignment = dict(current['assignment'])
                new_assignment[var] = value

                day_score, day_fatigue = evaluate_day(value, actions)
                new_total_fatigue = current['total_fatigue'] + day_fatigue

                if new_total_fatigue > self.max_fatigue:
                    continue

                new_total_score = current['total_score'] + day_score
                new_categories = set(current['categories'])
                for session in value:
                    new_categories.add(session[0])

                new_state = {
                    'assignment': new_assignment,
                    'remaining': current['remaining'] - {var},
                    'total_score': new_total_score,
                    'total_fatigue': new_total_fatigue,
                    'categories': new_categories
                }

                heapq.heappush(queue, (-new_total_score, counter, new_state))
                counter += 1

        return self.best_solution

# Main execution
all_sessions = get_all_sessions(actions)
days = [f"Day{i}" for i in range(1, 8)]
domains = {day: generate_domain(all_sessions) for day in days}

csp = OptimizedTrainingCSP(days, domains, max_fatigue=45)
solution = csp.solve(timeout=30)

# Output results
output = ""
if solution:
    total_score = 0
    total_fatigue = 0
    for day in days:
        plan = solution[day]
        score, fatigue = evaluate_day(plan, actions)
        total_score += score
        total_fatigue += fatigue
        output += f"{day}:\n"
        for session in plan:
            output += f"  - {session[1]} (Level {session[2]}) in {session[0]}\n"
        output += f"    Score: {score:.2f}, Fatigue: {fatigue:.2f}\n"
    output += f"\nTotal Score: {total_score:.2f}\n"
    output += f"Total Fatigue: {total_fatigue:.2f}"
else:
    output = "No solution found within time limit."

# print(output)
    
# backend/CSP.py
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS  # For cross-origin requests (if needed)

app = Flask(__name__)
CORS(app)  # Enable CORS if frontend/backend are on different ports

# Serve the results.html file from the interface directory
@app.route('/results')
def serve_results():
    return send_from_directory('../interface', 'results.html')

# API endpoint to send data
@app.route('/api/data')
def send_data():

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run on port 5000