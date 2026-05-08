from backend.models import StoredWorkout
from backend.repositories.workout_repository import WorkoutRepository


WORKOUT_SEED_DATA = [
    # Cardio - Beginner
    {
        "category": "Cardio",
        "level": "Beginner",
        "exercises": ["30-min brisk walk", "Light cycling", "Swimming laps"],
        "duration_minutes": 30,
        "intensity": "low",
        "calories_burned": 200,
        "equipment_needed": [],
        "muscle_groups": ["Cardiovascular system", "Legs"],
        "benefits": ["Improved endurance", "Better heart health", "Low impact"],
        "description": "Light cardio workout suitable for beginners"
    },
    # Cardio - Intermediate
    {
        "category": "Cardio",
        "level": "Intermediate",
        "exercises": ["30-min jog", "Jump rope intervals", "Cycling sprints"],
        "duration_minutes": 35,
        "intensity": "medium",
        "calories_burned": 350,
        "equipment_needed": ["Jump rope"],
        "muscle_groups": ["Cardiovascular system", "Legs", "Core"],
        "benefits": ["Increased endurance", "Calorie burning", "Improved stamina"],
        "description": "Intermediate cardio with higher intensity intervals"
    },
    # Upper Body - Beginner
    {
        "category": "Upper Body",
        "level": "Beginner",
        "exercises": ["Push-ups (3x10)", "Dumbbell rows (3x10)", "Shoulder press (3x10)"],
        "duration_minutes": 30,
        "intensity": "medium",
        "calories_burned": 150,
        "equipment_needed": ["Dumbbells"],
        "muscle_groups": ["Chest", "Back", "Shoulders", "Biceps", "Triceps"],
        "benefits": ["Upper body strength", "Improved posture", "Muscle tone"],
        "description": "Beginner-friendly upper body strength training"
    },
    # Upper Body - Intermediate
    {
        "category": "Upper Body",
        "level": "Intermediate",
        "exercises": ["Bench press (4x8)", "Pull-ups (3x8)", "Arnold press (4x10)"],
        "duration_minutes": 40,
        "intensity": "high",
        "calories_burned": 220,
        "equipment_needed": ["Barbell", "Pull-up bar"],
        "muscle_groups": ["Chest", "Back", "Shoulders", "Biceps", "Triceps"],
        "benefits": ["Muscle growth", "Increased strength", "Better stability"],
        "description": "Intermediate upper body workout with compound movements"
    },
    # Lower Body - Beginner
    {
        "category": "Lower Body",
        "level": "Beginner",
        "exercises": ["Bodyweight squats (3x15)", "Lunges (3x12)", "Glute bridges (3x15)"],
        "duration_minutes": 30,
        "intensity": "medium",
        "calories_burned": 180,
        "equipment_needed": [],
        "muscle_groups": ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
        "benefits": ["Lower body strength", "Improved balance", "Functional fitness"],
        "description": "Beginner-friendly lower body workout using bodyweight"
    },
    # Lower Body - Intermediate
    {
        "category": "Lower Body",
        "level": "Intermediate",
        "exercises": ["Barbell squats (4x8)", "Romanian deadlift (4x8)", "Leg press (4x10)"],
        "duration_minutes": 45,
        "intensity": "high",
        "calories_burned": 300,
        "equipment_needed": ["Barbell", "Leg press machine"],
        "muscle_groups": ["Quadriceps", "Hamstrings", "Glutes", "Lower back"],
        "benefits": ["Muscle growth", "Increased leg strength", "Better athletic performance"],
        "description": "Intermediate lower body workout with heavy compound lifts"
    },
    # Full Body - Beginner
    {
        "category": "Full Body",
        "level": "Beginner",
        "exercises": ["Burpees (3x8)", "Mountain climbers (3x15)", "Jumping jacks (3x20)"],
        "duration_minutes": 25,
        "intensity": "medium",
        "calories_burned": 200,
        "equipment_needed": [],
        "muscle_groups": ["Full body", "Cardiovascular system"],
        "benefits": ["Full body engagement", "Cardio and strength", "Time efficient"],
        "description": "Quick full body workout combining cardio and strength"
    },
    # Full Body - Intermediate
    {
        "category": "Full Body",
        "level": "Intermediate",
        "exercises": ["Deadlifts (4x6)", "Clean and press (3x8)", "Kettlebell swings (3x12)"],
        "duration_minutes": 50,
        "intensity": "high",
        "calories_burned": 400,
        "equipment_needed": ["Barbell", "Kettlebell"],
        "muscle_groups": ["Full body", "Core", "Legs", "Back", "Shoulders"],
        "benefits": ["Overall strength", "Explosive power", "Functional fitness"],
        "description": "Advanced full body workout with explosive movements"
    },
    # Rest - Beginner
    {
        "category": "Rest",
        "level": "Beginner",
        "exercises": ["Light stretching", "Short walk"],
        "duration_minutes": 20,
        "intensity": "low",
        "calories_burned": 50,
        "equipment_needed": [],
        "muscle_groups": ["All"],
        "benefits": ["Recovery", "Flexibility", "Reduced soreness"],
        "description": "Recovery and rest day with light movement"
    },
    # Rest - Intermediate
    {
        "category": "Rest",
        "level": "Intermediate",
        "exercises": ["Light stretching", "Short walk"],
        "duration_minutes": 20,
        "intensity": "low",
        "calories_burned": 50,
        "equipment_needed": [],
        "muscle_groups": ["All"],
        "benefits": ["Recovery", "Flexibility", "Mental rest"],
        "description": "Recovery and rest day with light movement"
    }
]


def seed_workouts():
    """Seed the database with default workout data on startup"""
    workout_repository = WorkoutRepository()
    
    # Clear existing workouts
    workout_repository.clear_all()
    
    # Insert seed data
    for workout_data in WORKOUT_SEED_DATA:
        stored_workout = StoredWorkout(**workout_data)
        workout_repository.save(stored_workout)
    
    print(f"✓ Seeded {len(WORKOUT_SEED_DATA)} workouts to database")