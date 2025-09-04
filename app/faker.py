from faker import Faker
import random
from datetime import datetime, timedelta
from pydantic import BaseModel


fake = Faker()



class FakerDB:
    @staticmethod
    def get_call(call_id: int) -> dict:
        agent_id = random.randint(1, 10)
        customer_id = random.randint(1000, 9999)
        start_time = datetime.utcnow() - timedelta(minutes=random.randint(0, 1000))
        duration = random.randint(60, 600)
        transcript = " ".join(fake.sentences(nb=random.randint(3, 8)))


        return {
            "call_id": call_id,
            "agent_id": agent_id,
            "customer_id": customer_id,
            "language": "en",
            "start_time": start_time,
            "duration_seconds": duration,
            "transcript": transcript,
        }
    

        