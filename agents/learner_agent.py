import json
from models import Learner, LearnerSession
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """
You are the Learner Agent in an agentic curriculum system.
Analyse an individual learner's data and produce an actionable learner profile.
Output a JSON object with these exact keys:
{
  "learner_id": int,
  "learning_pace": "slow" or "medium" or "fast",
  "preferred_content_type": string,
  "strong_topics": [list of topic strings],
  "weak_topics": [list of topic strings],
  "stall_risk": "low" or "medium" or "high",
  "engagement_trend": "improving" or "stable" or "declining",
  "recommended_next_action": string,
  "personalization_notes": string
}
"""

def run(db, learner_id):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        return {"error": f"Learner {learner_id} not found"}

    sessions = db.query(LearnerSession).filter(LearnerSession.learner_id == learner_id).all()
    session_data = [
        {
            "content_id": s.content_id,
            "time_spent": s.time_spent,
            "completion_rate": s.completion_rate,
            "engagement_score": s.engagement_score,
        }
        for s in sessions
    ]

    learner_data = {
        "id": learner.id,
        "name": learner.name,
        "level": learner.level,
        "learning_style": learner.learning_style,
        "topics_of_interest": learner.topics_of_interest,
        "total_time_spent_minutes": learner.total_time_spent,
        "stall_topics": learner.stall_topics,
        "sessions": session_data,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Analyse this learner: {json.dumps(learner_data, indent=2)}")

    try:
        profile = json.loads(raw)
    except:
        profile = {"raw_response": raw, "parse_error": True}

    memory.write("learner_agent", f"profile_{learner_id}", profile)
    print(f"  ✅ Learner Agent: Analysed learner {learner_id} ({learner.name})")
    return profile
