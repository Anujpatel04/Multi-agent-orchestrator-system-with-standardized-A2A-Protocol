import google.generativeai as genai
from core.vector_db import VectorDatabase
from core.config import GEMINI_API_KEY
from datetime import datetime
from core.model_helper import get_gemini_model, get_response_text, generate_content_with_retry

class Agent1:
    """Agent for managing User 1's daily routine and schedule"""
    
    def __init__(self):
        # Initialize Gemini with best available model
        self.model = get_gemini_model(GEMINI_API_KEY)
        
        # Initialize vector database
        self.vector_db = VectorDatabase(agent_name="agent1")
        
        # System prompt
        self.system_prompt = """You are Agent 1, managing the schedule and routines for User 1.
        You represent User 1 exclusively. All schedules in your database belong to User 1.
        When users provide information about User 1's schedule, store it in the vector database.
        When asked about schedules, you respond with User 1's availability.
        When comparing with other agents, you share User 1's schedule and find common free time with other users."""
    
    def store_schedule(self, schedule_data: str, metadata: dict = None):
        """Store schedule/routine data in vector database"""
        if metadata is None:
            metadata = {}
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.now().isoformat()
        
        doc_id = self.vector_db.add_data(schedule_data, metadata)
        
        prompt = f"""Summarize this schedule/routine information and store it:
        
        {schedule_data}
        
        Provide a brief confirmation that the information has been stored."""
        
        response = generate_content_with_retry(self.model, prompt)
        response_text = get_response_text(response)
        
        return {
            "doc_id": doc_id,
            "summary": response_text,
            "message": "Schedule data stored successfully"
        }
    
    def query_schedule(self, query: str):
        """Query the schedule database using natural language"""
        search_results = self.vector_db.search(query, n_results=5)
        
        context = ""
        if search_results['documents'] and len(search_results['documents'][0]) > 0:
            context = "\n\nRelevant schedule information:\n"
            for i, doc in enumerate(search_results['documents'][0]):
                metadata = search_results['metadatas'][0][i] if search_results['metadatas'] and search_results['metadatas'][0] else {}
                context += f"- {doc}\n"
                if metadata:
                    context += f"  Metadata: {metadata}\n"
        else:
            context = "\n\nNo relevant schedule information found in the database."
        prompt = f"""{self.system_prompt}
        
        User query: {query}
        
        {context}
        
        Please provide a helpful response based on the available schedule information.
        If the information is not available, let the user know and suggest they add it."""
        
        response = generate_content_with_retry(self.model, prompt)
        response_text = get_response_text(response)
        
        return {
            "query": query,
            "response": response_text,
            "relevant_data": search_results
        }
    
    def get_all_schedules(self):
        """Get all stored schedules"""
        return self.vector_db.get_all()
    
    def delete_schedule(self, doc_id: str):
        """Delete a schedule entry"""
        self.vector_db.delete(doc_id)
        return {"message": f"Schedule entry {doc_id} deleted successfully"}
    
    def get_schedules_for_comparison(self):
        """Get all schedules in a format suitable for comparison with other agents"""
        return self.vector_db.get_all()
    
    def query_other_agent_schedule(self, other_agent_schedules: dict):
        """Query and compare with another agent's schedule data"""
        my_schedules = self.get_schedules_for_comparison()
        
        return {
            "my_schedules": my_schedules,
            "other_agent_schedules": other_agent_schedules,
            "agent_name": "Agent 1"
        }

