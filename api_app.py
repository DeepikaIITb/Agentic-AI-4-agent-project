"""FastAPI backend — serves learner list and runs the agentic pipeline."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database.db import SessionLocal, Learner
from database.seed import seed
from orchestrator import run_pipeline

app = FastAPI(title="Agentic Curriculum API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend HTML
FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.on_event("startup")
def startup():
    seed()

@app.get("/")
def index():
    return FileResponse(os.path.join(FRONTEND, "index.html"))

@app.get("/api/learners")
def get_learners():
    db = SessionLocal()
    learners = db.query(Learner).all()
    db.close()
    return [
        {"id": l.id, "name": l.name, "prior_knowledge": l.prior_knowledge, "learning_style": l.learning_style}
        for l in learners
    ]

@app.get("/api/run/{learner_id}")
def run_for_learner(learner_id: int):
    db = SessionLocal()
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    db.close()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    try:
        result = run_pipeline(learner_id)
        # Flatten for the frontend
        la = result["learner_analysis"]
        aa = result["assessment_analysis"]
        pa = result["population_analysis"]
        lp = result["learning_path"]
        raw = la.get("raw_profile", {})
        bench = pa.get("raw_benchmark", {})
        mastery = aa.get("raw_mastery", {})

        return {
            "learner": {
                "id": learner_id,
                "name": raw.get("name", learner.name),
                "prior_knowledge": raw.get("prior_knowledge", learner.prior_knowledge),
                "learning_style": raw.get("learning_style", learner.learning_style),
                "avg_score": raw.get("avg_assessment_score", 0),
                "avg_engagement": raw.get("avg_engagement", 0),
                "summary": la.get("summary", ""),
                "strengths": la.get("strengths", []),
                "weaknesses": la.get("weaknesses", []),
                "recommended_pace": la.get("recommended_pace", "medium"),
                "preferred_content_types": la.get("preferred_content_types", []),
            },
            "assessment": {
                "mastered_topics": aa.get("mastered_topics", []),
                "struggling_topics": aa.get("struggling_topics", []),
                "knowledge_gaps": aa.get("knowledge_gaps", []),
                "misconceptions": aa.get("misconceptions", []),
                "readiness_for_advanced": aa.get("readiness_for_advanced", False),
                "mastery_map": aa.get("mastery_map", {}),
                "raw_mastery": {
                    t: v["avg_score"] for t, v in mastery.items()
                },
            },
            "population": {
                "performance_tier": pa.get("performance_tier", "average"),
                "percentile_rank": bench.get("percentile_rank", 50),
                "learner_avg_score": bench.get("learner_avg_score", 0),
                "cohort_avg_score": bench.get("cohort_avg_score", 0),
                "peer_group_avg_score": bench.get("peer_group_avg_score", 0),
                "recommended_challenge_level": pa.get("recommended_challenge_level", "medium"),
                "peer_comparison_summary": pa.get("peer_comparison_summary", ""),
            },
            "path": {
                "learning_path": lp.get("learning_path", []),
                "total_duration_mins": lp.get("total_duration_mins", 0),
                "estimated_weeks": lp.get("estimated_weeks", 0),
                "focus_areas": lp.get("focus_areas", []),
                "path_rationale": lp.get("path_rationale", ""),
                "milestones": lp.get("milestones", []),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
