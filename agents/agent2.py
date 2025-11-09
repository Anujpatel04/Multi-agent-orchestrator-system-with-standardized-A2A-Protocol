from core.vector_db import VectorDatabase
from core.config import DEEPSEEK_API_KEY, GEMINI_API_KEY_AGENT2
from datetime import datetime
from core.model_helper import (
    get_deepseek_model, 
    get_deepseek_response_text, 
    generate_content_with_deepseek,
    get_gemini_model,
    get_response_text,
    generate_content_with_retry
)

class Agent2:
    """Agent for managing User 2's daily routine and schedule"""
    
    def __init__(self, api_key=None):
        # Agent 2 uses DeepSeek API (fallback to Gemini if DeepSeek not available)
        self.use_deepseek = False
        
        if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "your_deepseek_api_key_here":
            try:
                # Try to initialize DeepSeek
                self.client = get_deepseek_model(DEEPSEEK_API_KEY)
                self.use_deepseek = True
                print("Agent 2: Using DeepSeek API")
            except Exception as e:
                print(f"Agent 2: DeepSeek initialization failed: {e}, falling back to Gemini")
                self.use_deepseek = False
                # Fallback to Gemini
                api_key = api_key or GEMINI_API_KEY_AGENT2
                self.model = get_gemini_model(api_key)
        else:
            # Use Gemini as fallback
            api_key = api_key or GEMINI_API_KEY_AGENT2
            self.model = get_gemini_model(api_key)
            print("Agent 2: Using Gemini API (DeepSeek key not provided)")
        
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
        
        # Conversational, precise prompt - no markdown formatting
        prompt = f"""You are managing User 2's schedule. Answer this query naturally and precisely.

Query: {query}

{context}

Provide a clear, helpful answer with specific details (times, days, activities) when available. Be conversational and friendly. If information is missing, say so clearly.

IMPORTANT: 
- Do NOT use markdown formatting (no asterisks *, no bold **, no bullet points •)
- Write in plain text only
- Use simple sentences and commas to separate items
- Format: "User 2 is free before 11:00 AM, from 1:00 PM to 2:30 PM, and after 9:00 PM"."""
        
        try:
            # Use DeepSeek or Gemini based on initialization
            if self.use_deepseek:
                response = generate_content_with_deepseek(self.client, prompt, max_retries=3, base_delay=1.0)
                response_text = get_deepseek_response_text(response)
            else:
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
                    response_text = f"Based on User 2's schedule:\n\n" + "\n".join(schedule_lines)
                    
                    # Add a note about the query if relevant
                    if "free" in query.lower() or "available" in query.lower():
                        response_text += "\n\nThis shows the scheduled activities. Free time would be between these activities."
                    elif "when" in query.lower() or "time" in query.lower():
                        response_text += "\n\nThese are the scheduled times found in the database."
                else:
                    response_text = f"Based on the available schedule information for User 2, I found relevant data for your query: '{query}'. The schedule data is available, but I'm having trouble processing it right now. Please try again in a moment."
            else:
                # No context found
                if "rate limit" in error_msg or "quota" in error_msg or "429" in error_msg:
                    response_text = f"I couldn't find specific schedule information for '{query}' in User 2's schedule. Please try again in a moment or add more schedule data."
                else:
                    response_text = f"I couldn't find any relevant schedule information for your query: '{query}'. Please add schedule information or try a different query."
        
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

