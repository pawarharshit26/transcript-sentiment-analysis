import os
import json
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from datetime import datetime

import torch
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from sqlalchemy.orm import Session

from app.models.calls import DBCall, CallRepository
from app.db import SessionLocal
import structlog
from celery import shared_task

# Initialize logging
logger = structlog.get_logger()

# Initialize models (lazy loading)
MODEL_CACHE = {}

def get_sentence_transformer():
    if 'sentence_transformer' not in MODEL_CACHE:
        MODEL_CACHE['sentence_transformer'] = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2',
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
    return MODEL_CACHE['sentence_transformer']

def get_sentiment_analyzer():
    if 'sentiment_analyzer' not in MODEL_CACHE:
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        MODEL_CACHE['sentiment_analyzer'] = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
    return MODEL_CACHE['sentiment_analyzer']

def calculate_agent_talk_ratio(transcript: str) -> float:
    """
    Calculate the ratio of agent words to total words in the transcript.
    Assumes transcript format with speaker tags like 'Agent:' or 'Customer:'.
    """
    if not transcript:
        return 0.0
    
    agent_words = 0
    customer_words = 0
    
    for line in transcript.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Simple speaker detection (can be enhanced based on actual transcript format)
        if line.lower().startswith('agent:'):
            agent_words += len(line.split()) - 1  # Subtract 1 for the 'Agent:' prefix
        elif line.lower().startswith('customer:'):
            customer_words += len(line.split()) - 1  # Subtract 1 for the 'Customer:' prefix
    
    total_words = agent_words + customer_words
    return agent_words / total_words if total_words > 0 else 0.0

def analyze_sentiment(text: str) -> Dict:
    """
    Analyze sentiment of text using the sentiment analysis pipeline.
    Returns a dictionary with 'label' and 'score'.
    """
    if not text.strip():
        return {"label": "NEUTRAL", "score": 0.0}
    
    try:
        sentiment_analyzer = get_sentiment_analyzer()
        result = sentiment_analyzer(text[:512])[0]  # Limit to first 512 tokens
        
        # Convert to -1 to 1 scale
        score = result['score']
        if result['label'] == 'NEGATIVE':
            score = -score
            
        return {
            "label": result['label'],
            "score": float(score),
            "confidence": float(result['score'])
        }
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return {"label": "ERROR", "score": 0.0, "error": str(e)}

def generate_embeddings(text: str) -> List[float]:
    """
    Generate sentence embeddings for the given text.
    """
    if not text.strip():
        return []
        
    try:
        model = get_sentence_transformer()
        # Encode the text and convert to list for JSON serialization
        return model.encode(text, convert_to_tensor=False).tolist()
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        return []

def clean_transcript(transcript: str) -> str:
    """
    Clean the transcript by removing filler words and normalizing text.
    
    Args:
        transcript: Raw transcript text
        
    Returns:
        Cleaned transcript with filler words removed
    """
    if not transcript:
        return ""
    
    # Common filler words and phrases
    FILLER_WORDS = {
        'um', 'uh', 'ah', 'er', 'like', 'you know', 'i mean', 'sort of', 
        'kind of', 'basically', 'actually', 'literally', 'right', 'okay',
        'so', 'well', 'just', 'really', 'very', 'quite', 'somewhat', 'maybe',
        'i guess', 'i think', 'i suppose', 'you see', 'you know what i mean',
        'at the end of the day', 'to be honest', 'believe me', 'you know what',
        'or something', 'or whatever', 'and stuff', 'and things', 'and everything',
        'and all', 'or something like that', 'or anything', 'or whatever',
        'or so', 'or something', 'or whatever', 'i don\'t know', 'i mean',
        'you know what i\'m saying', 'if you will', 'as it were'
    }
    
    # Split into lines and process each line
    lines = []
    for line in transcript.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Split into speaker and content
        parts = line.split(':', 1)
        if len(parts) == 2:
            speaker, content = parts
            # Remove filler words from content
            words = content.split()
            cleaned_words = [
                word for word in words 
                if word.lower().strip('.,!?;:"\'()[]{}') not in FILLER_WORDS
            ]
            # Only keep non-empty lines
            if cleaned_words:
                lines.append(f"{speaker}: {' '.join(cleaned_words)}")
    
    return '\n'.join(lines)

def process_call_transcript(transcript: str) -> Dict:
    """
    Process call transcript to extract insights.
    
    Args:
        transcript: Raw transcript text
        
    Returns:
        Dictionary containing insights
    """
    if not transcript:
        return {
            "agent_talk_ratio": 0.0,
            "sentiment_score": 0.0,
            "sentiment_scores": {},
            "embedding": []
        }
    
    # Clean the transcript first
    cleaned_transcript = clean_transcript(transcript)
    
    # Calculate agent talk ratio on cleaned transcript
    agent_talk_ratio = calculate_agent_talk_ratio(cleaned_transcript)
    
    # Analyze sentiment on cleaned transcript
    sentiment_result = analyze_sentiment(cleaned_transcript)
    
    # Generate embeddings on cleaned transcript
    embedding = generate_embeddings(cleaned_transcript)
    
    return {
        "agent_talk_ratio": agent_talk_ratio,
        "sentiment_score": sentiment_result["score"],
        "sentiment_scores": {
            "overall": sentiment_result,
        },
        "embedding": embedding,
        "cleaned_transcript": cleaned_transcript  # For debugging purposes
    }

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_call_insights(self, call_id: int) -> Dict:
    """
    Celery task to generate insights for a call.
    
    Args:
        call_id: ID of the call to process
        
    Returns:
        Dict with processing results
    """
    logger.info(f"Starting insights generation for call {call_id}")
    call_repo = CallRepository()
    
    try:
        # Mark call as processing
        call_repo.update_insights(call_id, status='processing')
        
        # Get call data from database
        with SessionLocal() as db:
            call = db.query(DBCall).filter(DBCall.call_id == call_id).first()
            if not call:
                raise ValueError(f"Call with ID {call_id} not found")
            
            # Process the transcript
            insights = process_call_transcript(call.transcript)
            
            # Update call with insights
            call_repo.update_insights(
                call_id=call_id,
                agent_talk_ratio=insights['agent_talk_ratio'],
                sentiment_score=insights['sentiment_score'],
                sentiment_scores=insights['sentiment_scores'],
                embedding=insights['embedding'],
                status='completed'
            )
            
            logger.info(f"Successfully processed call {call_id}")
            return {
                "status": "success",
                "call_id": call_id,
                "agent_talk_ratio": insights['agent_talk_ratio'],
                "sentiment_score": insights['sentiment_score']
            }
            
    except Exception as e:
        error_msg = f"Error processing call {call_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Update status with error
        call_repo.update_insights(
            call_id=call_id,
            status=f"failed: {str(e)[:200]}"  # Truncate error message
        )
        
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    pass