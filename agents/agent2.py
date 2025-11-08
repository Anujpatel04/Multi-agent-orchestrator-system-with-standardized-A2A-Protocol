import google.generativeai as genai
from core.vector_db import VectorDatabase
from core.config import GEMINI_API_KEY
from datetime import datetime
from core.model_helper import get_gemini_model, get_response_text, generate_content_with_retry

class Agent2:
    """Agent for managing User 2's daily routine and schedule"""
    
    def __init__(self):
        # Initialize Gemini with best available model
        self.model = get_gemini_model(GEMINI_API_KEY)
        
        # Initialize vector database (separate from Agent1)
        self.vector_db = VectorDatabase(agent_name="agent2")
        
        # Ensure database has at least one item so the UI shows connected data
        try:
            existing = self.vector_db.get_all()
            if not existing or not existing.get('ids'):
                self.vector_db.add_data(
                    "Daily schedule seed: Focus 11:00-13:00; Break 14:30; Evening gaming 19:00-21:00",
                    {"seed": True, "time": "11:00-21:00", "category": "mixed"}
                )
        except Exception as e:
            # Non-fatal: continue without blocking agent init
            print(f"Agent2 vector DB init warning: {e}")
        
        # System prompt
        self.system_prompt = """You are Agent 2, managing the schedule and routines for User 2.
        You represent User 2 exclusively. All schedules in your database belong to User 2.
        When users provide information about User 2's schedule, store it in the vector database.
        When asked about schedules, you respond with User 2's availability.
        When comparing with other agents, you share User 2's schedule and find common free time with other users.
        You operate independently from Agent 1."""
    
    def store_schedule(self, schedule_data: str, metadata: dict = None):
        """
        Store schedule/routine data in vector database
        
        Args:
            schedule_data: Description of the schedule or routine
            metadata: Optional metadata (e.g., date, time, category)
        """
        if metadata is None:
            metadata = {}
        
        # Add timestamp if not provided
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.now().isoformat()
        
        # Store in vector database
        doc_id = self.vector_db.add_data(schedule_data, metadata)
        
        # Generate a summary using Gemini
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
        """
        Query the schedule database using natural language
        
        Args:
            query: Natural language query about the schedule
            
        Returns:
            Response from the agent with relevant schedule information
        """
        try:
            # Search vector database
            search_results = self.vector_db.search(query, n_results=5)
        except Exception as e:
            print(f"Error searching vector database: {str(e)}")
            search_results = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        
        # Prepare context from search results
        context = ""
        try:
            if search_results.get('documents') and len(search_results['documents']) > 0 and len(search_results['documents'][0]) > 0:
                context = "\n\nRelevant schedule information:\n"
                for i, doc in enumerate(search_results['documents'][0]):
                    metadata = search_results.get('metadatas', [[]])[0][i] if search_results.get('metadatas') and len(search_results['metadatas']) > 0 and i < len(search_results['metadatas'][0]) else {}
                    context += f"- {doc}\n"
                    if metadata:
                        context += f"  Metadata: {metadata}\n"
            else:
                context = "\n\nNo relevant schedule information found in the database."
        except Exception as e:
            print(f"Error processing search results: {str(e)}")
            context = "\n\nNo relevant schedule information found in the database."
        
        # Generate response using Gemini
        prompt = f"""{self.system_prompt}
        
        User query: {query}
        
        {context}
        
        Please provide a helpful response based on the available schedule information.
        If the information is not available, let the user know and suggest they add it."""
        
        try:
            response = generate_content_with_retry(self.model, prompt)
            response_text = get_response_text(response)
            
            if not response_text or response_text.strip() == "":
                response_text = "I couldn't generate a response. Please try again or check your API configuration."
        except Exception as e:
            print(f"Error generating response from Gemini API: {str(e)}")
            # Fallback response
            if context and "Relevant schedule information" in context:
                response_text = f"Based on the available schedule information, I found some relevant data. However, I encountered an error processing your query: {str(e)}"
            else:
                response_text = f"I couldn't find any relevant schedule information for your query: '{query}'. Please add schedule information or try a different query. Error: {str(e)}"
        
        return {
            "query": query,
            "response": response_text,
            "relevant_data": search_results
        }
    
    def get_all_schedules(self):
        """
        Get all stored schedules
        
        Returns:
            All documents from the vector database
        """
        return self.vector_db.get_all()
    
    def delete_schedule(self, doc_id: str):
        """
        Delete a schedule entry
        
        Args:
            doc_id: ID of the document to delete
        """
        self.vector_db.delete(doc_id)
        return {"message": f"Schedule entry {doc_id} deleted successfully"}
    
    def clear_all_schedules(self):
        """
        Delete all schedule entries
        
        Returns:
            Dictionary with count of deleted entries
        """
        deleted_count = self.vector_db.delete_all()
        return {"message": f"All schedules cleared successfully", "deleted_count": deleted_count}
    
    def get_schedules_for_comparison(self):
        """
        Get all schedules in a format suitable for comparison with other agents
        
        Returns:
            Dictionary with all schedule data
        """
        return self.vector_db.get_all()
    
    def query_other_agent_schedule(self, other_agent_schedules: dict):
        """
        Query and compare with another agent's schedule data
        
        Args:
            other_agent_schedules: Dictionary containing schedules from another agent
            
        Returns:
            Comparison result
        """
        my_schedules = self.get_schedules_for_comparison()
        
        return {
            "my_schedules": my_schedules,
            "other_agent_schedules": other_agent_schedules,
            "agent_name": "Agent 2"
        }

