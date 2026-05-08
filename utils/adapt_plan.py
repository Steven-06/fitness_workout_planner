import copy


def adapt_plan(plan, missed_day):
    if missed_day not in plan:
        return copy.deepcopy(plan)

    updated = copy.deepcopy(plan)
    missed_workout = updated[missed_day]["workout"]
    del updated[missed_day]

    for day, info in updated.items():
        current_tokens = [t.strip() for t in info["workout"].split("+")]
        if current_tokens[0] == "Rest" or missed_workout in current_tokens:
            continue
        updated[day]["workout"] = info["workout"] + " + " + missed_workout
        break

    return updated


def compare_plans(csp_plan, rule_plan, goal=""):
    def score(plan):
        days     = list(plan.keys())
        workouts = [plan[d]["workout"].split("+")[0].strip() for d in days]

        conflicts = sum(
            1 for i in range(len(workouts) - 1)
            if workouts[i] == workouts[i + 1]
        )

        rest_days = sum(1 for w in workouts if w == "Rest")

        goal_lower = goal.lower()
        if "lose weight" in goal_lower:
            goal_match = workouts.count("Cardio")
        elif "muscle gain" in goal_lower:
            strength   = {"Upper Body", "Lower Body", "Full Body"}
            goal_match = sum(1 for w in workouts if w in strength)
        else:
            goal_match = len({w for w in workouts if w != "Rest"})

        return {
            "consecutive_conflicts": conflicts,
            "rest_days":             rest_days,
            "goal_match_score":      goal_match,
        }

    csp_score  = score(csp_plan)
    rule_score = score(rule_plan)

    csp_wins = rule_wins = 0

    if csp_score["consecutive_conflicts"] < rule_score["consecutive_conflicts"]:
        csp_wins += 1
    elif csp_score["consecutive_conflicts"] > rule_score["consecutive_conflicts"]:
        rule_wins += 1

    if csp_score["goal_match_score"] > rule_score["goal_match_score"]:
        csp_wins += 1
    elif csp_score["goal_match_score"] < rule_score["goal_match_score"]:
        rule_wins += 1

    if csp_wins > rule_wins:
        verdict = "CSP plan wins — better constraint satisfaction and goal alignment."
    elif rule_wins > csp_wins:
        verdict = "Rule-based plan scores higher this run — CSP may have used stricter recovery constraints."
    else:
        verdict = "Both plans are equivalent across all metrics."

    return {
        "csp_score":  csp_score,
        "rule_score": rule_score,
        "verdict":    verdict,
    }