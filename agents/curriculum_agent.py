import json
from models import Curriculum
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """
You are the Curriculum Agent in an agentic curriculum system.
Map available curriculum content to a learner's needs and generate a personalized learning path.
Output a JSON object with these exact keys:
{
  "learner_id": int,
  "current_level_assessment": string,
  "coverage_gaps": [list of topics the learner hasn't touched but should],
  "recommended_learning_path": [
    {
      "step": int,
      "content_id": int,
      "title": string,
      "topic": string,
      "reason": string,
      "estimated_time_minutes": float,
      "priority": "high" or "medium" or "low"
    }
  ],
  "content_to_revisit": [
    {
      "content_id": int,
      "title": string,
      "reason": string
    }
  ],
  "next_best_content_id": int,
  "path_summary": string,
  "estimated_completion_hours": float
}
"""

def run(db, learner_id):
    all_content = db.query(Curriculum).all()

    content_catalog = [
        {
            "id": c.id,
            "title": c.title,
            "topic": c.topic,
            "content_type": c.content_type,
            "difficulty": c.difficulty,
            "prerequisites": c.prerequisites,
            "estimated_time": c.estimated_time,
            "bloom_level": c.bloom_level,
        }
        for c in all_content
    ]

    learner_profile = memory.read("learner_agent", f"profile_{learner_id}") or {}
    mastery_map = memory.read("assessment_agent", f"mastery_{learner_id}") or {}
    population_benchmarks = memory.read("population_agent", f"benchmarks_{learner_id}") or {}

    payload = {
        "learner_id": learner_id,
        "learner_profile": learner_profile,
        "mastery_map": mastery_map,
        "population_benchmarks": population_benchmarks,
        "available_content": content_catalog,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Generate a personalized learning path: {json.dumps(payload, indent=2)}")

    try:
        learning_path = json.loads(raw)
    except:
        learning_path = {"raw_response": raw, "parse_error": True}

    memory.write("curriculum_agent", f"path_{learner_id}", learning_path)
    print(f"  ✅ Curriculum Agent: Personalized path generated for learner {learner_id}")
    return learning_path
