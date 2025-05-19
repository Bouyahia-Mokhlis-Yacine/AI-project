import numpy as np
import itertools
import math
import copy
from collections import defaultdict
import json 




class Node:
    def __init__(self, position, metrics, action=None):
        self.position = position
        self.metrics = metrics.copy()
        # Store action as immutable tuple
        self.action = action if action else "rest"  # (category, intensities)
        
    def copy(self):
        """Create a deep copy of the node"""
        return Node(
            position=self.position,
            metrics=self.metrics.copy(),
            action=self.action
        )




class  Training_Problem :
    def __init__(self, initial_state ):
        self.initial_state = initial_state
        state = initial_state



    def generate_neighbors (self , state): 


        "This function generates the neighbors of the current state by applying all possible actions and their intensities"
        if state.position == "Goalkeeper" :
            with open('../project/../project/Goalkeeper_actions.json', 'r') as f:
                actions = json.load(f)
        

        if state.position == "Attacker" :
            with open('../project/Attacker_actions.json', 'r') as f:
                actions = json.load(f)

        if state.position == "Defender" :
            with open ('../project/Defender_actions.json' , 'r') as f:
                actions = json.load(f)


        if state.position == "Defender" :
            with open ('../project/midfielder_actions.json' , 'r') as f:
                actions = json.load(f)


                
        neighbors = []
        for action in actions.keys():
            for exercise in actions[action].keys() :
                new_state = self.transition(state , action)
                neighbors.append(new_state)

        return neighbors



    def transition(self, state, action):



        "this function applies the action and its intensities to the current state and returns the new state"

        if state.position == "Goalkeeper" :
            with open('../project/Goalkeeper_actions.json') as f:
                actions = json.load(f)

        if state.position == "Attacker" :
            with open('../project/Attacker_actions.json', 'r') as f:
                actions = json.load(f)

        if state.position == "Defender" :
            with open ('../project/Defender_actions.json' , 'r') as f:
                actions = json.load(f)

        if state.position == "Midfilder" :
            with open ('../project/midfielder_actions.json' , 'r') as f:
                actions = json.load(f)

                
        total_effects = defaultdict(float)
        # Get exercises for this action from predefined actions data
        exercises = actions[action].keys()
        
        for exercise in exercises:
            exercise_effects = actions[action][exercise]

            for metric in exercise_effects.keys():
                total_effects[metric] += exercise_effects[metric]  # Accumulate deltas

        # Apply changes to the NEW state's metrics
        new_state = state.copy()
        for metric in total_effects.keys():
            # Access metrics via .metrics, not state[metric]
            new_state.metrics[metric] += ((100 - state.metrics[metric]) / 100) * total_effects[metric]
        return Node(
        position=state.position,
        metrics=new_state.metrics,
        action=(action)
    )  # Return updated state







    def evaluate_performance(self , state) : 

        if not isinstance(state, Node):
            raise ValueError("Invalid state type")

        """ this function just calculates the performance score of the player based on the metrics and position 
        the performance score is calculated based on the position of the player and the metrics that are available for this position """

        def fifa_curve(raw_score, min_raw=50, max_raw=100):


            "this function applies the FIFA curve to the raw score to get the final score"


        # Ensure raw_score is within the range
        # Normalize to 0-1 range
            normalized = (raw_score - min_raw) / (max_raw - min_raw)
        # Apply logistic curve (adjust k for steeper/flatter curves)   // this function will be needed afterwards 
            k = 4  # Controls the curve steepness (FIFA uses ~3-5)
            curved = 99 / (1 + np.exp(-k * (normalized - 0.5)))
            return round(curved)

        

        if state.position == "Goalkeeper":
            # scores = {
            #     # Awareness: Save Rate (50%) + Clean Sheets (30%) - Errors (20%)
            #     'awareness': (state.metrics['save_percentage'] * 0.5) + 
            #                 (state.metrics['clean_sheet_bonus'] * 0.3) - 
            #                 (metrics['error_impact'] * 0.2),
                
            #     # Catching: Success Rate (80%) - Drop Penalty (20%)
            #     'catching': (state.metrics['catch_success_rate'] * 0.8) - 
            #             (state.metrics['drop_penalty'] * 0.2),
                
            #     # Parrying: Direct safe parry rate
            #     'parrying': state.metrics['safe_parry_rate'],
                
            #     # Reflexes: Close Range (40%) + Reaction Saves + Penalty Bonus
            #     'reflexes': (state.metrics['close_range_save_rate'] * 0.4) +
            #             (state.metrics['reaction_saves'] * 5) +
            #             (10 if state.metrics['penalty_save_rate'] >= 33 else 0),
                
            #     # Reach: Height (50%) + Long Shots (30%) + Diving (20%)
            #     'reach':(metrics['long_shot_save_rate'] * 0.5) +
            #             (metrics['diving_save_rate'] * 0.5)

            # }
                # 'overall': 0.25 * scores['awareness'] + 0.25 * scores['catching'] + 0.2 * scores['parrying'] + 0.15 * scores['reflexes'] + 0.15 * scores['reach']
            state.metrics["overall"] = 0.25 * state.metrics['awareness'] + 0.25 * state.metrics['catching'] + 0.2 * state.metrics['parrying'] + 0.15 * state.metrics['reflexes'] + 0.15 * state.metrics['reach']
            return state.metrics["overall"]


        
        elif state.position == "Defender":
            #TacklingAndDuels = 0.35 × TacklesWon + 0.25 × GroundDuelsWon + 0.2 × AerialDuelsWon + 0.2 × DefendingDrillScore
            #Positioning = 0.3 × ((1 - Errors / MaxErrors) × 100) + 0.3 × DefensiveShapeScore + 0.2 × ((1 - ReactionTime / 1000) × 100) + 0.2 × PositioningAwareness
            #Passing = 0.4 × PassAccuracy + 0.25 × (Clearances / MaxClearances × 100) + 0.2 × DistributionTrainingScore + 0.15 × (ChancesCreated × 20)
            #Physical = 0.25 × (VO2max / 75 × 100) + 0.2 × (Strength / 250 × 100) + 0.15 × (Distance / 12000 × 100) + 0.15 × (TrainingLoad / 1000 × 100) + 0.15 × (sleep_quality × 10) + 0.1 × ((80 - RestingHR) / 40 × 100)
            #DefensiveImpact = 0.3 × DuelsWon + 0.25 × MarkingTraining + 0.25 × (DefContributions / MaxDefContrib × 100) + 0.2 × ((1 - ReactionTime / 1000) × 100)
            #Overall = 0.25 × TacklingAndDuels + 0.25 × Positioning + 0.20 × DefensiveImpact + 0.15 × Physical + 0.15 × Passing
            # Calculate the metrics based on the state
            TacklingAndDuels = 0.35 * state.metrics["TacklesWon"] + 0.25 * state.metrics["GroundDuelsWon"] + 0.2 * state.metrics["AerialDuelsWon"] + 0.2 * state.metrics["DefendingDrillScore"]
            PositioningAndAwareness = 0.3 * ((1 - state.metrics["Errors"] / state.metrics["MaxErrors"]) * 100) + 0.3 * state.metrics["defensive_shape_training_score"] + 0.2 * ((1 - state.metrics["ReactionTime"] / 1000) * 100) + 0.2 * state.metrics["PositioningAwareness"]
            PassingAndBuildup = 0.4 * state.metrics["PassAccuracy"] + 0.25 * (state.metrics["clearances"] / state.metrics["MaxClearances"] * 100) + 0.2 * state.metrics["DistributionTrainingScore"] + 0.15 * (state.metrics["ChancesCreated"] * 20)
            PhysicalConditioning = 0.25 * (state.metrics["vo2_max"] / 75 * 100) + 0.2 * (state.metrics["Strength"] / 250 * 100) + 0.15 * (state.metrics["Distance"] / 12000 * 100) + 0.15 * (state.metrics["TrainingLoad"] / 1000 * 100) + 0.15 * (state.metrics["sleep_quality"] * 10) + 0.1 * ((80 - state.metrics["RestingHR"]) / 40 * 100)
            DefensiveImpact = 0.3 * state.metrics["DuelsWon"] + 0.25 * state.metrics["MarkingTraining"] + 0.25 * (state.metrics["DefContributions"] / state.metrics["MaxDefContrib"] * 100) + 0.2 * ((1 - state.metrics["ReactionTime"] / 1000) * 100)
            overall = 0.25 * TacklingAndDuels + 0.25 * PositioningAndAwareness + 0.2 * DefensiveImpact + 0.15 * PhysicalConditioning + 0.15 * PassingAndBuildup

            return {
                "TacklingAndDuels": TacklingAndDuels ,
                "PositioningAndAwareness": PositioningAndAwareness ,
                "PassingAndBuildup": PassingAndBuildup ,
                "PhysicalConditioning": PhysicalConditioning,
                "DefensiveImpact": DefensiveImpact,
                "overall": overall
            }
        

        elif state.position == "Midfielder-D":
            Defending = min(
                (state.metrics["Tackles_per_match"] * 10) +       
                (state.metrics["Clearances_per_match"] * 8) +     
                (state.metrics["Duels_won_percent"] * 0.8) +      
                (state.metrics["Total_distance_km"] * 2),         
                    100                              # Cap at 100
                            )
            
            Passing = min(
                (state.metrics["Pass_completion"] * 0.8) +        
                (state.metrics["Assists_per_match"] * 20) +       
                (state.metrics["Chances_created_per_match"] * 3), 
                100
            )


            Physicality = min(
                (state.metrics["Total_distance_km"] * 2.5) +      # 12.6 → 31.5
                (state.metrics["Sprint_distance_km"] * 1.2),      # 28.8 → 34.56
                100
            )

            Reliability = max(100 - (state.metrics["Major_errors"] * 25) , 50) * 0.05

            overall = fifa_curve((Defending * 0.4) + (Passing * 0.2) + (Physicality * 0.2) + (Reliability * 0.2))

            return {
                "Defending": Defending,
                "Passing": Passing,
                "Physicality": Physicality,
                "Reliability": Reliability,
                "overall": overall
            }
        elif state.position == "Midfielder-A":
            Attacking = min(
                (state.metrics["Goals_per_match"] * 90) +         # 0.28 → 25.2
                (state.metrics["Assists_per_match"] * 50) +       # 0.6 → 30
                (state.metrics["Shots_on_target_per_match"] * 15),# 0.8 → 12
                100
            )

            Passing = min(
                (state.metrics["Pass_completion"] * 0.7) +        # 85% → 59.5
                (state.metrics["Chances_created_per_match"] * 12),# 2.4 → 28.8
                100
            )

            Dribbling = min(
                (state.metrics["Dribble_success_percent"] * 0.9) + # 70% → 63
                (state.metrics["Duels_won_percent"] * 0.4),        # 70% → 28
                100
            )

            Mobility = (state.metrics["Total_distance_km"] / 15) * 100
            
            overall = fifa_curve((Attacking * 0.3) + (Passing * 0.4) + (Dribbling * 0.2) + (Mobility * 0.1))

            return {
                "Attacking": Attacking,
                "Passing": Passing,
                "Dribbling": Dribbling,
                "Mobility": Mobility,
                "overall": overall
            }
        elif state.position == "Striker":
            #Shooting =Shooting = 0.5 × (Goals × 20) + 0.25 × (ShotsOnTarget × 10) + 0.2 × FinishingTest + 0.05 × DribbleSuccess
            #Pace = 0.6 × (SprintSpeed × 10) + 0.25 × (SprintDistance / 1000 × 100) + 0.15 × (TotalDistance / 12000 × 100)
            #Dribbling = 0.5 × DribbleSuccess + 0.3 × DuelsWon + 0.2 × ((1 - ReactionTime / 1000) × 100)
            #Passing = 0.4 × (Assists × 25) + 0.35 × PassCompletion + 0.25 × (ChancesCreated × 20)
            #Physical = 0.25 × (VO2max / 75 × 100) + 0.2 × (Strength / 250 × 100) + 0.2 × (TrainingLoad / 1000 × 100) + 0.15 × (sleep_quality × 10) + 0.1 × ((80 - RestingHR) / 40 × 100) + 0.1 × BMI_Factor
            #Overall = 0.30 × Shooting + 0.20 × Pace + 0.20 × Dribbling + 0.15 × Physical + 0.15 × Passing
            Shooting = 0.5 * (state.metrics["Goals"] * 20) + 0.25 * (state.metrics["ShotsOnTarget"] * 10) + 0.2 * state.metrics["FinishingTest"] + 0.05 * state.metrics["DribbleSuccess"]
            Pace = 0.6 * (state.metrics["SprintSpeed"] * 10) + 0.25 * (state.metrics["SprintDistance"] / 1000 * 100) + 0.15 * (state.metrics["TotalDistance"] / 12000 * 100)
            Dribbling = 0.5 * state.metrics["DribbleSuccess"] + 0.3 * state.metrics["DuelsWon"] + 0.2 * ((1 - state.metrics["ReactionTime"] / 1000) * 100)
            Passing = 0.4 * (state.metrics["Assists"] * 25) + 0.35 * state.metrics["PassCompletion"] + 0.25 * (state.metrics["ChancesCreated"] * 20)
            Physical = 0.25 * (state.metrics["vo2_max"] / 75 * 100) + 0.2 * (state.metrics["Strength"] / 250 * 100) + 0.2 * (state.metrics["TrainingLoad"] / 1000 * 100) + 0.15 * (state.metrics["sleep_quality"] * 10) + 0.1 * ((80 - state.metrics["RestingHR"]) / 40 * 100) + 0.1 * state.metrics["BMI_Factor"]
            overall = 0.3 * Shooting + 0.2 * Pace + 0.2 * Dribbling + 0.15 * Physical + 0.15 * Passing
            return {
                "Shooting": Shooting,
                "Pace": Pace,
                "Dribbling": Dribbling,
                "Passing": Passing,
                "Physical": Physical,
                "overall": overall
            }
        



    def evaluate_injury_risk(self , state) :

        return (  
        (state.metrics ["acute_workload"] * 0.4) +  
        (state.metrics["chronic_workload"] * 0.3) +  
        (1 / (state.metrics["days_since_last_injury"] + 1) * 0.3)  # Inverse relationship  
    )  


