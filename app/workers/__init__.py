from app.workers.ingestion import ingest_call as ingest_call
from app.workers.insights import generate_call_insights as generate_call_insights

__all__ = ['ingest_call', 'generate_call_insights']
    