from repositories import WorkoutRepository


def generate_rule_based_plan(user):
    repo = WorkoutRepository()
    
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
        workout_category = rotation[i % len(rotation)]
        workout = repo.get_by_category_and_level(workout_category, level)
        exercises = workout["exercises"] if workout else []
        plan[day] = {
            "workout": workout_category,
            "exercises": exercises,
        }
    return plan