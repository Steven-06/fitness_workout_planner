from constraint import Problem

EXERCISES = {
    "Cardio": {
        "Beginner":     ["30-min brisk walk", "Light cycling", "Swimming laps"],
        "Intermediate": ["30-min jog", "Jump rope intervals", "Cycling sprints"],
    },
    "Upper Body": {
        "Beginner":     ["Push-ups (3x10)", "Dumbbell rows (3x10)", "Shoulder press (3x10)"],
        "Intermediate": ["Bench press (4x8)", "Pull-ups (3x8)", "Arnold press (4x10)"],
    },
    "Lower Body": {
        "Beginner":     ["Bodyweight squats (3x15)", "Lunges (3x12)", "Glute bridges (3x15)"],
        "Intermediate": ["Barbell squats (4x8)", "Romanian deadlift (4x8)", "Leg press (4x10)"],
    },
    "Full Body": {
        "Beginner":     ["Burpees (3x8)", "Mountain climbers (3x15)", "Jumping jacks (3x20)"],
        "Intermediate": ["Deadlifts (4x6)", "Clean and press (3x8)", "Kettlebell swings (3x12)"],
    },
    "Rest": {
        "Beginner":     ["Light stretching", "Short walk"],
        "Intermediate": ["Light stretching", "Short walk"],
    },
}


class CSPWorkoutPlanner:
    def __init__(self, user):
        self.user     = user
        self.problem  = Problem()
        self.days     = user["available_days"]
        self.level    = user.get("level", "Beginner")
        self.workouts = ["Cardio", "Upper Body", "Lower Body", "Full Body", "Rest"]

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

        return {
            day: {
                "workout":   solution[day],
                "exercises": EXERCISES[solution[day]].get(self.level, []),
            }
            for day in self.days
        }