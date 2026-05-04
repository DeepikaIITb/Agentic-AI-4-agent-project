import sys, os
sys.path.insert(0, os.path.expanduser("~/agentic-curriculum"))

import streamlit as st
st.set_page_config(page_title="Agentic Curriculum System", page_icon="🎓", layout="wide")

from database.db import SessionLocal, init_db
from database.seed import seed
from models import Learner
from orchestrator import run_cycle

# Init DB
init_db()
seed()

st.title("🎓 Agentic Curriculum System")
st.caption("4-agent AI system · llama-3.3-70b · 30 learners")

# Sidebar - learner selector
db = SessionLocal()
learners = db.query(Learner).all()
db.close()

learner_options = {f"Learner {l.id} — {l.name} ({l.level})": l.id for l in learners}

st.sidebar.header("Select Learner")
selected = st.sidebar.selectbox("Learner", list(learner_options.keys()))
learner_id = learner_options[selected]

# Agent status pills
st.sidebar.markdown("---")
st.sidebar.markdown("**Agent Status**")
st.sidebar.success("✅ Learner agent")
st.sidebar.success("✅ Assessment agent")
st.sidebar.success("✅ Population agent")
st.sidebar.success("✅ Curriculum agent")

run_btn = st.sidebar.button("▶ Run Agents", use_container_width=True, type="primary")

if run_btn:
    with st.spinner("Running 4-agent pipeline... this may take 15-20 seconds..."):
        try:
            db = SessionLocal()
            result = run_cycle(db, learner_id)
            db.close()
            st.session_state["result"] = result
            st.session_state["learner_id"] = learner_id
            st.session_state["learner_name"] = next(l.name for l in learners if l.id == learner_id)
        except Exception as e:
            st.error(f"Pipeline error: {e}")

if "result" in st.session_state:
    result = st.session_state["result"]
    profile  = result.get("learner_profile", {})
    mastery  = result.get("mastery_map", {})
    pop      = result.get("population_benchmarks", {})
    path     = result.get("final_learning_path", {})
    vs       = pop.get("target_learner_vs_cohort", {})

    st.success(f"✅ Pipeline complete for **{st.session_state['learner_name']}**")

    # ── Summary metrics ───────────────────────────────────────────────
    st.subheader("📊 Summary Metrics")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Overall Mastery", f"{mastery.get('overall_mastery', 0):.1f}%")
    c2.metric("Percentile Rank", f"{vs.get('mastery_percentile', 0):.0f}th")
    c3.metric("Learning Pace", profile.get('learning_pace', '—').title())
    c4.metric("Stall Risk", profile.get('stall_risk', '—').title())
    c5.metric("Cohort Size", pop.get('cohort_size', 30))

    st.markdown("---")

    # ── Agent outputs ─────────────────────────────────────────────────
    st.subheader("🤖 Agent Outputs")
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("**👤 Learner Agent**")
            st.caption("Individual behaviour analysis")
            st.write(f"**Pace:** {profile.get('learning_pace','—')}")
            st.write(f"**Engagement:** {profile.get('engagement_trend','—')}")
            st.write(f"**Stall Risk:** {profile.get('stall_risk','—')}")
            st.write(f"**Strong Topics:** {', '.join(profile.get('strong_topics',[]))}")
            st.write(f"**Weak Topics:** {', '.join(profile.get('weak_topics',[]))}")
            st.info(profile.get('personalization_notes',''))

        with st.container(border=True):
            st.markdown("**📝 Assessment Agent**")
            st.caption("Mastery map per topic")
            st.write(f"**Overall Mastery:** {mastery.get('overall_mastery',0):.1f}%")
            st.write(f"**Highest Topic:** {mastery.get('highest_mastery_topic','—')}")
            st.write(f"**Lowest Topic:** {mastery.get('lowest_mastery_topic','—')}")
            st.write(f"**Priority Topics:** {', '.join(mastery.get('priority_topics_for_practice',[]))}")

    with col2:
        with st.container(border=True):
            st.markdown("**👥 Population Agent**")
            st.caption("Cohort benchmarking")
            st.write(f"**Percentile:** {vs.get('mastery_percentile',0):.0f}th")
            st.write(f"**Pace vs Cohort:** {vs.get('pace_comparison','—')}")
            st.write(f"**Cohort Avg Mastery:** {pop.get('cohort_avg_mastery',0):.1f}%")
            st.write(f"**Unique Strengths:** {', '.join(vs.get('unique_strengths',[]))}")
            st.info(pop.get('cohort_insights',''))

        with st.container(border=True):
            st.markdown("**🎯 Curriculum Agent**")
            st.caption("Personalised learning path")
            lp = path.get('recommended_learning_path', [])
            st.write(f"**Path Steps:** {len(lp)}")
            st.write(f"**Est. Completion:** {path.get('estimated_completion_hours',0):.1f} hours")
            st.write(f"**Coverage Gaps:** {', '.join(path.get('coverage_gaps',[]))}")
            st.info(path.get('path_summary',''))

    st.markdown("---")

    # ── Mastery chart ─────────────────────────────────────────────────
    mastery_map = mastery.get("mastery_map", {})
    if mastery_map:
        st.subheader("📈 Topic Mastery Breakdown")
        import pandas as pd
        df = pd.DataFrame([
            {"Topic": k, "Mastery Score": v.get("mastery_score", 0), "Level": v.get("mastery_level", "")}
            for k, v in mastery_map.items()
        ])
        st.bar_chart(df.set_index("Topic")["Mastery Score"])

    # ── Learning path ─────────────────────────────────────────────────
    if lp:
        st.subheader("🗺️ Recommended Learning Path")
        import pandas as pd
        df_path = pd.DataFrame([
            {
                "Step": s.get("step"),
                "Title": s.get("title",""),
                "Topic": s.get("topic",""),
                "Priority": s.get("priority",""),
                "Est. Time (mins)": s.get("estimated_time_minutes",0),
                "Reason": s.get("reason",""),
            }
            for s in lp
        ])
        st.dataframe(df_path, use_container_width=True, hide_index=True)

else:
    st.info("👈 Select a learner from the sidebar and click **Run Agents** to start the pipeline.")
    st.markdown("""
    ### How it works
    1. **Curriculum Agent** scans content catalogue
    2. **Learner Agent** analyses individual behaviour  
    3. **Assessment Agent** maps mastery per topic
    4. **Population Agent** benchmarks against 30-learner cohort
    5. **Curriculum Agent** generates personalised learning path
    """)
