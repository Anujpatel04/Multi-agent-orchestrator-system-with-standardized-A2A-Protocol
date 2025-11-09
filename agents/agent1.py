import google.generativeai as genai
from core.vector_db import VectorDatabase
from core.config import GEMINI_API_KEY_AGENT1
from datetime import datetime
from core.model_helper import get_gemini_model, get_response_text, generate_content_with_retry

class Agent1:
    """Agent for managing User 1's daily routine and schedule"""
    
    def __init__(self, api_key=None):
        # Use provided API key or default to AGENT1 key (same as orchestrator)
        api_key = api_key or GEMINI_API_KEY_AGENT1
        # Initialize Gemini with best available model
        self.model = get_gemini_model(api_key)
        
        # Initialize vector database
        self.vector_db = VectorDatabase(agent_name="agent1")
        
        # Ensure database has at least one item so the UI shows connected data
        try:
            existing = self.vector_db.get_all()
            if not existing or not existing.get('ids'):
                self.vector_db.add_data(
                    "Daily schedule seed: Standup 09:30-10:00; Deep work 10:00-12:00; Lunch 12:30-13:00",
                    {"seed": True, "time": "09:30-13:00", "category": "work"}
                )
        except Exception as e:
            # Non-fatal: continue without blocking agent init
            print(f"Agent1 vector DB init warning: {e}")
        
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
    
    def _clean_markdown(self, text: str):
        """Remove markdown formatting from text"""
        if not text:
            return text
        
        # Remove all markdown formatting characters
        text = text.replace('**', '').replace('*', '').replace('__', '').replace('_', '').replace('•', '')
        
        # Remove bullet points and format as sentences
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove leading bullet points, dashes, or asterisks
            line = line.lstrip('•-*').strip()
            
            # Skip empty lines after cleaning
            if not line:
                continue
            
            # If line looks like a list item (starts with colon or is short), combine with previous
            if ':' in line and len(line.split(':')) == 2:
                # Format as "Item: description"
                cleaned_lines.append(line)
            elif cleaned_lines and not cleaned_lines[-1].endswith(('.', ':', '!', '?')):
                # Append to previous line with comma
                cleaned_lines[-1] += ', ' + line
            else:
                cleaned_lines.append(line)
        
        # Join lines with periods
        result = '. '.join(cleaned_lines)
        # Clean up multiple spaces, periods, and commas
        result = result.replace('..', '.').replace('  ', ' ').replace(' ,', ',').replace(',,', ',').strip()
        
        return result
    
    def query_schedule(self, query: str):
        """Query the schedule database using natural language"""
        try:
            search_results = self.vector_db.search(query, n_results=3)
        except Exception as e:
            print(f"Error searching vector database: {str(e)}")
            search_results = {'documents': [[]], 'metadatas': [[]], 'ids': [[]]}
        
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
        
        # Conversational, precise prompt - no markdown formatting
        prompt = f"""You are managing User 1's schedule. Answer this query naturally and precisely.

Query: {query}

{context}

Provide a clear, helpful answer with specific details (times, days, activities) when available. Be conversational and friendly. If information is missing, say so clearly.

IMPORTANT: 
- Do NOT use markdown formatting (no asterisks *, no bold **, no bullet points •)
- Write in plain text only
- Use simple sentences and commas to separate items
- Format: "User 1 is free before 9:30 AM, from 12:00 PM to 12:30 PM, and after 1:00 PM"."""
        
        try:
            # Try with more retries and better delays
            response = generate_content_with_retry(self.model, prompt, max_retries=3, base_delay=1.0)
            response_text = get_response_text(response)
            
            # Clean markdown formatting from response
            response_text = self._clean_markdown(response_text)
            
            if not response_text or response_text.strip() == "":
                response_text = "I couldn't generate a response. Please try again or check your API configuration."
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Error generating response from Gemini API: {str(e)}")
            
            # If we have context from vector DB, generate a useful answer from it
            if context and "Relevant schedule information" in context:
                # Extract schedule data and format it nicely
                schedule_lines = []
                if search_results.get('documents') and len(search_results['documents']) > 0:
                    for i, doc in enumerate(search_results['documents'][0][:3]):  # Use first 3 results
                        schedule_lines.append(f"• {doc}")
                
                if schedule_lines:
                    # Generate a simple, useful answer from the data
                    response_text = f"Based on User 1's schedule:\n\n" + "\n".join(schedule_lines)
                    
                    # Add a note about the query if relevant
                    if "free" in query.lower() or "available" in query.lower():
                        response_text += "\n\nThis shows the scheduled activities. Free time would be between these activities."
                    elif "when" in query.lower() or "time" in query.lower():
                        response_text += "\n\nThese are the scheduled times found in the database."
                else:
                    response_text = f"Based on the available schedule information for User 1, I found relevant data for your query: '{query}'. The schedule data is available, but I'm having trouble processing it right now. Please try again in a moment."
            else:
                # No context found
                if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                    response_text = f"I couldn't find specific schedule information for '{query}' in User 1's schedule. Please try again in a moment or add more schedule data."
                else:
                    response_text = f"I couldn't find any relevant schedule information for your query: '{query}'. Please add schedule information or try a different query."
        
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

