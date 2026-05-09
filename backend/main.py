from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routes.workout_routes import router as workout_router
from routes.user_routes import router as user_router
from seed import seed_workouts
from services.adherence_predictor import AdherencePredictor

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

app = FastAPI(title="Fitness Tracker API", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Seed workouts + load (or train) the adherence NN on startup
@app.on_event("startup")
async def startup_event():
    seed_workouts()
    metrics = AdherencePredictor().load_or_train()
    if metrics is not None:
        print(f"Trained adherence model -- {metrics}")
    else:
        print("Loaded adherence model from artifacts")

app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(workout_router, prefix="/api/v1", tags=["workouts"])

@app.get("/", response_class=FileResponse)
async def root():
    return FRONTEND_DIR / "index.html"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)