metrics = {
    # Shot-stopping metrics
    "save_percentage": 73,          # 73% saves (average for top-tier GKs)
    "goals_conceded": 4,            # 4 goals conceded in last 5 matches
    "1v1_training_score": 82,       # Strong in 1v1 drills
    "reaction_time": 180,           # 180ms (elite: 150-200ms range)
    "aerial_ball_handling_success": 78,  # 78% success in aerial claims
    "cross_claims": 12,             # 12 cross claims in 5 matches
    "jump_height": 75,              # 75cm vertical jump
    "defensive_set_piece_handling": 85, # Strong in set-piece organization

    # Distribution metrics
    "distribution_accuracy_score": 88,  # 88% pass accuracy
    "long_pass_success": 68,        # 68% successful long passes
    "distribution_training": 84,    # High training score
    "pass_completion": 86,          # 86% overall pass completion

    # Error/risk metrics
    "errors_leading_to_goals": 1,   # 1 error leading to a goal in 5 matches
    "cognitive_score": 88,          # High decision-making score
    "video_analysis_engagement": 92, # Actively engages in video analysis

    # Derived metrics (placeholders)
    "max_goals_conceded": 3,        # Worst match: conceded 3 goals
    "MaxErrors": 2,                 # Max 2 errors in a single match
    "set_piece_handling_score": 85, # Strong set-piece defense
    "clean_sheet_bonus": 2,              # 2 clean sheets in 5 matches

    # Handling metrics
    "catches": 15,                  # 15 catches in 5 matches
    "punches": 5,                   # 5 punches
    "drops": 2,                     # 2 dropped catches
    "safe_parry": 8,                # 8 safe parries
    "total_parry": 10,              # 10 total parry attempts

    # Defensive drills
    "tackles_won": 9,               # 9 tackles won
    "ground_duels_won": 65,         # 65% ground duels won
    "aerial_duels_won": 76,         # 76% aerial duels won
    "defending_drill_score": 88,    # Training performance

    # Mental/positioning
    "errors_leading_to_shots": 3,   # 3 errors leading to shots
    "defensive_shape_training_score": 83,
    "positioning_awareness_score": 89, # Strong positional IQ

    # In-game actions
    "passing_accuracy": 87,         # 87% passing accuracy
    "clearances": 18,               # 18 clearances in 5 matches
    "distribution_under_pressure": 79, # Performs under pressure
    "chances_created": 1,           # 1 assist/chance created

    # Physical metrics
    "vo2_max": 54,                  # High aerobic capacity (ml/kg/min)
    "lower_body_strength": 92,      # Leg press: 92% of position max
    "total_distance_covered": 25.3, # 25.3km over 5 matches
    "total_training_load": 435,     # Cumulative load (arbitrary units)
    "resting_heart_rate": 48,       # Bradycardia (elite fitness)
    "sleep_quality": 84,            # 84/100 sleep score
    "sprint_distance": 30,

    # Match impact
    "duels_won": 72,                # 72% of duels won
    "marking_and_tackling": 85,     # Defensive drill score
    "defensive_contributions": 22,  # 22 interceptions/blocks/clearances
    "mental_fatigue_score": 28,     # Low fatigue (0 = fresh, 100 = exhausted)
    "close_range_save_rate" : 90,         # 90% close-range saves
    "reaction_saves": 80,            # 80% reaction saves
    "long_shot_save_rate": 75,         # 75% long shot saves
    "penalty_save_rate": 30,         # 30% penalty saves
    "diving_save_rate": 85,         # 85% diving saves
    "injury_prevention": 20,
    "fatigue_score":10,

    # Attack contribution (minimal for GKs)
    "assists_per_match": 0.1,       # 0.1 assists per match
    "goals_per_match": 0.0,         # Rarely scores
    "shots_on_target_per_match": 0.2, # Occasional long kicks
    "dribble_success_percent": 40,  # 40% dribble success (rarely dribbles)
    "FinishingTest": 72,            # Penalty practice score

    # Athleticism
    "SprintSpeed": 31.5,            # 31.5 km/h top speed
    "SprintDistance": 285,          # 285m of sprints per match
    "BMI_Factor": 23.1,             # BMI 23.1 (optimal for agility)

    # Injury/load metrics
    "chronic_workload": 7.1,       # 4-week workload
    "acute_workload": 8.9,          # 1-week workload
    "days_since_last_injury": 120,  # No recent injuries
    "injury_history_count": 2,      # 2 past injuries
    "hrv": 63,                      # Heart rate variability (healthy)
    "fatigue": 24,                  # Low fatigue (0-100 scale)
    "video_analysis_score": 87,     # High engagement
    "Strength": 88                  # Overall strength index

}
    # "error_impact": "errors_leading_to_goals" / "goals_conceded" ,
    # "drops_penalty" : "drops"/"catches",
    # "safe_parry_rate" : "safe_parry" / "total_parry" ,
    # "catch_success_rate" : ["catches"] / ("catches" + "punches") *100,
