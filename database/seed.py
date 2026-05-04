import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from faker import Faker
from datetime import datetime, timedelta
import random
from database.db import SessionLocal, init_db
from models import Learner, LearnerSession, Assessment, Curriculum

fake = Faker()
random.seed(42)

TOPICS = ["algebra", "geometry", "statistics", "calculus", "linear_algebra",
          "probability", "python_basics", "data_structures", "algorithms", "machine_learning"]
STYLES = ["visual", "auditory", "kinesthetic"]
LEVELS = ["beginner", "intermediate", "advanced"]
DIFFICULTIES = ["easy", "medium", "hard"]
CONTENT_TYPES = ["video", "quiz", "reading", "exercise"]

def seed():
    init_db()
    db = SessionLocal()

    if db.query(Learner).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    for i in range(20):
        item = Curriculum(
            title=f"{random.choice(TOPICS).replace('_',' ').title()} – {fake.bs().title()[:40]}",
            topic=random.choice(TOPICS),
            difficulty=random.choice(DIFFICULTIES),
            content_type=random.choice(CONTENT_TYPES),
            estimated_time=random.randint(10, 60),
        )
        db.add(item)
    db.commit()
    items = db.query(Curriculum).all()

    for _ in range(30):
        learner = Learner(
            name=fake.name(),
            email=fake.unique.email(),
            level=random.choice(LEVELS),
            learning_style=random.choice(STYLES),
            topics_of_interest=random.sample(TOPICS, 3),
            total_time_spent=round(random.uniform(10, 300), 1),
            stall_topics=random.sample(TOPICS, 2),
        )
        db.add(learner)
    db.commit()
    learners = db.query(Learner).all()

    base = datetime.utcnow() - timedelta(days=60)
    for learner in learners:
        for item in random.sample(items, k=random.randint(4, 12)):
            session = LearnerSession(
                learner_id=learner.id,
                content_id=item.id,
                time_spent=round(random.uniform(5, item.estimated_time), 1),
                completion_rate=round(random.uniform(0.3, 1.0), 2),
                engagement_score=round(random.uniform(0.4, 1.0), 2),
                session_date=base + timedelta(days=random.randint(0, 55)),
            )
            db.add(session)

        for topic in random.sample(TOPICS, k=random.randint(3, 7)):
            assessment = Assessment(
                learner_id=learner.id,
                topic=topic,
                score=round(random.uniform(30, 100), 1),
                taken_at=base + timedelta(days=random.randint(0, 55)),
                time_taken=random.randint(10, 45),
            )
            db.add(assessment)

    db.commit()
    db.close()
    print("✅ Seeded 30 learners, 20 curriculum items, sessions & assessments.")

if __name__ == "__main__":
    seed()

def run_seed(db):
    seed()

