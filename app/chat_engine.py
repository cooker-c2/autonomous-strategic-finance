# chat_engine.py
import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from .logic_engine import read_knowledge_base, KnowledgeBaseError
from typing import Dict, Any

class CFOChatbot:
    def __init__(self):
        self.quick_replies = {
            "forecast": ["📊 Download Excel Forecast"],
            "general": ["📅 Generate Forecast", "💼 Financial Advice"]
        }
    
    def get_llm(self):
        """Initialize LLM safely with error handling"""
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.3,
                google_api_key=os.getenv('GOOGLE_API_KEY')
            )
        except Exception as e:
            print(f"Google Gemini initialization failed: {e}")
            return self.create_mock_llm()
    
    def create_mock_llm(self):
        """Create a mock LLM for demo purposes"""
        class MockLLM:
            async def ainvoke(self, input_data):
                user_query = input_data.get("user_query", "").lower()
                
                if "forecast" in user_query or "projection" in user_query:
                    content = "📊 **Financial Forecast Generated!**\n\nBased on your query, I can generate a detailed revenue forecast. Would you like to download the Excel file?"
                elif "revenue" in user_query or "growth" in user_query:
                    content = "💰 **Revenue Analysis**\n\nYour SaaS company shows strong growth potential. I can generate a detailed forecast if you'd like!"
                else:
                    content = "🤖 **AI CFO Assistant Ready!**\n\nI can help you with financial forecasting, revenue projections, and scenario analysis.\n\nWhat would you like to explore today?"
                
                return type('obj', (object,), {'content': content})()
        return MockLLM()
    
    async def generate_response(self, user_message: str) -> Dict[str, Any]:
        """Generate AI-powered responses"""
        try:
            kb_text = read_knowledge_base()
            llm = self.get_llm()
            
            prompt_template = ChatPromptTemplate.from_template(
                """You are an AI CFO assistant. Based on the KNOWLEDGE BASE below, analyze the USER'S QUERY and provide a helpful response.

KNOWLEDGE BASE:
{knowledge_base}

USER'S QUERY: {user_query}

Provide a professional, well-formatted response with clear sections.
"""
            )

            chain = (
                {"knowledge_base": RunnablePassthrough(), "user_query": RunnablePassthrough()}
                | prompt_template
                | llm
            )
            
            ai_response = await chain.ainvoke({
                "knowledge_base": kb_text,
                "user_query": user_message
            })
            
            intent = self.detect_intent(user_message)
            params = self.extract_parameters(user_message)
            
            response_data = {
                "response": ai_response.content,
                "suggestions": self.quick_replies.get(intent, self.quick_replies["general"]),
                "forecast_query": params.get("query"),
                "forecast_months": params.get("months")
            }
            
            return response_data
        
        except KnowledgeBaseError as e:
            return {
                "response": "An error occurred: The knowledge base file is missing.",
                "suggestions": [],
                "error": str(e)
            }
        except Exception as e:
            return {
                "response": "I'm sorry, an error occurred while processing your request. Please try again later.",
                "suggestions": [],
                "error": str(e)
            }
    
    def detect_intent(self, message: str) -> str:
        """Detect user intent"""
        message_lower = message.lower()
        if any(word in message_lower for word in ["forecast", "revenue", "growth", "projection", "predict"]):
            return "forecast"
        return "general"
    
    def extract_parameters(self, message: str) -> Dict[str, Any]:
        """Extract forecast parameters"""
        query_text = message
        months = 12
        
        month_match = re.search(r'(\d+)\s*month', message.lower())
        if month_match:
            months = int(month_match.group(1))
            
        return {"query": query_text, "months": months}

# Global chatbot instance
chatbot = CFOChatbot()