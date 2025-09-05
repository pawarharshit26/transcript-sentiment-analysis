from faker import Faker
import random
from datetime import datetime, timedelta
from pydantic import BaseModel


fake = Faker()



class FakerDB:
    
    # Conversation patterns for different issue types
    ISSUE_TYPES = [
        "billing", "technical_support", "service_outage", "account_access", 
        "product_inquiry", "complaint", "cancellation", "upgrade_request"
    ]
    
    @staticmethod
    def _generate_customer_issue(issue_type: str) -> str:
        """Generate a customer's opening statement based on issue type"""
        issues = {
            "billing": [
                f"Hi, I have a question about a charge of ${fake.random_int(10, 200)} on my bill.",
                f"I was charged for something I didn't order. Can you help me understand this?",
                f"My bill seems higher than usual this month. Can you explain why?"
            ],
            "technical_support": [
                f"I'm having trouble with my {fake.random_element(['internet', 'email', 'account', 'app'])}. It's not working properly.",
                f"My {fake.random_element(['connection', 'service', 'device'])} keeps {fake.random_element(['disconnecting', 'freezing', 'crashing'])}.",
                f"I can't access my account. It says my {fake.random_element(['password', 'username', 'credentials'])} is invalid."
            ],
            "service_outage": [
                f"My {fake.random_element(['internet', 'phone', 'TV'])} service has been down since {fake.time()}.",
                f"Is there an outage in my area? My service isn't working.",
                f"I've been without service for {fake.random_int(1, 8)} hours. What's going on?"
            ],
            "account_access": [
                f"I can't log into my account using my email {fake.email()}.",
                f"I forgot my password and the reset link isn't working.",
                f"My account seems to be locked. Can you help me unlock it?"
            ],
            "product_inquiry": [
                f"I'm interested in upgrading to a {fake.random_element(['faster', 'premium', 'business'])} plan.",
                f"What {fake.random_element(['internet', 'phone', 'TV'])} packages do you offer?",
                f"Can you tell me about your {fake.random_element(['latest', 'new', 'promotional'])} offers?"
            ],
            "complaint": [
                f"I'm very frustrated with the service quality lately.",
                f"This is the {fake.random_int(2, 5)}th time I'm calling about the same issue.",
                f"I've been a customer for {fake.random_int(2, 10)} years and the service has gotten worse."
            ],
            "cancellation": [
                f"I want to cancel my {fake.random_element(['internet', 'phone', 'TV'])} service.",
                f"I'm thinking about switching providers. What can you offer to keep me?",
                f"I need to downgrade my plan due to budget constraints."
            ],
            "upgrade_request": [
                f"I need faster internet for {fake.random_element(['work', 'gaming', 'streaming'])}.",
                f"Can I add {fake.random_element(['premium channels', 'more data', 'international calling'])} to my plan?",
                f"What would it cost to upgrade to your {fake.random_element(['premium', 'business', 'unlimited'])} package?"
            ]
        }
        return random.choice(issues.get(issue_type, ["I need help with my account."]))

    @staticmethod
    def _generate_agent_response(context: str) -> str:
        """Generate agent responses based on context"""
        responses = [
            f"I'd be happy to help you with that. Let me {fake.random_element(['check your account', 'look into this', 'review your services'])}.",
            f"I understand your concern. Can you provide me with your {fake.random_element(['account number', 'phone number', 'email address'])}?",
            f"I apologize for the {fake.random_element(['inconvenience', 'trouble', 'issue'])}. Let me see what I can do to resolve this.",
            f"Thank you for contacting us. I'll {fake.random_element(['investigate this', 'check our system', 'review your account'])} right away.",
            f"I see what's happening here. Let me {fake.random_element(['fix this for you', 'update your account', 'process this change'])}."
        ]
        return random.choice(responses)

    @staticmethod
    def _generate_conversation(call_id: int) -> str:
        """Generate a dynamic customer support conversation using Faker"""
        fake.seed_instance(call_id)
        random.seed(call_id)
        
        # Choose random issue type
        issue_type = random.choice(FakerDB.ISSUE_TYPES)
        
        # Generate conversation
        transcript_parts = []
        
        # Customer opens with issue
        customer_issue = FakerDB._generate_customer_issue(issue_type)
        transcript_parts.append(f"Customer: {customer_issue}")
        
        # Agent responds
        agent_greeting = FakerDB._generate_agent_response("greeting")
        transcript_parts.append(f"Agent: {agent_greeting}")
        
        # Generate 3-6 more exchanges
        num_exchanges = random.randint(3, 6)
        for i in range(num_exchanges):
            if i % 2 == 0:  # Customer turn
                customer_msg = fake.sentence()
                if "?" not in customer_msg:
                    customer_msg = customer_msg.rstrip('.') + "?"
                transcript_parts.append(f"Customer: {customer_msg}")
            else:  # Agent turn
                agent_msg = FakerDB._generate_agent_response("follow_up")
                transcript_parts.append(f"Agent: {agent_msg}")
        
        # End with resolution
        if random.choice([True, False]):
            transcript_parts.append(f"Customer: {fake.random_element(['Thank you for your help!', 'That resolves my issue.', 'Perfect, thanks!'])}")
        else:
            transcript_parts.append(f"Agent: {fake.random_element(['Is there anything else I can help you with?', 'Thank you for contacting us today.', 'Have a great day!'])}")
        
        return "\n".join(transcript_parts)

    @staticmethod
    def get_call(call_id: int) -> dict:
        # Seed both faker and random with call_id for unique but reproducible data
        fake.seed_instance(call_id)
        random.seed(call_id)
        
        agent_id = random.randint(1, 10)
        customer_id = random.randint(1000, 9999)
        start_time = datetime.utcnow() - timedelta(minutes=random.randint(0, 1000))
        
        # Generate realistic conversation
        transcript = FakerDB._generate_conversation(call_id)
        
        # Calculate duration based on transcript length (roughly 2 words per second)
        word_count = len(transcript.split())
        duration = max(60, word_count // 2)  # Minimum 1 minute

        return {
            "call_id": call_id,
            "agent_id": agent_id,
            "customer_id": customer_id,
            "language": "en",
            "start_time": start_time.isoformat(),
            "duration_seconds": duration,
            "transcript": transcript,
        }
    

        