metrics["safe_parry_rate"] = metrics["safe_parry"] / (metrics["total_parry"])  # Avoid division by zero
metrics["drop_penalty"] = metrics["drops"] / (metrics["catches"] + 1)  # Avoid division by zero
metrics["error_impact"] = metrics["errors_leading_to_goals"] / (metrics["goals_conceded"] + 1)  # Avoid division by zero
metrics["catch_success_rate"] = (metrics["catches"] / (metrics["catches"] + metrics["punches"])) * 100




scores = {
                # Awareness: Save Rate (50%) + Clean Sheets (30%) - Errors (20%)
                'awareness': (metrics['save_percentage'] * 0.5) + 
                            (metrics['clean_sheet_bonus'] * 0.3) - 
                            (metrics['error_impact'] * 0.2),
                
                # Catching: Success Rate (80%) - Drop Penalty (20%)
                'catching': (metrics['catch_success_rate'] * 0.8) - 
                        (metrics['drop_penalty'] * 0.2),
                
                # Parrying: Direct safe parry rate
                'parrying': metrics['safe_parry_rate'],
                
                # Reflexes: Close Range (40%) + Reaction Saves + Penalty Bonus
                'reflexes': (metrics['close_range_save_rate'] * 0.4) +
                        (metrics['reaction_saves'] * 5) +
                        (10 if metrics['penalty_save_rate'] >= 33 else 0),
                
                # Reach: Height (50%) + Long Shots (30%) + Diving (20%)
                'reach':(metrics['long_shot_save_rate'] * 0.5) +
                        (metrics['diving_save_rate'] * 0.5)

            }


