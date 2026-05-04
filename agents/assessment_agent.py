import json
from models import Assessment
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """
You are the Assessment Agent in an agentic curriculum system.
Analyse a learner's assessment history and produce a detailed mastery map.
Output a JSON object with these exact keys:
{
  "learner_id": int,
  "mastery_map": {
    "<topic_name>": {
      "mastery_score": float between 0-100,
      "mastery_level": "low" or "developing" or "proficient" or "advanced",
      "needs_reassessment": boolean,
      "misconceptions": [list of strings],
      "improvement_trend": "improving" or "stable" or "declining"
    }
  },
  "overall_mastery": float between 0-100,
  "highest_mastery_topic": string,
  "lowest_mastery_topic": string,
  "priority_topics_for_practice": [list of topic strings],
  "recommendations": string
}
"""

def run(db, learner_id):
    assessments = db.query(Assessment).filter(Assessment.learner_id == learner_id).all()

    if not assessments:
        return {"learner_id": learner_id, "mastery_map": {}, "overall_mastery": 0}

    assessment_data = [
        {
            "topic": a.topic,
            "score": a.score,
            "difficulty": a.difficulty,
            "hints_used": a.hints_used,
            "attempts": a.attempts,
            "time_taken": a.time_taken,
            "misconceptions": a.misconceptions,
        }
        for a in assessments
    ]

    learner_profile = memory.read("learner_agent", f"profile_{learner_id}") or {}

    payload = {
        "learner_id": learner_id,
        "learner_level": learner_profile.get("learning_pace", "unknown"),
        "assessments": assessment_data,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Analyse this learner's assessments: {json.dumps(payload, indent=2)}")

    try:
        mastery_map = json.loads(raw)
    except:
        mastery_map = {"raw_response": raw, "parse_error": True}

    memory.write("assessment_agent", f"mastery_{learner_id}", mastery_map)
    print(f"  ✅ Assessment Agent: Mastery map built for learner {learner_id}")
    return mastery_map
