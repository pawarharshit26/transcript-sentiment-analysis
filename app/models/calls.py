from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

from app.db import Base, SessionLocal
from sqlalchemy.exc import SQLAlchemyError



class DBCall(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, unique=True, index=True, nullable=False)

    agent_id = Column(Integer)
    customer_id = Column(Integer, index=True)
    language = Column(String)
    start_time = Column(DateTime, index=True)
    duration_seconds = Column(Integer)
    transcript = Column(Text)

    # Insights
    agent_talk_ratio = Column(Float, nullable=True, comment="Ratio of agent words to total words in the call")
    sentiment_score = Column(Float, nullable=True, comment="Overall sentiment score from -1 (negative) to 1 (positive)")
    sentiment_scores = Column(JSON, nullable=True, comment="Detailed sentiment scores for different segments")
    embedding = Column(Text, nullable=True, comment="Sentence embeddings for the call transcript")
    processed_at = Column(DateTime, nullable=True, comment="When the call was processed for insights")
    processing_status = Column(String(20), default='pending', 
                            comment="Status of insight processing: pending, processing, completed, failed")


class CallRepository:
    def __init__(self, session_factory=SessionLocal):
        """
        session_factory: a callable that returns a new DB session.
        Defaults to SessionLocal from SQLAlchemy setup.
        """
        self.session_factory = session_factory

    def create(self, db_call: DBCall) -> DBCall:
        """
        Save a call into DB using managed session.
        """
        with self.session_factory() as db:
            try:
                db.add(db_call)
                db.commit()
                db.refresh(db_call)
                return db_call
            except SQLAlchemyError as e:
                db.rollback()
                raise e

    def get(self, call_id: int) -> DBCall:
        with self.session_factory() as db:
            return db.query(DBCall).filter_by(call_id=call_id).first()

    def update(self, db_call):
        with self.session_factory() as db:
            try:
                db.commit()
                db.refresh(db_call)
                return db_call
            except SQLAlchemyError as e:
                db.rollback()
                raise e

    def update_insights(
        self, 
        call_id: int, 
        agent_talk_ratio: float = None,
        sentiment_score: float = None,
        sentiment_scores: dict = None,
        embedding: list = None,
        status: str = 'completed'
    ) -> DBCall:
        """
        Update call insights in a single transaction.
        
        Args:
            call_id: ID of the call to update
            agent_talk_ratio: Ratio of agent words to total words
            sentiment_score: Overall sentiment score (-1 to 1)
            sentiment_scores: Detailed sentiment scores
            embedding: Sentence embeddings
            status: Processing status (pending, processing, completed, failed)
            
        Returns:
            Updated DBCall object
        """
        with self.session_factory() as db:
            try:
                call = db.query(DBCall).filter_by(call_id=call_id).first()
                if not call:
                    raise ValueError(f"Call with ID {call_id} not found")
                    
                if agent_talk_ratio is not None:
                    call.agent_talk_ratio = agent_talk_ratio
                if sentiment_score is not None:
                    call.sentiment_score = sentiment_score
                if sentiment_scores is not None:
                    call.sentiment_scores = sentiment_scores
                if embedding is not None:
                    call.embedding = embedding
                    
                call.processing_status = status
                call.processed_at = datetime.utcnow()
                
                db.commit()
                db.refresh(call)
                return call
                
            except SQLAlchemyError as e:
                db.rollback()
                raise e
    
    def create_or_update(self, db_call: DBCall) -> DBCall:
        """
        Create a new call or update existing one based on call_id.
        Returns the saved/updated call.
        """
        with self.session_factory() as db:
            try:
                # Check if call already exists
                existing_call = db.query(DBCall).filter_by(call_id=db_call.call_id).first()
                
                if existing_call:
                    # Update existing call
                    existing_call.agent_id = db_call.agent_id
                    existing_call.customer_id = db_call.customer_id
                    existing_call.language = db_call.language
                    existing_call.start_time = db_call.start_time
                    existing_call.duration_seconds = db_call.duration_seconds
                    existing_call.transcript = db_call.transcript
                    existing_call.agent_talk_ratio = db_call.agent_talk_ratio
                    existing_call.sentiment_score = db_call.sentiment_score
                    existing_call.agent_talk_ratio = db_call.agent_talk_ratio
                    existing_call.sentiment_score = db_call.sentiment_score
                    existing_call.sentiment_scores = db_call.sentiment_scores
                    existing_call.embedding = db_call.embedding
                    existing_call.processed_at = db_call.processed_at
                    existing_call.processing_status = db_call.processing_status
                    
                    db.commit()
                    db.refresh(existing_call)
                    return existing_call
                else:
                    # Create new call
                    db.add(db_call)
                    db.commit()
                    db.refresh(db_call)
                    return db_call
                    
            except SQLAlchemyError as e:
                db.rollback()
                raise e
    
    