new_metrics = {
    # Physical & Technical Metrics
    "total_distance": 8.5,          # Total km added in drills (weekly)
    "flexibility_score": 75,        # 75/100 (improved via mobility work)
    "sprint_speed": 32.4,           # km/h (specific to sprint training)
    "defensive_coverage": 84,       # % of defensive zones covered effectively
    "VO2_max": 57,                  # ml/kg/min (improved via RSA sprints)
    "fatigue_resistance": 88,       # 0-100 scale (high = resilient)
    "jump_power": 82,               # cm (vertical leap improvement)
    "unilateral_strength": 89,       # 0-100 score (split squat performance)
    "balance": 88,                  # 0-100 (ankle stability drills)
    "posterior_chain_strength": 91,  # 0-100 (Nordic curl strength)
    "muscle_resilience": 87,         # 0-100 (eccentric load tolerance)
    "defensive_errors": 0 ,

    # Mental/Cognitive Metrics
    "mental_fatigue": 18,           # 0-100 (lower = fresher)
    "duel_resilience": 78,          # % recovery rate after losing duels
    "decision_making": 85,          # 0-100 (tactical choices under pressure)
    "decision_speed": 165,          # ms (stimulus response time)
    "stress_level": 14,             # 0-100 (lower = calmer)
    "anticipation": 89,             # 0-100 (predicting opposition moves)
    "decision_quality": 87,         # 0-100 (effectiveness of choices)

    # Tactical Metrics
    "tactical_adaptability": 86,    # 0-100 (adjusting to 10v11 scenarios)
    "defensive_resilience": 83,     # 0-100 (sustaining defensive shape)
    "contextual_adaptability": 88,   # 0-100 (home/away performance gap)
    "stress_management": 82,        # 0-100 (handling pressure)
    "tactical_flexibility": 84,      # 0-100 (switching between deep/mid-block)
    "tactical_awareness": 91,        # 0-100 (reading the game)
    "tactical_positioning": 90,      # 0-100 (optimal clearance positioning)
    "clearance_success": 86,         # % of clearances reaching teammates
    "positional_awareness": 0,

    # Recovery Metrics
    "recovery_quality": 86,         # 0-100 (yoga/breathing impact)
    "HRV": 68,                       # Heart rate variability (higher = better)
    "TacklesWon" : 5,
    "GroundDuelsWon" : 3,
    "AerialDuelsWon" : 3,
    "DefendingDrillScore" : 80,
    "Errors" : 1,
    "ReactionTime" : 200, 
    "PositioningAwareness" : 80,
    "PassAccuracy" : 80,
    "MaxClearances" : 5 ,
    "DistributionTrainingScore" : 70,
    "ChancesCreated" : 2,
    
    
    
}



metrics = metrics | scores | new_metrics 

