import json
from models import Learner, LearnerSession
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """You are a Learner Agent. Analyse learner data and return JSON with keys:
learner_id(int), learning_pace(slow/medium/fast), preferred_content_type(string),
strong_topics(list), weak_topics(list), stall_risk(low/medium/high),
engagement_trend(improving/stable/declining), recommended_next_action(string), personalization_notes(string)"""

def run(db, learner_id):
    # Cache check
    cached = memory.read("learner_agent", f"profile_{learner_id}")
    if cached:
        print(f"  ✅ Learner Agent: Using cached profile for learner {learner_id}")
        return cached

    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        return {"error": f"Learner {learner_id} not found"}

    sessions = db.query(LearnerSession).filter(LearnerSession.learner_id == learner_id).all()
    # Send only last 5 sessions to reduce tokens
    session_data = [
        {"content_id": s.content_id, "time_spent": s.time_spent,
         "completion_rate": s.completion_rate, "engagement_score": s.engagement_score}
        for s in sessions[-5:]
    ]

    learner_data = {
        "id": learner.id, "name": learner.name, "level": learner.level,
        "learning_style": learner.learning_style,
        "topics_of_interest": learner.topics_of_interest,
        "total_time_spent_minutes": learner.total_time_spent,
        "stall_topics": learner.stall_topics,
        "sessions": session_data,
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Analyse this learner: {json.dumps(learner_data)}")
    try:
        profile = json.loads(raw)
    except:
        profile = {"raw_response": raw, "parse_error": True}

    memory.write("learner_agent", f"profile_{learner_id}", profile)
    print(f"  ✅ Learner Agent: Analysed learner {learner_id} ({learner.name})")
    return profile
