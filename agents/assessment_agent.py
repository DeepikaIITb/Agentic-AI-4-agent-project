import json
from models import Assessment
from services.claude_client import call_claude_json
from services.memory_store import memory

SYSTEM_PROMPT = """You are an Assessment Agent. Analyse assessments and return JSON with keys:
learner_id(int), mastery_map(dict of topic->mastery_score/mastery_level/needs_reassessment/misconceptions/improvement_trend),
overall_mastery(float 0-100), highest_mastery_topic(string), lowest_mastery_topic(string),
priority_topics_for_practice(list), recommendations(string)"""

def run(db, learner_id):
    # Cache check
    cached = memory.read("assessment_agent", f"mastery_{learner_id}")
    if cached:
        print(f"  ✅ Assessment Agent: Using cached mastery for learner {learner_id}")
        return cached

    assessments = db.query(Assessment).filter(Assessment.learner_id == learner_id).all()
    if not assessments:
        return {"learner_id": learner_id, "mastery_map": {}, "overall_mastery": 0}

    # Summarise assessments instead of sending raw data
    topic_scores = {}
    for a in assessments:
        topic_scores.setdefault(a.topic, []).append(a.score)
    summary = {topic: round(sum(s)/len(s), 1) for topic, s in topic_scores.items()}

    learner_profile = memory.read("learner_agent", f"profile_{learner_id}") or {}
    payload = {
        "learner_id": learner_id,
        "topic_avg_scores": summary,
        "weak_topics": learner_profile.get("weak_topics", []),
    }

    raw = call_claude_json(SYSTEM_PROMPT, f"Build mastery map: {json.dumps(payload)}")
    try:
        mastery_map = json.loads(raw)
    except:
        mastery_map = {"raw_response": raw, "parse_error": True}

    memory.write("assessment_agent", f"mastery_{learner_id}", mastery_map)
    print(f"  ✅ Assessment Agent: Mastery map built for learner {learner_id}")
    return mastery_map
