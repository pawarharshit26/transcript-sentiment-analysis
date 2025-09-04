from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from app.db import SessionLocal
from sqlalchemy.exc import SQLAlchemyError



class DBCall(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, unique=True, index=True, nullable=False)

    agent_id = Column(Integer, ForeignKey("agents.id"))
    customer_id = Column(Integer, index=True)
    language = Column(String)
    start_time = Column(DateTime)
    duration_seconds = Column(Integer)
    transcript = Column(Text)

    # Insights
    agent_talk_ratio = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    embedding = Column(Text, nullable=True)  # can store as JSON or vector

    # relationship back to agent
    agent = relationship("Agent", back_populates="calls")


class CallRepository:
    def __init__(self, session_factory=SessionLocal):
        """
        session_factory: a callable that returns a new DB session.
        Defaults to SessionLocal from SQLAlchemy setup.
        """
        self.session_factory = session_factory

    def create_call(self, db_call: DBCall) -> DBCall:
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

    def get_call(self, call_id: int) -> DBCall:
        with self.session_factory() as db:
            return db.query(DBCall).filter_by(call_id=call_id).first()

    def update_call(self, db_call):
        with self.session_factory() as db:
            try:
                db.commit()
                db.refresh(db_call)
                return db_call
            except SQLAlchemyError as e:
                db.rollback()
                raise e