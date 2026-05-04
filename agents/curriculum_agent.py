import json
from models import Curriculum
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """You are a Curriculum Agent. Generate a personalized learning path and return JSON with keys:
learner_id(int), current_level_assessment(string), coverage_gaps(list),
recommended_learning_path(list of step/content_id/title/topic/reason/estimated_time_minutes/priority),
content_to_revisit(list of content_id/title/reason),
next_best_content_id(int), path_summary(string), estimated_completion_hours(float)"""

def run(db, learner_id):
    # Cache check
    cached = memory.read("curriculum_agent", f"path_{learner_id}")
    if cached:
        print(f"  ✅ Curriculum Agent: Using cached path for learner {learner_id}")
        return cached

    all_content = db.query(Curriculum).all()
    # Send only essential content fields
    content_catalog = [
        {"id": c.id, "title": c.title, "topic": c.topic,
         "difficulty": c.difficulty, "estimated_time": c.estimated_time}
        for c in all_content
    ]

    learner_profile = memory.read("learner_agent", f"profile_{learner_id}") or {}
    mastery_map = memory.read("assessment_agent", f"mastery_{learner_id}") or {}
    population_benchmarks = memory.read("population_agent", f"benchmarks_{learner_id}") or {}

    # Send only key fields from each agent — not full objects
    payload = {
        "learner_id": learner_id,
        "level": learner_profile.get("learning_pace", "medium"),
        "strong_topics": learner_profile.get("strong_topics", []),
        "weak_topics": learner_profile.get("weak_topics", []),
        "overall_mastery": mastery_map.get("overall_mastery", 0),
        "priority_topics": mastery_map.get("priority_topics_for_practice", []),
        "percentile": population_benchmarks.get("target_learner_vs_cohort", {}).get("mastery_percentile", 50),
        "available_content": content_catalog,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Generate learning path: {json.dumps(payload)}")
    try:
        learning_path = json.loads(raw)
    except:
        learning_path = {"raw_response": raw, "parse_error": True}

    memory.write("curriculum_agent", f"path_{learner_id}", learning_path)
    print(f"  ✅ Curriculum Agent: Personalized path generated for learner {learner_id}")
    return learning_path
