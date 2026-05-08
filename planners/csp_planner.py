from constraint import Problem
from repositories import WorkoutRepository


class CSPWorkoutPlanner:
    def __init__(self, user):
        self.user     = user
        self.problem  = Problem()
        self.days     = user["available_days"]
        self.level    = user.get("level", "Beginner")
        self.workouts = ["Cardio", "Upper Body", "Lower Body", "Full Body", "Rest"]
        self.repo = WorkoutRepository()

    def add_variables(self):
        for day in self.days:
            self.problem.addVariable(day, self.workouts)

    def no_consecutive_same(self):
        for i in range(len(self.days) - 1):
            d1, d2 = self.days[i], self.days[i + 1]
            self.problem.addConstraint(lambda a, b: a != b, (d1, d2))

    def beginner_limit(self):
        if self.level == "Beginner":
            intense = ["Lower Body", "Full Body", "Cardio"]
            def limit(*values):
                return sum(1 for v in values if v in intense) <= 3
            self.problem.addConstraint(limit, self.days)

    def require_rest_day(self):
        self.problem.addConstraint(lambda *values: "Rest" in values, self.days)

    def goal_constraints(self):
        goal = self.user["goal"]
        if goal == "Lose Weight":
            self.problem.addConstraint(
                lambda *values: values.count("Cardio") >= 2,
                self.days,
            )
        elif goal == "Muscle Gain":
            strength = ["Upper Body", "Lower Body", "Full Body"]
            self.problem.addConstraint(
                lambda *values: sum(1 for v in values if v in strength) >= 2,
                self.days,
            )

    def generate_plan(self):
        self.add_variables()
        self.no_consecutive_same()
        self.beginner_limit()
        self.require_rest_day()
        self.goal_constraints()

        solution = self.problem.getSolution()
        if solution is None:
            return None

        plan = {}
        for day in self.days:
            workout_category = solution[day]
            workout = self.repo.get_by_category_and_level(workout_category, self.level)
            exercises = workout["exercises"] if workout else []
            plan[day] = {
                "workout": workout_category,
                "exercises": exercises,
            }
        
        return plan