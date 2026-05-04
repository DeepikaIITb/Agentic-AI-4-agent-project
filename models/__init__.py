from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Learner(Base):
    __tablename__ = "learners"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    level = Column(String, default="beginner")
    learning_style = Column(String, default="visual")
    topics_of_interest = Column(JSON, default=list)
    content_consumed = Column(JSON, default=list)
    total_time_spent = Column(Float, default=0.0)
    stall_topics = Column(JSON, default=list)
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    assessments = relationship("Assessment", back_populates="learner")
    sessions = relationship("LearnerSession", back_populates="learner")

class LearnerSession(Base):
    __tablename__ = "learner_sessions"
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    content_id = Column(Integer, ForeignKey("curriculum.id"))
    time_spent = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    session_date = Column(DateTime, default=datetime.utcnow)
    learner = relationship("Learner", back_populates="sessions")
    content = relationship("Curriculum")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    topic = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    difficulty = Column(String, default="medium")
    hints_used = Column(Integer, default=0)
    attempts = Column(Integer, default=1)
    time_taken = Column(Float, default=0.0)
    question_breakdown = Column(JSON, default=dict)
    misconceptions = Column(JSON, default=list)
    taken_at = Column(DateTime, default=datetime.utcnow)
    learner = relationship("Learner", back_populates="assessments")

class Curriculum(Base):
    __tablename__ = "curriculum"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    content_type = Column(String, default="video")
    difficulty = Column(String, default="beginner")
    prerequisites = Column(JSON, default=list)
    estimated_time = Column(Float, default=30.0)
    tags = Column(JSON, default=list)
    description = Column(Text, default="")
    bloom_level = Column(String, default="remember")
    created_at = Column(DateTime, default=datetime.utcnow)
