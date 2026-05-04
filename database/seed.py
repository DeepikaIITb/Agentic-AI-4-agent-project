import random
from faker import Faker
from datetime import datetime
from sqlalchemy.orm import Session
from models import Learner, LearnerSession, Assessment, Curriculum

fake = Faker()

TOPICS = [
    "Python Basics", "Data Structures", "Algorithms", "OOP Concepts",
    "Web Development", "APIs & REST", "Databases & SQL", "Machine Learning Intro",
    "React Fundamentals", "System Design"
]

CONTENT_TYPES = ["video", "article", "exercise", "quiz"]
DIFFICULTIES = ["beginner", "intermediate", "advanced"]
LEARNING_STYLES = ["visual", "reading", "kinesthetic"]
BLOOM_LEVELS = ["remember", "understand", "apply", "analyse", "evaluate", "create"]

def seed_curriculum(db):
    items = []
    for i, topic in enumerate(TOPICS):
        for level in ["beginner", "intermediate"]:
            item = Curriculum(
                title=f"{topic} - {level.capitalize()} Guide",
                topic=topic,
                content_type=random.choice(CONTENT_TYPES),
                difficulty=level,
                prerequisites=[i - 1] if i > 0 else [],
                estimated_time=random.uniform(15, 60),
                tags=[topic.lower().replace(" ", "-"), level],
                description=f"A comprehensive {level} guide on {topic}.",
                bloom_level=random.choice(BLOOM_LEVELS),
            )
            db.add(item)
            items.append(item)
    db.commit()
    for item in items:
        db.refresh(item)
    print(f"✅ Seeded {len(items)} curriculum items")
    return items

def seed_learners(db, count=30):
    learners = []
    for _ in range(count):
        learner = Learner(
            name=fake.name(),
            email=fake.unique.email(),
            level=random.choice(DIFFICULTIES),
            learning_style=random.choice(LEARNING_STYLES),
            topics_of_interest=random.sample(TOPICS, k=random.randint(2, 5)),
            content_consumed=[],
            total_time_spent=random.uniform(0, 500),
            stall_topics=random.sample(TOPICS, k=random.randint(0, 2)),
            last_active=fake.date_time_between(start_date="-30d", end_date="now"),
        )
        db.add(learner)
        learners.append(learner)
    db.commit()
    for l in learners:
        db.refresh(l)
    print(f"✅ Seeded {len(learners)} learners")
    return learners

def seed_sessions(db, learners, curriculum):
    for learner in learners:
        consumed = random.sample(curriculum, k=random.randint(2, 8))
        content_ids = [c.id for c in consumed]
        learner.content_consumed = content_ids
        for content in consumed:
            session = LearnerSession(
                learner_id=learner.id,
                content_id=content.id,
                time_spent=random.uniform(5, content.estimated_time),
                completion_rate=random.uniform(0.3, 1.0),
                engagement_score=random.uniform(0.4, 1.0),
                session_date=fake.date_time_between(start_date="-30d", end_date="now"),
            )
            db.add(session)
    db.commit()
    print(f"✅ Seeded learner sessions")

def seed_assessments(db, learners):
    misconception_pool = [
        "confuses == with =",
        "off-by-one errors in loops",
        "misunderstands mutable defaults",
        "wrong time complexity estimate",
        "forgets to handle edge cases",
    ]
    for learner in learners:
        topics_to_assess = random.sample(TOPICS, k=random.randint(2, 5))
        for topic in topics_to_assess:
            score = random.uniform(30, 100)
            assessment = Assessment(
                learner_id=learner.id,
                topic=topic,
                score=round(score, 1),
                max_score=100.0,
                difficulty=random.choice(DIFFICULTIES),
                hints_used=random.randint(0, 5),
                attempts=random.randint(1, 3),
                time_taken=random.uniform(10, 45),
                question_breakdown={f"q{i}": random.choice(["correct", "wrong"]) for i in range(1, 6)},
                misconceptions=random.sample(misconception_pool, k=random.randint(0, 2)) if score < 70 else [],
                taken_at=fake.date_time_between(start_date="-30d", end_date="now"),
            )
            db.add(assessment)
    db.commit()
    print(f"✅ Seeded assessments")

def run_seed(db):
    print("\n🌱 Seeding database with mock data...\n")
    curriculum = seed_curriculum(db)
    learners = seed_learners(db, count=30)
    seed_sessions(db, learners, curriculum)
    seed_assessments(db, learners)
    print("\n✅ All seed data ready!\n")
