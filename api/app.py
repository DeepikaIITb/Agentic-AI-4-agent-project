import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from database.db import SessionLocal, init_db
from database.seed import seed

app = FastAPI(title="Agentic Curriculum API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.on_event("startup")
def startup():
    seed()

@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND, "index.html"))

@app.get("/api/learners")
def get_learners():
    from models import Learner
    db = SessionLocal()
    learners = db.query(Learner).all()
    db.close()
    return [
        {"id": l.id, "name": l.name, "prior_knowledge": l.level, "learning_style": l.learning_style}
        for l in learners
    ]

@app.get("/api/run/{learner_id}")
def run_for_learner(learner_id: int):
    from models import Learner
    from orchestrator import run_cycle
    db = SessionLocal()
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        db.close()
        raise HTTPException(status_code=404, detail="Learner not found")
    try:
        result = run_cycle(db, learner_id)
        db.close()
        profile = result.get("learner_profile", {})
        mastery  = result.get("mastery_map", {})
        pop      = result.get("population_benchmarks", {})
        path     = result.get("final_learning_path", {})
        vs       = pop.get("target_learner_vs_cohort", {})
        lp       = path.get("recommended_learning_path", [])

        return {
            "learner": {
                "id": learner_id,
                "name": learner.name,
                "prior_knowledge": learner.level,
                "learning_style": learner.learning_style,
                "avg_score": mastery.get("overall_mastery", 0),
                "avg_engagement": 0.75,
                "summary": profile.get("personalization_notes", ""),
                "strengths": profile.get("strong_topics", []),
                "weaknesses": profile.get("weak_topics", []),
                "recommended_pace": profile.get("learning_pace", "medium"),
                "preferred_content_types": [profile.get("preferred_content_type", "video")],
            },
            "assessment": {
                "mastered_topics": profile.get("strong_topics", []),
                "struggling_topics": profile.get("weak_topics", []),
                "knowledge_gaps": path.get("coverage_gaps", []),
                "misconceptions": [],
                "readiness_for_advanced": mastery.get("overall_mastery", 0) > 75,
                "mastery_map": mastery.get("mastery_map", {}),
                "raw_mastery": {
                    k: v.get("mastery_score", 0)
                    for k, v in mastery.get("mastery_map", {}).items()
                },
            },
            "population": {
                "performance_tier": "above_average" if vs.get("mastery_percentile", 50) > 60 else "average",
                "percentile_rank": vs.get("mastery_percentile", 50),
                "learner_avg_score": mastery.get("overall_mastery", 0),
                "cohort_avg_score": pop.get("cohort_avg_mastery", 0),
                "peer_group_avg_score": pop.get("cohort_avg_mastery", 0),
                "recommended_challenge_level": "hard" if vs.get("mastery_percentile", 50) > 75 else "medium",
                "peer_comparison_summary": vs.get("pace_comparison", ""),
            },
            "path": {
                "learning_path": [
                    {
                        "item_id": step.get("content_id"),
                        "title": step.get("title", ""),
                        "topic": step.get("topic", ""),
                        "difficulty": "medium",
                        "content_type": "video",
                        "duration_mins": int(step.get("estimated_time_minutes", 30)),
                        "reason": step.get("reason", ""),
                    }
                    for step in lp
                ],
                "total_duration_mins": int(path.get("estimated_completion_hours", 1) * 60),
                "estimated_weeks": round(path.get("estimated_completion_hours", 1) / 5, 1),
                "focus_areas": path.get("coverage_gaps", []),
                "path_rationale": path.get("path_summary", ""),
                "milestones": [f"Complete step {s.get('step')}: {s.get('title','')}" for s in lp[:3]],
            },
        }
    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=str(e))
