from fastapi import FastAPI
from backend.routes.workout_routes import router as workout_router
from backend.routes.user_routes import router as user_router
from backend.seed import seed_workouts

app = FastAPI(title="Fitness Tracker API", version="1.0.0")

# Seed workouts on startup
@app.on_event("startup")
async def startup_event():
    seed_workouts()

app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(workout_router, prefix="/api/v1", tags=["workouts"])

@app.get("/")
async def root():
    return {"message": "Welcome to Fitness Tracker API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)