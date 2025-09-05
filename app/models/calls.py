from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from app.db import SessionLocal
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
    agent_talk_ratio = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    embedding = Column(Text, nullable=True)  # can store as JSON or vector


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
                    existing_call.embedding = db_call.embedding
                    
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
    
    