import json
from models import Learner, Assessment
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """You are a Population Agent. Benchmark a learner against cohort and return JSON with keys:
cohort_size(int), cohort_avg_mastery(float), cohort_common_struggles(list),
cohort_fastest_completed_topics(list),
target_learner_vs_cohort(dict with mastery_percentile/pace_comparison/unique_strengths/areas_behind_cohort),
cohort_insights(string), population_recommended_path(list)"""

def run(db, learner_id):
    # Cache check
    cached = memory.read("population_agent", f"benchmarks_{learner_id}")
    if cached:
        print(f"  ✅ Population Agent: Using cached benchmarks for learner {learner_id}")
        return cached

    # Pre-compute cohort stats in Python — don't send raw data to LLM
    all_assessments = db.query(Assessment).filter(Assessment.learner_id != learner_id).all()
    topic_scores = {}
    for a in all_assessments:
        topic_scores.setdefault(a.topic, []).append(a.score)
    topic_avg = {t: round(sum(s)/len(s), 1) for t, s in topic_scores.items()}
    cohort_avg = round(sum(topic_avg.values()) / len(topic_avg), 1) if topic_avg else 0

    all_learners = db.query(Learner).filter(Learner.id != learner_id).all()
    levels = {l: sum(1 for x in all_learners if x.level == l) for l in ["beginner","intermediate","advanced"]}

    mastery_map = memory.read("assessment_agent", f"mastery_{learner_id}") or {}
    learner_mastery = mastery_map.get("overall_mastery", 0)

    # Send only summary stats — not raw learner data
    payload = {
        "target_learner_id": learner_id,
        "target_overall_mastery": learner_mastery,
        "target_weak_topics": mastery_map.get("priority_topics_for_practice", []),
        "cohort_size": len(all_learners),
        "cohort_avg_mastery": cohort_avg,
        "cohort_topic_avgs": topic_avg,
        "cohort_level_distribution": levels,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Benchmark learner: {json.dumps(payload)}")
    try:
        population_insights = json.loads(raw)
    except:
        population_insights = {"raw_response": raw, "parse_error": True}

    memory.write("population_agent", f"benchmarks_{learner_id}", population_insights)
    print(f"  ✅ Population Agent: Cohort benchmarks ready for learner {learner_id}")
    return population_insights
