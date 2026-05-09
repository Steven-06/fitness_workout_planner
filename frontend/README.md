# Frontend (Modern Web App)

The new frontend is served directly by the FastAPI backend at the project root. It provides the same user workflows in a polished HTML/CSS/JavaScript interface.

## Run the frontend

1. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload
   ```
2. Open your browser and visit:
   ```text
   http://localhost:8000
   ```

## Features

- Create or load users
- Generate rule-based and CSP workout plans
- Compare plans, adapt plans, and predict adherence
- Browse saved plans, comparisons, predictions, and workouts
- Optional backend URL override for remote API deployments
