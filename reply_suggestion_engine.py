"""
AI-Powered Reply Suggestion Engine with RAG
Feature 6: Intelligent email reply suggestions using vector database and LLM
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer
import openai
from config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReplyVectorDatabase:
    """Vector database for storing and retrieving email reply templates"""
    
    def __init__(self, db_path: str = "./reply_vector_db"):
        """Initialize ChromaDB with persistent storage"""
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name="email_reply_templates",
                metadata={"description": "Email reply templates and contexts"}
            )
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Vector database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize vector database: {e}")
            raise
    
    def add_training_data(self, templates: List[Dict]):
        """Add training templates to vector database"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for i, template in enumerate(templates):
                # Create searchable text from email pattern and context
                searchable_text = f"{template['email_pattern']} {template.get('context', '')}"
                documents.append(searchable_text)
                
                # Store metadata including reply template
                metadata = {
                    "scenario": template['scenario'],
                    "reply_template": template['reply_template'],
                    "category": template.get('category', 'general'),
                    "urgency": template.get('urgency', 'medium'),
                    "confidence": template.get('confidence', 0.8),
                    "created_at": datetime.now().isoformat()
                }
                metadatas.append(metadata)
                ids.append(f"template_{i}_{template['scenario']}")
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ Added {len(templates)} training templates to vector database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add training data: {e}")
            return False
    
    def search_similar_context(self, email_content: str, n_results: int = 3) -> List[Dict]:
        """Search for similar email contexts"""
        try:
            # Query the collection for similar contexts
            results = self.collection.query(
                query_texts=[email_content],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            similar_contexts = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    context = {
                        'document': doc,
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                    }
                    similar_contexts.append(context)
            
            logger.info(f"✅ Found {len(similar_contexts)} similar contexts for email")
            return similar_contexts
            
        except Exception as e:
            logger.error(f"❌ Failed to search similar contexts: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector database"""
        try:
            count = self.collection.count()
            return {
                "total_templates": count,
                "collection_name": self.collection.name,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get collection stats: {e}")
            return {"total_templates": 0, "status": "error"}

class RAGReplyEngine:
    """RAG-based reply suggestion engine"""
    
    def __init__(self):
        """Initialize RAG engine with vector database and OpenAI"""
        self.vector_db = ReplyVectorDatabase()
        
        # Initialize OpenAI client
        if not OPENAI_API_KEY:
            logger.warning("⚠️ OpenAI API key not found. Reply suggestions will use template-based fallback.")
            self.openai_client = None
        else:
            openai.api_key = OPENAI_API_KEY
            self.openai_client = openai
            logger.info("✅ OpenAI client initialized for RAG")
        
        # User context for personalization
        self.user_context = {
            "name": "Vikas T G",
            "calendar_link": "https://cal.com/vikastg",
            "email": "vikastg2000@gmail.com",
            "phone": "+91-8792283829",
            "current_role": "Full Stack Developer",
            "company": "Available for opportunities"
        }
        
        # Initialize with training data
        self._load_training_data()
    
    def _load_training_data(self):
        """Load initial training data into vector database"""
        training_data = [
            # Job Application Scenarios
            {
                "scenario": "job_interview_invitation",
                "email_pattern": "shortlisted, technical interview, when available, schedule, time slot",
                "reply_template": "Thank you for shortlisting my profile! I'm excited about this opportunity. I'm available for a technical interview and would be happy to schedule it at your convenience. You can book a slot directly here: {calendar_link}\n\nLooking forward to discussing my qualifications further.\n\nBest regards,\n{name}",
                "category": "job_application",
                "urgency": "high",
                "confidence": 0.9,
                "context": "Professional job application response with calendar booking"
            },
            {
                "scenario": "assignment_submission_request",
                "email_pattern": "assignment, deadline, submission, demo video, features, github",
                "reply_template": "Thank you for providing the assignment details! I've carefully reviewed the requirements and am working on implementing all the specified features.\n\nI will ensure to:\n- Complete all required functionalities\n- Provide comprehensive documentation\n- Include a detailed demo video\n- Submit via GitHub repository\n\nI'm committed to delivering high-quality work before the deadline.\n\nBest regards,\n{name}",
                "category": "job_application",
                "urgency": "high",
                "confidence": 0.9,
                "context": "Assignment acknowledgment and commitment response"
            },
            {
                "scenario": "job_rejection_response",
                "email_pattern": "not selected, unfortunately, decided to proceed, another candidate",
                "reply_template": "Thank you for informing me about your decision. While I'm disappointed, I appreciate the opportunity to have been considered for this position.\n\nI enjoyed learning about your team and the role. If any similar opportunities arise in the future, I would be very interested to hear from you.\n\nThank you again for your time and consideration.\n\nBest regards,\n{name}",
                "category": "job_application",
                "urgency": "low",
                "confidence": 0.8,
                "context": "Professional and gracious job rejection response"
            },
            
            # Business & Collaboration
            {
                "scenario": "project_collaboration",
                "email_pattern": "collaboration, project, team, work together, partnership",
                "reply_template": "Thank you for reaching out about this collaboration opportunity! I'm very interested in working together on this project.\n\nI'd love to discuss:\n- Project scope and requirements\n- Timeline and deliverables\n- Technical stack and methodologies\n- Communication and collaboration processes\n\nWould you be available for a brief call to discuss this further? You can schedule a convenient time here: {calendar_link}\n\nLooking forward to our collaboration!\n\nBest regards,\n{name}",
                "category": "collaboration",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Professional collaboration and project discussion"
            },
            {
                "scenario": "business_inquiry_response",
                "email_pattern": "interested in services, pricing, proposal, quotation, business",
                "reply_template": "Thank you for your interest in my services! I'm excited about the possibility of working with you.\n\nI'd be happy to discuss your requirements in detail and provide a customized proposal. Could we schedule a brief call to understand your needs better?\n\nYou can book a convenient time here: {calendar_link}\n\nI look forward to hearing from you!\n\nBest regards,\n{name}",
                "category": "business",
                "urgency": "high",
                "confidence": 0.9,
                "context": "Professional business inquiry response"
            },
            
            # Scheduling & Meetings
            {
                "scenario": "meeting_reschedule_request",
                "email_pattern": "reschedule, postpone, change time, different slot, unavailable",
                "reply_template": "Thank you for letting me know about the schedule change. I completely understand and am flexible with the timing.\n\nI'm available for rescheduling and you can choose a new time slot that works best for you here: {calendar_link}\n\nPlease feel free to pick any convenient time, and I'll adjust my schedule accordingly.\n\nThank you for your understanding!\n\nBest regards,\n{name}",
                "category": "scheduling",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Professional and accommodating rescheduling response"
            },
            {
                "scenario": "meeting_confirmation",
                "email_pattern": "meeting confirmed, see you, looking forward, agenda",
                "reply_template": "Thank you for confirming our meeting! I'm looking forward to our discussion.\n\nI've noted the time in my calendar and will be well-prepared for our conversation. If you have any specific agenda items you'd like me to review beforehand, please let me know.\n\nSee you soon!\n\nBest regards,\n{name}",
                "category": "scheduling",
                "urgency": "low",
                "confidence": 0.7,
                "context": "Meeting confirmation acknowledgment"
            },
            
            # Technical & Development
            {
                "scenario": "technical_question",
                "email_pattern": "technical question, how to, implementation, code, development",
                "reply_template": "Thank you for your technical question! I'd be happy to help you with this.\n\nBased on your description, here are a few approaches you could consider:\n\n1. [I'll provide specific technical guidance based on the question]\n2. [Alternative solutions if applicable]\n\nIf you'd like to discuss this in more detail or need hands-on assistance, feel free to schedule a call: {calendar_link}\n\nHappy coding!\n\nBest regards,\n{name}",
                "category": "technical",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Helpful technical assistance response"
            },
            {
                "scenario": "code_review_request",
                "email_pattern": "code review, pull request, feedback on code, review my",
                "reply_template": "Thank you for asking me to review your code! I'd be happy to take a look and provide feedback.\n\nPlease share the repository link or code files, and I'll review:\n- Code structure and best practices\n- Performance optimizations\n- Potential improvements\n- Documentation suggestions\n\nI'll aim to provide detailed feedback within 24-48 hours.\n\nBest regards,\n{name}",
                "category": "technical",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Code review acceptance response"
            },
            
            # Feedback & Reviews
            {
                "scenario": "feedback_request_response",
                "email_pattern": "feedback, review, comments, suggestions, improvement",
                "reply_template": "Thank you for offering to provide feedback! I greatly value your insights and would appreciate any comments or suggestions you might have.\n\nYour expertise would be invaluable in helping me improve, and I'm open to:\n- Technical feedback and code review\n- Process improvements\n- Best practices recommendations\n- Any other suggestions\n\nIf you'd prefer to discuss this over a call, feel free to schedule a time here: {calendar_link}\n\nThank you for your time and support!\n\nBest regards,\n{name}",
                "category": "feedback",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Grateful and professional feedback request acknowledgment"
            },
            {
                "scenario": "positive_feedback_response",
                "email_pattern": "great job, excellent work, impressed, well done, congratulations",
                "reply_template": "Thank you so much for your kind words! I really appreciate the positive feedback.\n\nIt was a pleasure working on this project, and I'm glad the results met your expectations. Your support and clear communication made the process smooth and enjoyable.\n\nI look forward to future opportunities to collaborate!\n\nBest regards,\n{name}",
                "category": "feedback",
                "urgency": "low",
                "confidence": 0.7,
                "context": "Grateful response to positive feedback"
            },
            
            # General Professional
            {
                "scenario": "introduction_email",
                "email_pattern": "introduction, nice to meet, connect, networking, mutual",
                "reply_template": "Thank you for the introduction! It's great to connect with you.\n\nI'd love to learn more about your work and explore potential areas where we might collaborate. Would you be open to a brief call to get to know each other better?\n\nYou can schedule a convenient time here: {calendar_link}\n\nLooking forward to our conversation!\n\nBest regards,\n{name}",
                "category": "networking",
                "urgency": "medium",
                "confidence": 0.7,
                "context": "Professional networking introduction response"
            },
            {
                "scenario": "thank_you_response",
                "email_pattern": "thank you, thanks, grateful, appreciate",
                "reply_template": "You're very welcome! I'm glad I could help.\n\nIf you need any further assistance or have additional questions, please don't hesitate to reach out. I'm always happy to help.\n\nBest regards,\n{name}",
                "category": "general",
                "urgency": "low",
                "confidence": 0.6,
                "context": "Simple acknowledgment of thanks"
            },
            
            # Event & Educational
            {
                "scenario": "event_invitation",
                "email_pattern": "event, invitation, conference, workshop, seminar, join us",
                "reply_template": "Thank you for the invitation! This event sounds very interesting and relevant to my work.\n\nI would love to attend if my schedule permits. Could you please share more details about:\n- Date and time\n- Location or virtual link\n- Agenda or topics covered\n- Registration process\n\nI look forward to participating!\n\nBest regards,\n{name}",
                "category": "events",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Professional event invitation response"
            },
            {
                "scenario": "training_opportunity",
                "email_pattern": "training, course, workshop, skill development, learning",
                "reply_template": "Thank you for sharing this training opportunity! Continuous learning is very important to me, and this looks like a valuable program.\n\nI'm interested in participating. Could you provide more information about:\n- Course curriculum and duration\n- Schedule and time commitment\n- Prerequisites or requirements\n- Registration process\n\nI appreciate you thinking of me for this opportunity!\n\nBest regards,\n{name}",
                "category": "education",
                "urgency": "medium",
                "confidence": 0.8,
                "context": "Training opportunity interest response"
            },
            
            # Support & Help
            {
                "scenario": "help_request",
                "email_pattern": "help, assistance, support, problem, issue, stuck",
                "reply_template": "I'd be happy to help you with this! Let me take a look at your situation.\n\nTo better assist you, could you provide a bit more detail about:\n- What you're trying to achieve\n- What steps you've already tried\n- Any error messages you're seeing\n- Your current setup or environment\n\nOnce I understand the context better, I can provide more targeted assistance.\n\nBest regards,\n{name}",
                "category": "support",
                "urgency": "high",
                "confidence": 0.9,
                "context": "Helpful support request response"
            }
        ]
        
        # Add training data to vector database
        success = self.vector_db.add_training_data(training_data)
        if success:
            logger.info(f"✅ Loaded {len(training_data)} training templates")
        else:
            logger.error("❌ Failed to load training data")
    
    def suggest_reply(self, email_content: str, sender: str, subject: str = "", context: Dict = None) -> Dict:
        """Generate AI-powered reply suggestion using RAG"""
        try:
            # Combine subject and content for better matching
            full_email_text = f"{subject} {email_content}".strip()
            
            # Search for similar contexts in vector database
            similar_contexts = self.vector_db.search_similar_context(full_email_text, n_results=5)
            
            if not similar_contexts:
                return {
                    "success": False,
                    "error": "No similar contexts found",
                    "suggestion": None
                }
            
            # Get the most relevant template with improved threshold
            best_match = similar_contexts[0]
            
            # Lower the threshold for better diversity and add logging
            logger.info(f"🎯 Best match: {best_match['metadata']['scenario']} (similarity: {best_match['similarity_score']:.3f})")
            
            # Use different thresholds based on similarity score
            if best_match['similarity_score'] > 0.4:  # Lowered from 0.6
                # Use RAG with OpenAI for enhanced suggestions
                if self.openai_client:
                    suggestion = self._generate_rag_reply(full_email_text, sender, subject, similar_contexts)
                else:
                    suggestion = self._generate_template_reply(best_match)
            else:
                # Use template-based suggestion with customization
                suggestion = self._generate_template_reply(best_match)
            
            return {
                "success": True,
                "suggestion": suggestion,
                "confidence": best_match['similarity_score'],
                "scenario": best_match['metadata']['scenario'],
                "method": "RAG" if self.openai_client and best_match['similarity_score'] > 0.4 else "Template",
                "similar_contexts_count": len(similar_contexts)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate reply suggestion: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggestion": None
            }
    
    def _generate_rag_reply(self, email_content: str, sender: str, subject: str, contexts: List[Dict]) -> str:
        """Generate reply using RAG with OpenAI"""
        try:
            # Build context from similar templates
            context_text = "\n".join([
                f"Scenario: {ctx['metadata']['scenario']}\nTemplate: {ctx['metadata']['reply_template']}"
                for ctx in contexts[:2]  # Use top 2 contexts
            ])
            
            # Create RAG prompt
            rag_prompt = f"""
You are an AI assistant helping to write professional email replies. Use the following context and templates to generate an appropriate response.

CONTEXT AND TEMPLATES:
{context_text}

INCOMING EMAIL:
From: {sender}
Subject: {subject}
Content: {email_content}

USER INFORMATION:
Name: {self.user_context['name']}
Email: {self.user_context['email']}
Phone: {self.user_context['phone']}
Calendar Link: {self.user_context['calendar_link']}
Current Role: {self.user_context['current_role']}

INSTRUCTIONS:
1. Generate a professional and contextually appropriate reply
2. Use the user's information when relevant
3. Match the tone of the incoming email
4. Include calendar link when scheduling is mentioned
5. Keep the response concise but warm and professional
6. Do not exceed 150 words

Reply:"""

            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": rag_prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ RAG generation failed: {e}")
            # Fallback to template-based reply
            return self._generate_template_reply(contexts[0])
    
    def _generate_template_reply(self, context: Dict) -> str:
        """Generate reply using template substitution"""
        try:
            template = context['metadata']['reply_template']
            
            # Substitute user context variables
            reply = template.format(
                name=self.user_context['name'],
                calendar_link=self.user_context['calendar_link'],
                email=self.user_context['email'],
                phone=self.user_context['phone'],
                current_role=self.user_context['current_role']
            )
            
            return reply
            
        except Exception as e:
            logger.error(f"❌ Template generation failed: {e}")
            return "Thank you for your email. I'll get back to you soon!\n\nBest regards,\nVikas T G"
    
    def add_user_template(self, scenario: str, email_pattern: str, reply_template: str, category: str = "custom") -> bool:
        """Allow users to add custom reply templates"""
        try:
            custom_template = [{
                "scenario": scenario,
                "email_pattern": email_pattern,
                "reply_template": reply_template,
                "category": category,
                "urgency": "medium",
                "confidence": 0.7,
                "context": f"User-defined template for {scenario}"
            }]
            
            return self.vector_db.add_training_data(custom_template)
            
        except Exception as e:
            logger.error(f"❌ Failed to add user template: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        try:
            db_stats = self.vector_db.get_collection_stats()
            return {
                "vector_database": db_stats,
                "openai_enabled": self.openai_client is not None,
                "user_context": self.user_context,
                "status": "active"
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {"status": "error", "error": str(e)}

# Initialize global RAG engine instance
try:
    rag_engine = RAGReplyEngine()
    logger.info("🚀 RAG Reply Engine initialized and ready!")
except Exception as e:
    logger.error(f"❌ Failed to initialize RAG engine: {e}")
    rag_engine = None

def suggest_email_reply(email_content: str, sender: str, subject: str = "", context: Dict = None) -> Dict:
    """Main function to get reply suggestions"""
    if not rag_engine:
        return {
            "success": False,
            "error": "RAG engine not initialized",
            "suggestion": None
        }
    
    return rag_engine.suggest_reply(email_content, sender, subject, context)

if __name__ == "__main__":
    # Test the RAG engine
    print("🧪 Testing RAG Reply Engine...")
    
    # Test email
    test_email = """
    Hi Vikas,
    
    Thank you for your interest in our Backend Engineering Internship position. 
    We have reviewed your profile and are pleased to inform you that you have been 
    shortlisted for the technical interview round.
    
    When would be a good time for you to attend the technical interview? 
    Please let us know your availability.
    
    Best regards,
    HR Team
    """
    
    result = suggest_email_reply(
        email_content=test_email,
        sender="hr@company.com",
        subject="Technical Interview Schedule"
    )
    
    print(f"\n✅ Suggestion Result:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Method: {result['method']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Scenario: {result['scenario']}")
        print(f"\n📝 Suggested Reply:\n{result['suggestion']}")
    else:
        print(f"Error: {result['error']}")
