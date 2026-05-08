from planners.csp_planner import EXERCISES


def generate_rule_based_plan(user):
    
    days  = user["available_days"]
    goal  = user["goal"]
    level = user.get("level", "Beginner")

    if goal == "Lose Weight":
        rotation = ["Cardio", "Upper Body", "Cardio", "Lower Body", "Rest"]
    elif goal == "Muscle Gain":
        rotation = ["Upper Body", "Lower Body", "Full Body", "Rest"]
    else:
        rotation = ["Cardio", "Upper Body", "Rest"]

    plan = {}
    for i, day in enumerate(days):
        workout = rotation[i % len(rotation)]
        plan[day] = {
            "workout":   workout,
            "exercises": EXERCISES[workout].get(level, []),
        }
    return plan