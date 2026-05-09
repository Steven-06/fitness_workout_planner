# Frontend (Streamlit)

To run the Streamlit frontend (talks to the FastAPI backend), first start the backend (default: http://localhost:8000), then run:

```bash
pip install -r requirements.txt
streamlit run frontend/app.py
```

The app provides UI to create/load users, generate plans (rule-based or CSP), compare plans, adapt plans, predict adherence, and browse workouts. Configure the backend URL in the sidebar if your server runs elsewhere.
