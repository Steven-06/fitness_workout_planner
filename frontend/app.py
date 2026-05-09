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
if "last_comparison" not in st.session_state:
    st.session_state.last_comparison = None
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

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
    st.session_state.last_comparison = None
    st.session_state.last_prediction = None
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

def display_response(response, title="Response"):
    """Display API response with formatting"""
    if response is None:
        return False
    
    if response.status_code == 200:
        st.success(f"✅ {title} - Success!")
        with st.expander("📋 Details", expanded=True):
            st.json(response.json())
        return True
    else:
        st.error(f"❌ {title} - Error {response.status_code}")
        with st.expander("📋 Error Details"):
            try:
                st.json(response.json())
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
                        st.session_state.user = {**user_payload, "id": data.get("id")}
                        st.success(f"✅ User created! ID: `{data.get('id')}`")
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
            st.markdown(f"**ID**: `{user_data.get('_id', 'N/A')[:8]}...`")
        
        st.markdown(f"**Available Days**: {', '.join(user_data.get('available_days', []))}")
        
        with st.expander("📋 Full User Object"):
            st.json(user_data)
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
                    r = api_post("/plan/rule-based", payload=user_data)
                    if r:
                        st.session_state.last_plan = r.json()
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
                    r = api_post("/plan/csp", payload=user_data)
                    if r:
                        st.session_state.last_plan = r.json()
                        display_response(r, "CSP Plan Generated")
        
        if st.session_state.last_plan:
            st.markdown("---")
            st.subheader("📅 Generated Weekly Plan")
            
            plan = st.session_state.last_plan.get("plan", {})
            if plan:
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                cols = [col1, col2, col3, col4, col5, col6, col7]
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                
                for i, day in enumerate(days):
                    with cols[i]:
                        day_data = plan.get(day, {})
                        workout = day_data.get("workout", "Off")
                        st.markdown(f"""
                        <div class="metric">
                            <strong>{day[:3]}</strong><br>
                            {workout}
                        </div>
                        """, unsafe_allow_html=True)
                
                with st.expander("🔍 Detailed Plan"):
                    st.json(plan)

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
                    r = api_post("/plan/compare", payload=user_data)
                    if r:
                        st.session_state.last_comparison = r.json()
                        display_response(r, "Plan Comparison")
        
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
                        plan_payload = {"plan": st.session_state.last_plan.get("plan", {})}
                        r = api_post(
                            "/plan/adapt",
                            payload=plan_payload,
                            params={"missed_day": missed_day, "user_id": user_data.get("id", "temp")}
                        )
                        if r:
                            st.session_state.last_plan = r.json()
                            display_response(r, "Plan Adapted")
        
        if st.session_state.last_comparison:
            st.markdown("---")
            st.subheader("📊 Comparison Results")
            
            comp = st.session_state.last_comparison.get("comparison", {})
            
            if comp:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 📋 Rule-Based Score")
                    rule_score = comp.get("rule_score", {})
                    st.metric("Conflicts", rule_score.get("consecutive_conflicts", "-"))
                    st.metric("Rest Days", rule_score.get("rest_days", "-"))
                    st.metric("Goal Match", rule_score.get("goal_match_score", "-"))
                
                with col2:
                    st.markdown("### 🧩 CSP Score")
                    csp_score = comp.get("csp_score", {})
                    st.metric("Conflicts", csp_score.get("consecutive_conflicts", "-"))
                    st.metric("Rest Days", csp_score.get("rest_days", "-"))
                    st.metric("Goal Match", csp_score.get("goal_match_score", "-"))
                
                with col3:
                    st.markdown("### 🏆 Verdict")
                    verdict = comp.get("verdict", "No verdict")
                    st.info(verdict)

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
                    params = {}
                    if plan_id:
                        params["plan_id"] = plan_id
                    r = api_post("/predict/adherence", payload=user_data, params=params)
                    if r:
                        st.session_state.last_prediction = r.json()
                        display_response(r, "Prediction Complete")
        
        if st.session_state.last_prediction:
            st.markdown("---")
            st.subheader("📈 Prediction Results")
            
            pred = st.session_state.last_prediction.get("prediction", {})
            
            if pred:
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
        user_id = user_data.get("id", "")
        
        col_plans, col_comps, col_preds = st.columns(3)
        
        with col_plans:
            st.subheader("📅 Your Plans")
            if st.button("Load Plans", key="load_plans", use_container_width=True):
                with st.spinner("Loading plans..."):
                    r = api_get(f"/users/{user_id}/plans")
                    display_response(r, "User Plans")
        
        with col_comps:
            st.subheader("⚖️ Your Comparisons")
            if st.button("Load Comparisons", key="load_comps", use_container_width=True):
                with st.spinner("Loading comparisons..."):
                    r = api_get(f"/users/{user_id}/comparisons")
                    display_response(r, "User Comparisons")
        
        with col_preds:
            st.subheader("🤖 Your Predictions")
            if st.button("Load Predictions", key="load_preds", use_container_width=True):
                with st.spinner("Loading predictions..."):
                    r = api_get(f"/users/{user_id}/predictions")
                    display_response(r, "User Predictions")
        
        st.markdown("---")
        st.subheader("📊 Workout Database")
        
        col_all, col_filter = st.columns([1, 1])
        
        with col_all:
            if st.button("📋 View All Workouts", use_container_width=True):
                with st.spinner("Loading workouts..."):
                    r = api_get("/workouts")
                    if r and r.status_code == 200:
                        workouts = r.json().get("workouts", [])
                        st.success(f"✅ Found {len(workouts)} workouts")
                        
                        # Group by category
                        categories = {}
                        for w in workouts:
                            cat = w.get("category", "Unknown")
                            if cat not in categories:
                                categories[cat] = []
                            categories[cat].append(w)
                        
                        for cat, items in categories.items():
                            with st.expander(f"{cat} ({len(items)} workouts)"):
                                for item in items:
                                    st.markdown(f"""
                                    **{item.get('level')}** | Intensity: {item.get('intensity')} | Duration: {item.get('duration_minutes')}min
                                    - Exercises: {', '.join(item.get('exercises', [])[:3])}...
                                    """)
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
                    
                    display_response(r, "Filtered Workouts")

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
