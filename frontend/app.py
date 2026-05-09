import streamlit as st
import requests
import json

st.set_page_config(page_title="Fitness Planner", layout="wide")

st.title("Fitness Workout Planner — Frontend")

# Configuration
st.sidebar.header("Configuration")
base_url = st.sidebar.text_input("Backend base URL", value="http://localhost:8000")
user_id_input = st.sidebar.text_input("User ID (optional)")

if "user" not in st.session_state:
    st.session_state.user = None
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

def api_post(path, payload=None, params=None):
    url = base_url.rstrip("/") + path
    try:
        r = requests.post(url, json=payload, params=params, timeout=10)
        return r
    except Exception as e:
        st.error(f"Request error: {e}")
        return None

def api_get(path, params=None):
    url = base_url.rstrip("/") + path
    try:
        r = requests.get(url, params=params, timeout=10)
        return r
    except Exception as e:
        st.error(f"Request error: {e}")
        return None


with st.form("create_user_form"):
    st.subheader("Create / Load User")
    name = st.text_input("Name", value="")
    goal = st.selectbox("Primary Goal", ["weight_loss", "muscle_gain", "endurance", "general_fitness"])
    level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"], index=0)
    available_days = st.multiselect("Available Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], default=["Mon","Wed","Fri"])
    submitted = st.form_submit_button("Create User")
    if submitted:
        user_payload = {"name": name or "Anonymous", "goal": goal, "level": level, "available_days": available_days}
        r = api_post("/users", payload=user_payload)
        if r is not None and r.status_code == 200:
            data = r.json()
            st.success(f"User created: {data.get('id')}")
            st.session_state.user = {**user_payload, "id": data.get("id")}
        elif r is not None:
            st.error(f"Failed to create user: {r.status_code} {r.text}")

if user_id_input and (not st.session_state.user or st.session_state.user.get("id") != user_id_input):
    r = api_get(f"/users/{user_id_input}")
    if r is not None and r.status_code == 200:
        st.session_state.user = r.json()
        st.success(f"Loaded user {user_id_input}")
    elif r is not None:
        st.error(f"Could not load user: {r.status_code}")

if st.session_state.user:
    st.markdown("**Current user**")
    st.write(st.session_state.user)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("Generate Plans")
    if not st.session_state.user:
        st.info("Create or load a user first.")
    else:
        if st.button("Generate Rule-based Plan"):
            r = api_post("/plan/rule-based", payload=st.session_state.user)
            if r is not None and r.status_code == 200:
                st.session_state.last_plan = r.json()
                st.success("Rule-based plan generated")
                st.json(st.session_state.last_plan)
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

        if st.button("Generate CSP Plan"):
            r = api_post("/plan/csp", payload=st.session_state.user)
            if r is not None and r.status_code == 200:
                st.session_state.last_plan = r.json()
                st.success("CSP plan generated")
                st.json(st.session_state.last_plan)
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

        if st.button("Compare Plans"):
            r = api_post("/plan/compare", payload=st.session_state.user)
            if r is not None and r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

        st.markdown("**Adapt / Predict**")
        missed_day = st.text_input("Missed Day (e.g., Mon)")
        if st.button("Adapt Last Plan"):
            if not st.session_state.last_plan:
                st.info("Generate a plan first")
            else:
                # WorkoutPlan model expects {"plan": {...}}
                plan_payload = {"plan": st.session_state.last_plan.get("plan") if isinstance(st.session_state.last_plan, dict) else st.session_state.last_plan}
                params = {"missed_day": missed_day or "", "user_id": st.session_state.user.get("id", "temp")}
                r = api_post("/plan/adapt", payload=plan_payload, params=params)
                if r is not None and r.status_code == 200:
                    st.session_state.last_plan = r.json()
                    st.success("Plan adapted")
                    st.json(st.session_state.last_plan)
                else:
                    st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

        if st.button("Predict Adherence"):
            params = {}
            # optionally send plan_id if available
            plan_id = None
            r = api_post("/predict/adherence", payload=st.session_state.user, params=params)
            if r is not None and r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

with col2:
    st.header("Data & Workouts")
    if st.button("Get My Plans"):
        if not st.session_state.user:
            st.info("Load a user first")
        else:
            uid = st.session_state.user.get("id")
            r = api_get(f"/users/{uid}/plans")
            if r is not None and r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

    if st.button("Get My Comparisons"):
        if not st.session_state.user:
            st.info("Load a user first")
        else:
            uid = st.session_state.user.get("id")
            r = api_get(f"/users/{uid}/comparisons")
            if r is not None and r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

    if st.button("Get My Predictions"):
        if not st.session_state.user:
            st.info("Load a user first")
        else:
            uid = st.session_state.user.get("id")
            r = api_get(f"/users/{uid}/predictions")
            if r is not None and r.status_code == 200:
                st.json(r.json())
            else:
                st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

    st.markdown("---")
    st.subheader("Workouts")
    if st.button("List All Workouts"):
        r = api_get("/workouts")
        if r is not None and r.status_code == 200:
            st.json(r.json())
        else:
            st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

    cat = st.text_input("Category (for filter)")
    lvl = st.text_input("Level (for filter)")
    if st.button("Get Workout by Category/Level"):
        if cat and lvl:
            r = api_get(f"/workouts/{cat}/{lvl}")
        elif cat:
            r = api_get(f"/workouts/category/{cat}")
        elif lvl:
            r = api_get(f"/workouts/level/{lvl}")
        else:
            r = api_get("/workouts")
        if r is not None and r.status_code == 200:
            st.json(r.json())
        else:
            st.error(f"Error: {r.status_code} {r.text}" if r is not None else "Request failed")

st.markdown("---")
st.caption("This frontend talks to the backend FastAPI routes to create users, generate plans, and view stored data.")
