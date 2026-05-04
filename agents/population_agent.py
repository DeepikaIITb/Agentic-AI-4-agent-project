import json
from models import Learner, Assessment, LearnerSession
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """
You are the Population Agent in an agentic curriculum system.
Analyse cohort-level data and benchmark one learner against the population.
Output a JSON object with these exact keys:
{
  "cohort_size": int,
  "cohort_avg_mastery": float between 0-100,
  "cohort_common_struggles": [list of topic strings],
  "cohort_fastest_completed_topics": [list of topic strings],
  "target_learner_vs_cohort": {
    "mastery_percentile": float between 0-100,
    "pace_comparison": "slower" or "similar" or "faster",
    "unique_strengths": [list of topics where target outperforms cohort],
    "areas_behind_cohort": [list of topics where target underperforms]
  },
  "cohort_insights": string,
  "population_recommended_path": [list of topic strings in sequence]
}
"""

def run(db, learner_id):
    all_learners = db.query(Learner).filter(Learner.id != learner_id).all()
    all_assessments = db.query(Assessment).filter(Assessment.learner_id != learner_id).all()

    topic_scores = {}
    for a in all_assessments:
        topic_scores.setdefault(a.topic, []).append(a.score)

    topic_avg = {
        topic: round(sum(scores) / len(scores), 1)
        for topic, scores in topic_scores.items()
    }

    cohort_data = {
        "cohort_size": len(all_learners),
        "topic_avg_scores": topic_avg,
        "levels_distribution": {
            level: sum(1 for l in all_learners if l.level == level)
            for level in ["beginner", "intermediate", "advanced"]
        },
    }

    learner_profile = memory.read("learner_agent", f"profile_{learner_id}") or {}
    mastery_map = memory.read("assessment_agent", f"mastery_{learner_id}") or {}

    payload = {
        "target_learner_id": learner_id,
        "target_learner_profile": learner_profile,
        "target_learner_mastery": mastery_map,
        "cohort_data": cohort_data,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Benchmark this learner against the cohort: {json.dumps(payload, indent=2)}")

    try:
        population_insights = json.loads(raw)
    except:
        population_insights = {"raw_response": raw, "parse_error": True}

    memory.write("population_agent", f"benchmarks_{learner_id}", population_insights)
    print(f"  ✅ Population Agent: Cohort benchmarks ready for learner {learner_id}")
    return population_insights
