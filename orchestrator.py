import time
from database.db import SessionLocal
from services.memory_store import memory
import agents.learner_agent as learner_agent
import agents.assessment_agent as assessment_agent
import agents.population_agent as population_agent
import agents.curriculum_agent as curriculum_agent

def run_cycle(db, learner_id):
    print(f"\n🤖 Starting Agentic Cycle for Learner ID: {learner_id}")
    print("=" * 50)

    start = time.time()

    print("\n📚 Step 1/5: Curriculum Agent (scanning content)...")
    curriculum_agent.run(db, learner_id)

    print("\n👤 Step 2/5: Learner Agent (analysing individual)...")
    learner_agent.run(db, learner_id)

    print("\n📝 Step 3/5: Assessment Agent (mapping mastery)...")
    assessment_agent.run(db, learner_id)

    print("\n👥 Step 4/5: Population Agent (benchmarking cohort)...")
    population_agent.run(db, learner_id)

    print("\n🎯 Step 5/5: Curriculum Agent (generating final path)...")
    final_path = curriculum_agent.run(db, learner_id)

    elapsed = round(time.time() - start, 2)

    print("\n" + "=" * 50)
    print(f"✅ Cycle complete in {elapsed} seconds!")
    print("\n📊 RESULTS SUMMARY:")

    profile = memory.read("learner_agent", f"profile_{learner_id}") or {}
    mastery = memory.read("assessment_agent", f"mastery_{learner_id}") or {}
    population = memory.read("population_agent", f"benchmarks_{learner_id}") or {}
    path = memory.read("curriculum_agent", f"path_{learner_id}") or {}

    print(f"\n👤 LEARNER PROFILE:")
    print(f"   Learning Pace    : {profile.get('learning_pace', 'N/A')}")
    print(f"   Stall Risk       : {profile.get('stall_risk', 'N/A')}")
    print(f"   Engagement Trend : {profile.get('engagement_trend', 'N/A')}")
    print(f"   Next Action      : {profile.get('recommended_next_action', 'N/A')}")

    print(f"\n📝 MASTERY MAP:")
    print(f"   Overall Mastery  : {mastery.get('overall_mastery', 'N/A')}%")
    print(f"   Highest Topic    : {mastery.get('highest_mastery_topic', 'N/A')}")
    print(f"   Lowest Topic     : {mastery.get('lowest_mastery_topic', 'N/A')}")

    print(f"\n👥 COHORT COMPARISON:")
    vs = population.get('target_learner_vs_cohort', {})
    print(f"   Percentile       : {vs.get('mastery_percentile', 'N/A')}")
    print(f"   Pace vs Cohort   : {vs.get('pace_comparison', 'N/A')}")

    print(f"\n🎯 LEARNING PATH:")
    print(f"   Next Content ID  : {path.get('next_best_content_id', 'N/A')}")
    print(f"   Coverage Gaps    : {len(path.get('coverage_gaps', []))}")
    print(f"   Path Summary     : {path.get('path_summary', 'N/A')}")
    print("=" * 50)

    return {
        "learner_profile": profile,
        "mastery_map": mastery,
        "population_benchmarks": population,
        "final_learning_path": path,
    }
