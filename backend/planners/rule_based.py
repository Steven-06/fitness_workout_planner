from backend.repositories import WorkoutRepository


def generate_rule_based_plan(user):
    workout_repository = WorkoutRepository()
    
    available_days = user["available_days"]
    goal = user["goal"]
    level = user.get("level", "Beginner")

    if goal == "Lose Weight":
        rotation = ["Cardio", "Upper Body", "Cardio", "Lower Body", "Rest"]
    elif goal == "Muscle Gain":
        rotation = ["Upper Body", "Lower Body", "Full Body", "Rest"]
    else:
        rotation = ["Cardio", "Upper Body", "Rest"]

    plan = {}
    for index, day_name in enumerate(available_days):
        workout_category = rotation[index % len(rotation)]
        matching_workout = workout_repository.get_by_category_and_level(workout_category, level)
        exercises = matching_workout["exercises"] if matching_workout else []
        plan[day_name] = {
            "workout": workout_category,
            "exercises": exercises,
        }
    return plan