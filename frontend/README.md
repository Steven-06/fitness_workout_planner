# Frontend — Streamlit Interactive UI

A fully-featured, easy-to-test web interface for the Fitness Tracker API built with **Streamlit**.

## Quick Start

### Prerequisites
- Python 3.9+
- Streamlit installed: `pip install streamlit`
- FastAPI backend running on `http://localhost:8000/api/v1`

### Run the Frontend

1. **Start the backend first** (in a separate terminal):
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```
   Or use the provided startup script:
   ```powershell
   .\run_server.ps1  # Windows PowerShell
   ```

2. **Run the Streamlit frontend** (in the frontend directory):
   ```bash
   cd frontend
   streamlit run app.py
   ```
   
   Your browser should automatically open to `http://localhost:8501`

## Features & Tabs

### 1. 👤 User Management
- **Create New User** — Build a profile with name, fitness goal, experience level, and available training days
- **Load Existing User** — Retrieve a previously created user by ID
- **Profile Display** — View all current user information

**Pro Tip:** Click "Load Demo User" in the sidebar for instant testing!

### 2. 📅 Plan Generation
- **Rule-Based Planning** — Generate fast, predictable weekly plans using heuristic rules
- **CSP Planning** — AI-optimized plans using Constraint Satisfaction Problem solving
- **Visual Weekly Calendar** — See your complete workout schedule at a glance
- **Detailed Breakdown** — Expand to view full exercise lists and intensity details

### 3. ⚖️ Comparison & Adaptation
- **Compare Plans** — Generate both rule-based and CSP plans side-by-side
- **Scoring Metrics**:
  - Consecutive workout conflicts
  - Rest days per week
  - Goal alignment score
- **Plan Adaptation** — Automatically redistribute missed workouts while maintaining balance
- **Verdict System** — Detailed explanation of which approach is better for your profile

### 4. 🤖 AI Prediction
- **Adherence Predictor** — Neural network forecasts your likelihood of sticking to the plan
- **Difficulty Scoring** — Assess plan difficulty (0-100%)
- **Prediction Factors**:
  - Available time
  - Sessions per week
  - Historical completion rate
  - Workout intensity
  - Fitness goal & experience level
- **Visual Progress Bars** — Easy-to-understand adherence and difficulty visualization

### 5. 📊 Data & Analytics
- **View User History** — Retrieve all saved plans, comparisons, and predictions for your user
- **Workout Database** — Browse complete library of available workouts
- **Category & Level Filtering** — Filter workouts by:
  - Category: Cardio, Upper Body, Lower Body, Full Body, Rest
  - Level: Beginner, Intermediate
- **Grouped Display** — Exercises organized by category with intensity and duration info

## Testing Guide

### Quick Demo Workflow
1. Click **"Load Demo User"** in the sidebar
2. Go to **Plan Generation** tab
3. Click **"Generate CSP Plan"** to create a smart schedule
4. Click **"Generate & Compare Plans"** in the **Comparison & Adaptation** tab
5. Check the **AI Prediction** tab to see adherence forecast
6. View all results in the **Data & Analytics** tab

### Manual User Creation
1. In **User Management**, enter:
   - Name: "Test User"
   - Goal: "weight_loss"
   - Level: "Beginner"
   - Days: Select Mon, Wed, Fri
2. Click **"Create User"** — You'll get a unique ID
3. Use this ID to test different features

### Testing Each Endpoint

| Feature | Tab | Button | Tests |
|---------|-----|--------|-------|
| Create User | User Mgmt | Create User | POST /users |
| Load User | User Mgmt | Load User | GET /users/{id} |
| Rule-Based Plan | Plan Gen | Generate Rule-Based | POST /plan/rule-based |
| CSP Plan | Plan Gen | Generate CSP | POST /plan/csp |
| Compare Plans | Comparison | Compare Plans | POST /plan/compare |
| Adapt Plan | Comparison | Adapt Plan | POST /plan/adapt |
| Adherence Pred | AI Pred | Predict Adherence | POST /predict/adherence |
| Get Plans | Data & Analytics | Load Plans | GET /users/{id}/plans |
| Get Comparisons | Data & Analytics | Load Comparisons | GET /users/{id}/comparisons |
| Get Predictions | Data & Analytics | Load Predictions | GET /users/{id}/predictions |
| All Workouts | Data & Analytics | View All Workouts | GET /workouts |
| Filter Workouts | Data & Analytics | Filter Workouts | GET /workouts/{cat}/{level} |

## Backend URL Configuration

By default, the app connects to `http://localhost:8000/api/v1`.

To use a different backend:
1. Go to the **Configuration** section in the left sidebar
2. Change **Backend URL** to your API endpoint
3. Changes apply instantly

Example: `http://192.168.1.100:8000/api/v1`

## Session State Features

The app maintains session state across interactions:
- **Last Plan Generated** — Used for adaptation and prediction
- **Last Comparison** — Displayed in the Comparison tab
- **Last Prediction** — Shown in the AI Prediction tab
- **Current User** — Available across all tabs

Use **"Reset Session"** button to clear all saved state.

## Visual Feedback

- ✅ Green success messages with expandable details
- ❌ Red error messages with error details
- ⏳ Spinners during API calls
- 📋 Expandable JSON responses for detailed inspection
- 📊 Metric cards with numeric summaries
- 📈 Progress bars for prediction visualization

## API Validation

Every API call shows:
- Status code
- Full response JSON (expandable)
- Error details if the request fails

This makes debugging and testing backend issues straightforward.

## Known Behavior

- **Demo User** has ID `demo_user_001` but is not stored in database
- **Plan JSON** uses full day names (Monday, not Mon)
- **Adherence Probability** ranges from 0.0 to 1.0 (displayed as 0-100%)
- **Duration** stored in minutes in the database

## Architecture

```
frontend/
├── app.py           # Single-file Streamlit application
├── README.md        # This file
├── requirements.txt # Python dependencies
└── static/          # Optional static assets
```

### Dependencies
- `streamlit>=1.28.0` — Web UI framework
- `requests>=2.31.0` — HTTP client for API calls

Install with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Backend Connection Error
- Verify backend is running: `http://localhost:8000/docs`
- Check backend URL in sidebar configuration
- Ensure MongoDB is running (check logs for "Loaded adherence model")

### Empty Responses
- User may not exist — create a new one first
- Check MongoDB connection in backend logs
- Try "Reset Session" and try again

### Form Submission Not Working
- Ensure all required fields are filled
- Check browser console for JavaScript errors
- Try refreshing the page

## Development

To modify the UI:
1. Edit `app.py` directly
2. Streamlit will hot-reload on file save
3. Check terminal for any errors

No build or compilation required!

