import streamlit as st
import requests
import json
from datetime import datetime

# ============================================================================
# Page Configuration
# ============================================================================
st.set_page_config(
    page_title="Fitness Tracker UI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Styling & Theme
# ============================================================================
st.markdown("""
<style>
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .feature-card {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.25rem;
    }
    .metric {
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Initialization
# ============================================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None
if "rule_plan_data" not in st.session_state:
    st.session_state.rule_plan_data = None
if "csp_plan_data" not in st.session_state:
    st.session_state.csp_plan_data = None
if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = None
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "all_users" not in st.session_state:
    st.session_state.all_users = []
if "user_plans" not in st.session_state:
    st.session_state.user_plans = []
if "user_comparisons" not in st.session_state:
    st.session_state.user_comparisons = []
if "user_predictions" not in st.session_state:
    st.session_state.user_predictions = []
if "user_activity" not in st.session_state:
    st.session_state.user_activity = []
if "workouts" not in st.session_state:
    st.session_state.workouts = []

# ============================================================================
# Sidebar Configuration
# ============================================================================
st.sidebar.markdown("## ⚙️ Configuration")
base_url = st.sidebar.text_input("Backend URL", value="http://localhost:8000/api/v1", help="Base URL for API calls")

st.sidebar.markdown("---")
st.sidebar.markdown("## 📋 Quick Demo")
if st.sidebar.button("🚀 Load Demo User", help="Load a pre-configured demo user"):
    st.session_state.user = {
        "name": "Demo User",
        "goal": "weight_loss",
        "level": "Beginner",
        "available_days": ["Monday", "Wednesday", "Friday"],
        "id": "demo_user_001"
    }
    st.sidebar.success("Demo user loaded!")

if st.sidebar.button("🔄 Reset Session", help="Clear all session data"):
    st.session_state.user = None
    st.session_state.last_plan = None
    st.session_state.rule_plan_data = None
    st.session_state.csp_plan_data = None
    st.session_state.last_comparison = None
    st.session_state.last_prediction = None
    st.session_state.all_users = []
    st.session_state.user_plans = []
    st.session_state.user_comparisons = []
    st.session_state.user_predictions = []
    st.session_state.user_activity = []
    st.session_state.workouts = []
    st.sidebar.success("Session cleared!")

# ============================================================================
# API Helper Functions
# ============================================================================
def api_post(path, payload=None, params=None):
    """Make POST request to backend API"""
    url = base_url.rstrip("/") + path
    try:
        r = requests.post(url, json=payload, params=params, timeout=10)
        return r
    except Exception as e:
        st.error(f"❌ Request error: {e}")
        return None

def api_get(path, params=None):
    """Make GET request to backend API"""
    url = base_url.rstrip("/") + path
    try:
        r = requests.get(url, params=params, timeout=10)
        return r
    except Exception as e:
        st.error(f"❌ Request error: {e}")
        return None

def extract_user_id(user_data: dict) -> str:
    return user_data.get("_id") or user_data.get("id") or user_data.get("user_id") or user_data.get("userId") or ""

def format_value(value):
    if value is None:
        return ""
    if isinstance(value, dict):
        return "; ".join(f"{key}: {format_value(item)}" for key, item in value.items())
    if isinstance(value, list):
        return ", ".join(format_value(item) for item in value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return value

def show_table(title: str, rows: list, empty_message: str = "No records found"):
    st.markdown(f"**{title}**")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)

def user_rows(users: list) -> list:
    rows = []
    for user in users:
        rows.append({
            "ID": extract_user_id(user),
            "Name": user.get("name", ""),
            "Goal": user.get("goal", ""),
            "Level": user.get("level", ""),
            "Available Days": format_value(user.get("available_days", [])),
        })
    return rows

def plan_rows(plan: dict) -> list:
    rows = []
    for day, details in plan.items():
        rows.append({
            "Day": day,
            "Workout": details.get("workout", ""),
            "Exercises": format_value(details.get("exercises", [])),
        })
    return rows

def comparison_rows(comparison: dict) -> list:
    rule_score = comparison.get("rule_score", {})
    csp_score = comparison.get("csp_score", {})
    return [
        {
            "Metric": "Consecutive Conflicts",
            "Rule-Based": rule_score.get("consecutive_conflicts", ""),
            "CSP": csp_score.get("consecutive_conflicts", ""),
        },
        {
            "Metric": "Rest Days",
            "Rule-Based": rule_score.get("rest_days", ""),
            "CSP": csp_score.get("rest_days", ""),
        },
        {
            "Metric": "Goal Match Score",
            "Rule-Based": rule_score.get("goal_match_score", ""),
            "CSP": csp_score.get("goal_match_score", ""),
        },
        {
            "Metric": "Verdict",
            "Rule-Based": "",
            "CSP": comparison.get("verdict", ""),
        },
    ]

def prediction_rows(prediction: dict) -> list:
    return [
        {"Metric": "Adherence Probability", "Value": f"{prediction.get('adherence_probability', 0) * 100:.1f}%"},
        {"Metric": "Difficulty Score", "Value": f"{prediction.get('difficulty_score', 0) * 100:.1f}%"},
    ]

def workout_rows(workouts: list) -> list:
    rows = []
    for workout in workouts:
        rows.append({
            "Category": workout.get("category", ""),
            "Level": workout.get("level", ""),
            "Duration (min)": workout.get("duration_minutes", ""),
            "Intensity": workout.get("intensity", ""),
            "Exercises": format_value(workout.get("exercises", [])),
        })
    return rows

def activity_rows(activity: list) -> list:
    rows = []
    for item in activity:
        rows.append({
            "Action": item.get("action", ""),
            "Details": format_value(item.get("details", {})),
            "Timestamp": item.get("timestamp", ""),
        })
    return rows

def generic_response_rows(payload):
    if isinstance(payload, list):
        return [
            {"Item": idx + 1, "Value": format_value(item)}
            for idx, item in enumerate(payload)
        ]
    if isinstance(payload, dict):
        return [{"Field": key, "Value": format_value(value)} for key, value in payload.items()]
    return [{"Value": format_value(payload)}]

def display_response(response, title="Response"):
    """Display API response with formatting"""
    if response is None:
        return False
    
    if response.status_code == 200:
        st.success(f"✅ {title} - Success!")
        with st.expander("📋 Details", expanded=True):
            st.dataframe(generic_response_rows(response.json()), use_container_width=True, hide_index=True)
        return True
    else:
        st.error(f"❌ {title} - Error {response.status_code}")
        with st.expander("📋 Error Details"):
            try:
                st.dataframe(generic_response_rows(response.json()), use_container_width=True, hide_index=True)
            except:
                st.text(response.text)
        return False

# ============================================================================
# Main Title & Intro
# ============================================================================
st.title("🏋️ Fitness Tracker UI")
st.markdown("""
Welcome to the **Fitness Tracker** interactive interface! This UI lets you:
- Create and manage user profiles
- Generate weekly workout plans using CSP and rule-based algorithms
- Compare planning approaches
- Predict adherence likelihood with AI
- Explore workout database

**Click "Load Demo User" in the sidebar to get started instantly!**
""")

# ============================================================================
# Tab Layout
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 User Management",
    "📅 Plan Generation",
    "⚖️ Comparison & Adaptation",
    "🤖 AI Prediction",
    "📊 Data & Analytics"
])

# ============================================================================
# TAB 1: User Management
# ============================================================================
with tab1:
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("➕ Create New User")
        with st.form("create_user_form"):
            name = st.text_input("Name", placeholder="e.g., John Doe")
            goal = st.selectbox(
                "Primary Goal",
                ["weight_loss", "muscle_gain", "endurance", "general_fitness"],
                help="What is your main fitness goal?"
            )
            level = st.selectbox(
                "Experience Level",
                ["Beginner", "Intermediate"],
                help="Your current fitness level"
            )
            available_days = st.multiselect(
                "Available Training Days",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                default=["Monday", "Wednesday", "Friday"],
                help="Which days can you work out?"
            )
            submitted = st.form_submit_button("✅ Create User", use_container_width=True)
            
            if submitted:
                if not name:
                    st.error("Please enter a name")
                elif not available_days:
                    st.error("Please select at least one available day")
                else:
                    user_payload = {
                        "name": name,
                        "goal": goal,
                        "level": level,
                        "available_days": available_days
                    }
                    r = api_post("/users", payload=user_payload)
                    if r and r.status_code == 200:
                        data = r.json()
                        # Prefer the returned id/user_id, then fetch the stored user document
                        created_id = data.get("id") or data.get("user_id")
                        if created_id:
                            u = api_get(f"/users/{created_id}")
                            if u and u.status_code == 200:
                                st.session_state.user = u.json()
                                st.success(f"✅ User created! ID: `{created_id}`")
                            else:
                                # Fallback: save basic info with id
                                st.session_state.user = {**user_payload, "_id": created_id}
                                st.success(f"✅ User created! ID: `{created_id}` (partial)")
                        else:
                            st.error("Failed to read created user id from response")
                    else:
                        st.error(f"Failed to create user")
    
    with col_right:
        st.subheader("🔍 Load Existing User")
        with st.form("load_user_form"):
            user_id = st.text_input("User ID", placeholder="e.g., 507f1f77bcf86cd799439011")
            load_btn = st.form_submit_button("📥 Load User", use_container_width=True)
            
            if load_btn and user_id:
                r = api_get(f"/users/{user_id}")
                if r and r.status_code == 200:
                    st.session_state.user = r.json()
                    st.success(f"✅ User loaded!")
                else:
                    st.error(f"Could not load user (not found or error)")
    
    st.markdown("---")
    
    if st.session_state.user:
        st.subheader("👤 Current User Profile")
        user_data = st.session_state.user
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**Name**: {user_data.get('name', 'N/A')}")
        with col2:
            st.markdown(f"**Goal**: {user_data.get('goal', 'N/A')}")
        with col3:
            st.markdown(f"**Level**: {user_data.get('level', 'N/A')}")
        with col4:
            # Display the most likely id fields
            display_id = user_data.get("_id") or user_data.get("id") or user_data.get("user_id")
            if display_id:
                st.markdown(f"**ID**: `{display_id[:8]}...`")
            else:
                st.markdown("**ID**: N/A")
        
        st.markdown(f"**Available Days**: {', '.join(user_data.get('available_days', []))}")
        
        with st.expander("📋 Full User Details"):
            st.dataframe(
                [{"Field": key, "Value": format_value(value)} for key, value in user_data.items()],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("💡 Create or load a user to get started!")

# ============================================================================
# TAB 2: Plan Generation
# ============================================================================
with tab2:
    if not st.session_state.user:
        st.warning("⚠️ Please create or load a user first!")
    else:
        user_data = st.session_state.user
        st.info(f"Planning for **{user_data.get('name')}** | Goal: **{user_data.get('goal')}** | Days: {', '.join(user_data.get('available_days', []))}")
        
        col_rule, col_csp = st.columns([1, 1])

        with col_rule:
            st.subheader("📋 Rule-Based Planning")
            st.markdown("""
            Uses traditional heuristic rules to create workout schedules:
            - Follows predefined workout rotation patterns
            - Fast and predictable
            - Good baseline for comparison
            """)
            if st.button("Generate Rule-Based Plan", key="rule_plan", use_container_width=True):
                with st.spinner("Generating rule-based plan..."):
                    uid = extract_user_id(user_data)
                    r = api_post("/plan/rule-based", payload={"user_id": uid})
                    if r:
                        st.session_state.rule_plan_data = r.json()
                        st.session_state.last_plan = st.session_state.rule_plan_data
                        display_response(r, "Rule-Based Plan Generated")
        
        with col_csp:
            st.subheader("🧩 CSP Planning (AI-Optimized)")
            st.markdown("""
            Uses Constraint Satisfaction Problems for optimization:
            - Avoids consecutive same workouts
            - Enforces rest days
            - Aligns with fitness goals
            - Better constraint satisfaction
            """)
            if st.button("Generate CSP Plan", key="csp_plan", use_container_width=True):
                with st.spinner("Generating CSP plan..."):
                    uid = extract_user_id(user_data)
                    r = api_post("/plan/csp", payload={"user_id": uid})
                    if r:
                        st.session_state.csp_plan_data = r.json()
                        st.session_state.last_plan = st.session_state.csp_plan_data
                        display_response(r, "CSP Plan Generated")
        
        st.markdown("---")
        st.subheader("📅 Generated Weekly Plans")
        plan_col_1, plan_col_2 = st.columns(2)

        with plan_col_1:
            st.markdown("### Rule-Based Plan")
            if st.session_state.rule_plan_data:
                st.caption(f"Plan ID: {st.session_state.rule_plan_data.get('plan_id', 'N/A')}")
                rule_plan = st.session_state.rule_plan_data.get("plan", {})
                if rule_plan:
                    show_table("Weekly Schedule", plan_rows(rule_plan))
            else:
                st.info("Generate a rule-based plan to view it here.")

        with plan_col_2:
            st.markdown("### CSP Plan")
            if st.session_state.csp_plan_data:
                st.caption(f"Plan ID: {st.session_state.csp_plan_data.get('plan_id', 'N/A')}")
                csp_plan = st.session_state.csp_plan_data.get("plan", {})
                if csp_plan:
                    show_table("Weekly Schedule", plan_rows(csp_plan))
            else:
                st.info("Generate a CSP plan to view it here.")

# ============================================================================
# TAB 3: Comparison & Adaptation
# ============================================================================
with tab3:
    if not st.session_state.user:
        st.warning("⚠️ Please create or load a user first!")
    else:
        user_data = st.session_state.user
        
        col_compare, col_adapt = st.columns([1, 1])
        
        with col_compare:
            st.subheader("⚖️ Compare Plans")
            st.markdown("""
            Generates both rule-based and CSP plans, then compares them:
            - Constraint satisfaction metrics
            - Goal alignment scoring
            - Verdict on which approach is better
            """)
            if st.button("Generate & Compare Plans", key="compare", use_container_width=True):
                with st.spinner("Comparing rule-based vs CSP plans..."):
                    uid = extract_user_id(user_data)
                    r = api_post("/plan/compare", payload={"user_id": uid})
                    if r:
                        st.session_state.last_comparison = r.json()
                        display_response(r, "Plan Comparison")

        if st.session_state.rule_plan and st.session_state.csp_plan:
            st.markdown("---")
            st.subheader("📈 Side-by-Side Plan Comparison")
            compare_left, compare_right = st.columns(2)

            with compare_left:
                st.markdown("### Rule-Based Plan")
                show_table("Weekly Schedule", plan_rows(st.session_state.rule_plan.get("plan", {})))

            with compare_right:
                st.markdown("### CSP Plan")
                show_table("Weekly Schedule", plan_rows(st.session_state.csp_plan.get("plan", {})))
        
        with col_adapt:
            st.subheader("🔄 Adapt Missed Days")
            st.markdown("""
            Adapts your plan when you miss a workout:
            - Redistributes missed workout
            - Maintains balance
            - Preserves rest days
            """)
            missed_day = st.selectbox(
                "Which day did you miss?",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                key="missed_day_select"
            )
            if st.button("Adapt Plan", key="adapt", use_container_width=True):
                if not st.session_state.last_plan:
                    st.error("Generate a plan first!")
                else:
                    with st.spinner("Adapting plan..."):
                        plan_id = st.session_state.last_plan.get("plan_id")
                        uid = extract_user_id(user_data)
                        if not plan_id:
                            st.error("No stored plan_id available to adapt. Generate plan again to get a plan_id.")
                        else:
                            payload = {"plan_id": plan_id, "missed_day": missed_day, "user_id": uid}
                            r = api_post("/plan/adapt", payload=payload)
                            if r and r.status_code == 200:
                                st.session_state.last_plan = r.json()
                                display_response(r, "Plan Adapted")
                            else:
                                display_response(r, "Plan Adapt Failed")
        
        if st.session_state.last_comparison:
            st.markdown("---")
            st.subheader("📊 Comparison Results")
            comp = st.session_state.last_comparison.get("comparison", {})
            if comp:
                show_table("Comparison Summary", comparison_rows(comp))

# ============================================================================
# TAB 4: AI Prediction
# ============================================================================
with tab4:
    if not st.session_state.user:
        st.warning("⚠️ Please create or load a user first!")
    else:
        user_data = st.session_state.user
        
        st.subheader("🤖 Adherence Prediction")
        st.markdown("""
        Uses a neural network to predict:
        - **Adherence Probability**: Likelihood you'll stick to the plan (0-100%)
        - **Difficulty Score**: How challenging the plan is for you

        The model considers:
        - Available time for workouts
        - Number of sessions per week
        - Your previous completion history
        - Workout intensity levels
        - Your fitness goal and experience level
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Configure Prediction")
            
            # Optional: Use a generated plan for context
            use_plan = st.checkbox("Use generated plan for prediction", value=False)
            plan_id = None
            if use_plan and st.session_state.last_plan:
                plan_id = st.session_state.last_plan.get("plan_id")
                st.info(f"Using plan: `{plan_id[:8] if plan_id else 'N/A'}...`")
        
        with col2:
            st.markdown("### Run Prediction")
            if st.button("🔮 Predict Adherence", use_container_width=True):
                with st.spinner("Running AI prediction..."):
                    uid = extract_user_id(user_data)
                    payload = {"user_id": uid}
                    if plan_id:
                        payload["plan_id"] = plan_id
                    r = api_post("/predict/adherence", payload=payload)
                    if r:
                        st.session_state.last_prediction = r.json()
                        display_response(r, "Prediction Complete")
        
        if st.session_state.last_prediction:
            st.markdown("---")
            st.subheader("📈 Prediction Results")
            
            pred = st.session_state.last_prediction.get("prediction", {})
            
            if pred:
                show_table("Prediction Summary", prediction_rows(pred))
                col1, col2 = st.columns(2)
                
                with col1:
                    adherence = pred.get("adherence_probability", 0) * 100
                    st.metric(
                        "Adherence Probability",
                        f"{adherence:.1f}%",
                        delta=f"{'High confidence' if adherence > 70 else 'Moderate' if adherence > 50 else 'Low confidence'}",
                        delta_color="off"
                    )
                
                with col2:
                    difficulty = pred.get("difficulty_score", 0)
                    difficulty_pct = difficulty * 100
                    st.metric(
                        "Difficulty Score",
                        f"{difficulty_pct:.1f}%",
                        delta=f"{'Challenging' if difficulty > 0.6 else 'Moderate' if difficulty > 0.3 else 'Easy'}",
                        delta_color="off"
                    )
                
                # Visualization
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.progress(min(adherence / 100, 1.0), f"Adherence: {adherence:.1f}%")
                with col2:
                    st.progress(min(difficulty, 1.0), f"Difficulty: {difficulty_pct:.1f}%")

# ============================================================================
# TAB 5: Data & Analytics
# ============================================================================
with tab5:
    if not st.session_state.user:
        st.warning("⚠️ Please create or load a user first!")
    else:
        user_data = st.session_state.user
        user_id = (user_data.get("_id") or user_data.get("id") or user_data.get("user_id") or "")
        
        st.subheader("👥 System Users")
        if st.button("Load All Users", use_container_width=True):
            with st.spinner("Loading all users..."):
                r = api_get("/users")
                if r and r.status_code == 200:
                    users = r.json()
                    st.session_state.all_users = users if isinstance(users, list) else users.get("users", [])
                    display_response(r, "All Users")
                else:
                    st.error("Failed to load users")

        if st.session_state.all_users:
            show_table("All Users", user_rows(st.session_state.all_users))

            user_choices = {
                f"{user.get('name', 'Unknown')} | {extract_user_id(user)[:8]}": extract_user_id(user)
                for user in st.session_state.all_users
                if extract_user_id(user)
            }
            if user_choices:
                selected_user_label = st.selectbox("Load a user from the system", list(user_choices.keys()))
                if st.button("Load Selected User", use_container_width=True):
                    selected_user_id = user_choices[selected_user_label]
                    r = api_get(f"/users/{selected_user_id}")
                    if r and r.status_code == 200:
                        st.session_state.user = r.json()
                        st.success("Selected user loaded.")
                    else:
                        st.error("Could not load selected user")
        
        st.markdown("---")
        
        col_plans, col_comps, col_preds = st.columns(3)
        
        with col_plans:
            st.subheader("📅 Your Plans")
            if st.button("Load Plans", key="load_plans", use_container_width=True):
                with st.spinner("Loading plans..."):
                    r = api_get(f"/users/{user_id}/plans")
                    if r and r.status_code == 200:
                        plans_payload = r.json().get("plans", [])
                        st.session_state.user_plans = plans_payload
                        display_response(r, "User Plans")
                        if plans_payload:
                            for idx, plan in enumerate(plans_payload, start=1):
                                with st.expander(f"Plan {idx} | {plan.get('plan_model', 'unknown')} | {plan.get('plan_id', 'no id')}"):
                                    show_table("Plan Details", plan_rows(plan.get("plan_data", {})))
                    else:
                        st.error("Failed to load plans")
        
        with col_comps:
            st.subheader("⚖️ Your Comparisons")
            if st.button("Load Comparisons", key="load_comps", use_container_width=True):
                with st.spinner("Loading comparisons..."):
                    r = api_get(f"/users/{user_id}/comparisons")
                    if r and r.status_code == 200:
                        comps_payload = r.json().get("comparisons", [])
                        st.session_state.user_comparisons = comps_payload
                        display_response(r, "User Comparisons")
                        if comps_payload:
                            show_table(
                                "Comparisons",
                                [
                                    {
                                        "Comparison ID": item.get("comparison_id", ""),
                                        "Created At": item.get("created_at", ""),
                                        "Verdict": item.get("comparison_data", {}).get("verdict", ""),
                                    }
                                    for item in comps_payload
                                ],
                            )
                    else:
                        st.error("Failed to load comparisons")
        
        with col_preds:
            st.subheader("🤖 Your Predictions")
            if st.button("Load Predictions", key="load_preds", use_container_width=True):
                with st.spinner("Loading predictions..."):
                    r = api_get(f"/users/{user_id}/predictions")
                    if r and r.status_code == 200:
                        preds_payload = r.json().get("predictions", [])
                        st.session_state.user_predictions = preds_payload
                        display_response(r, "User Predictions")
                        if preds_payload:
                            show_table(
                                "Predictions",
                                [
                                    {
                                        "Prediction ID": item.get("prediction_id", ""),
                                        "Created At": item.get("created_at", ""),
                                        "Adherence": f"{item.get('prediction_data', {}).get('adherence_probability', 0) * 100:.1f}%",
                                        "Difficulty": f"{item.get('prediction_data', {}).get('difficulty_score', 0) * 100:.1f}%",
                                    }
                                    for item in preds_payload
                                ],
                            )
                    else:
                        st.error("Failed to load predictions")

        st.markdown("---")
        st.subheader("🕘 Current User Activity")
        activity_limit = st.slider("Activity items to load", min_value=5, max_value=50, value=20, step=5)
        if st.button("Load Activity", use_container_width=True):
            with st.spinner("Loading activity..."):
                r = api_get(f"/users/{user_id}/activity", params={"limit": activity_limit})
                if r and r.status_code == 200:
                    activity_payload = r.json().get("activity", [])
                    st.session_state.user_activity = activity_payload
                    display_response(r, "User Activity")
                    show_table("Activity Log", activity_rows(activity_payload))
                else:
                    st.error("Failed to load activity")
        
        st.markdown("---")
        st.subheader("📊 Workout Database")
        
        col_all, col_filter = st.columns([1, 1])
        
        with col_all:
            if st.button("📋 View All Workouts", use_container_width=True):
                with st.spinner("Loading workouts..."):
                    r = api_get("/workouts")
                    if r and r.status_code == 200:
                        workouts = r.json().get("workouts", [])
                        st.session_state.workouts = workouts
                        st.success(f"✅ Found {len(workouts)} workouts")
                        show_table("All Workouts", workout_rows(workouts))
                    else:
                        st.error("Failed to load workouts")
        
        with col_filter:
            st.markdown("**Filter Workouts**")
            category = st.selectbox(
                "Category",
                ["All", "Cardio", "Upper Body", "Lower Body", "Full Body", "Rest"],
                key="filter_cat"
            )
            level = st.selectbox(
                "Level",
                ["All", "Beginner", "Intermediate"],
                key="filter_level"
            )
            
            if st.button("🔍 Filter Workouts", use_container_width=True):
                with st.spinner("Filtering workouts..."):
                    if category != "All" and level != "All":
                        r = api_get(f"/workouts/{category}/{level}")
                    elif category != "All":
                        r = api_get(f"/workouts/category/{category}")
                    elif level != "All":
                        r = api_get(f"/workouts/level/{level}")
                    else:
                        r = api_get("/workouts")
                    if r and r.status_code == 200:
                        payload = r.json()
                        filtered_workouts = payload.get("workouts", []) if isinstance(payload, dict) else payload
                        show_table("Filtered Workouts", workout_rows(filtered_workouts))
                    else:
                        st.error("Failed to filter workouts")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
    <strong>Fitness Tracker UI</strong> | Built with Streamlit & FastAPI
    <br>
    Backend: <code>http://localhost:8000/api/v1</code>
</div>
""", unsafe_allow_html=True)
