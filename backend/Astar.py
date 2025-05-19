from queue import PriorityQueue
import itertools
import json
import random
import math
from lib import metrics





class AstarDailySchedule:

    @staticmethod
    def load_actions(position):
        """Load exercises from JSON file for the position"""
        with open(f'{position}_actions.json') as f:
            return json.load(f)

    @staticmethod
    def categorize_exercise(exercise_name, effects):
        """Determine exercise type based on its effects"""
        recovery_keywords = ['recovery', 'regeneration', 'hydrotherapy', 'yoga', 'sleep']
        mental_keywords = ['mental', 'cognitive', 'visualization', 'focus', 'confidence']
        
        # Check for recovery keywords in exercise name or effects
        if any(kw in exercise_name.lower() for kw in recovery_keywords):
            return 'recovery'
        if any(kw in effect.lower() for effect in effects for kw in recovery_keywords):
            return 'recovery'
            
        # Check for mental keywords
        if any(kw in exercise_name.lower() for kw in mental_keywords):
            return 'mental'
        if any(kw in effect.lower() for effect in effects for kw in mental_keywords):
            return 'mental'
            
        # Default to training
        return 'training'

    @staticmethod
    def organize_actions(raw_actions):
        """Convert raw JSON structure to categorized exercises"""
        categorized = {
            'training': {},
            'mental': {},
            'recovery': {}
        }
        
        for category, exercises in raw_actions.items():
            for ex_name, effects in exercises.items():
                ex_type = AstarDailySchedule.categorize_exercise(ex_name, effects)
                full_name = f"{category}_{ex_name}"
                categorized[ex_type][full_name] = effects
                
        return categorized

    @staticmethod
    def calculate_scores(action, metrics):
        """Calculate performance and risk for an action"""
        perf = sum(v * metrics.get(k, 0) for k, v in action.items() if v > 0)
        risk = sum(abs(v) * metrics.get(k, 0) for k, v in action.items() if v < 0)
        return perf, risk

    @staticmethod
    def generate_schedule(position, num_days, metrics):
        """Generate optimal schedule"""
        try:
            raw_actions = AstarDailySchedule.load_actions(position)
            actions = AstarDailySchedule.organize_actions(raw_actions)
            
            # Verify we have enough exercises
            for cat in ['training', 'mental', 'recovery']:
                if len(actions[cat]) < 2:
                    print(f"❌ Not enough {cat} exercises in {position}_actions.json")
                    return None

            schedule = []
            training_streak = 0
            training_days_completed = 0
            
            for day in range(7):  # 7-day week
                if training_days_completed >= num_days:
                    schedule.append("REST")
                    continue
                    
                if training_streak == 2:
                    schedule.append("REST")
                    training_streak = 0
                    continue
                    
                # Select exercises
                training_ex = random.sample(list(actions['training'].items()), 2)
                mental_ex = random.choice(list(actions['mental'].items()))
                recovery_ex = random.choice(list(actions['recovery'].items()))
                
                day_plan = training_ex + [mental_ex] + [recovery_ex]
                schedule.append([ex[0] for ex in day_plan])
                training_streak += 1
                training_days_completed += 1
            
            # Calculate scores
            total_perf = sum(
                AstarDailySchedule.calculate_scores(ex[1], metrics)[0]
                for day in schedule if day != "REST"
                for ex in day_plan
            )
            total_risk = sum(
                AstarDailySchedule.calculate_scores(ex[1], metrics)[1]
                for day in schedule if day != "REST"
                for ex in day_plan
            )
            
            # Normalize scores
            perf_score = 7.8 + (total_perf / (num_days * 3)) * 2.1
            risk_score = 2 + (total_risk / (num_days * 0.5)) * 8
            
            return {
                'schedule': schedule,
                'performance': min(9.9, max(7.8, perf_score)),
                'injury_risk': min(10, max(2, risk_score))
            }
            
        except Exception as e:
            print(f"❌ Error generating schedule: {str(e)}")
            return None



if __name__ == "__main__":
    # Example metrics (adjust these values based on your priorities)

    
    position = "Goalkeeper"  # if you want to test a failure example change the position to "Attacker" 

    training_days = 4 # Number of desired training days
    
    result = AstarDailySchedule.generate_schedule(position, training_days, metrics)
    
    if result:
        print("🌞 Daily Schedule:")
        for i, day in enumerate(result['schedule'], 1):
            print(f"Day {i}: {day if isinstance(day, list) else [day]}")
        print(f"\n🌟 Predicted Performance: {result['performance']:.1f}/10")
        print(f"⚠️  Injury Risk: {result['injury_risk']:.1f}/10")
    else:
        print("Failed to generate schedule")

