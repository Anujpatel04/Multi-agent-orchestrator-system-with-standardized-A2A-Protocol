
from core.model_helper import (
    get_gemini_model, 
    get_response_text, 
    generate_content_with_retry,
    get_deepseek_model,
    get_deepseek_response_text,
    generate_content_with_deepseek
)
from core.config import DEEPSEEK_API_KEY_ORCHESTRATOR, GEMINI_API_KEY_ORCHESTRATOR, GEMINI_API_KEY_AGENT1
from agents.agent1 import Agent1
from agents.agent2 import Agent2
from datetime import datetime
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class OrchestratorAgent:
    """Master orchestrator agent that coordinates queries across all agents"""
    
    def __init__(self):
        # Orchestrator uses DeepSeek API (fallback to Gemini if DeepSeek not available)
        self.use_deepseek = False
        
        if DEEPSEEK_API_KEY_ORCHESTRATOR and DEEPSEEK_API_KEY_ORCHESTRATOR != "your_deepseek_api_key_here":
            try:
                # Try to initialize DeepSeek
                self.client = get_deepseek_model(DEEPSEEK_API_KEY_ORCHESTRATOR)
                self.use_deepseek = True
                print("Orchestrator: Using DeepSeek API")
            except Exception as e:
                print(f"Orchestrator: DeepSeek initialization failed: {e}, falling back to Gemini")
                self.use_deepseek = False
                # Fallback to Gemini
                self.model = get_gemini_model(GEMINI_API_KEY_ORCHESTRATOR)
        else:
            # Use Gemini as fallback
            self.model = get_gemini_model(GEMINI_API_KEY_ORCHESTRATOR)
            print("Orchestrator: Using Gemini API (DeepSeek key not provided)")
        
        # Initialize all sub-agents with different API keys for parallel processing
        # Agent 1 uses Gemini, Agent 2 uses DeepSeek, Orchestrator uses DeepSeek
        self.agent1 = Agent1(api_key=GEMINI_API_KEY_AGENT1)
        self.agent2 = Agent2()  # Agent2 will use DeepSeek API from config
        
        # Store all available agents
        self.agents = {
            "Agent 1": self.agent1,
            "Agent 2": self.agent2
        }
        
        # Conversation history for context awareness
        self.conversation_history = []
        
        # System prompt for orchestrator
        self.system_prompt = """You are an Orchestrator Agent, a master coordinator that manages multiple specialized agents.
        Your role is to:
        1. Receive user queries
        2. Intelligently route queries to appropriate agents or query all agents
        3. Collect responses from all relevant agents
        4. Synthesize and aggregate the responses into a coherent answer for the user
        
        You have access to multiple agents, each with their own knowledge base:
        - Agent 1: Has its own schedule and routine database
        - Agent 2: Has its own schedule and routine database
        
        Always provide precise, concise responses. Focus on the answer, not explanations."""
    
    def _infer_user_from_context(self, user_query: str, conversation_history: list = None):
        """
        Infer which user is being discussed from conversation history if not explicitly mentioned
        
        Args:
            user_query: Current user query
            conversation_history: List of previous conversation messages
            
        Returns:
            'user1', 'user2', 'both', or None if cannot infer
        """
        query_lower = user_query.lower()
        
        # Check current query first
        user1_keywords = ['user 1', 'user1', 'agent 1', 'agent1', 'first user', 'user one', '1st user', 'user one\'s', 'user1\'s']
        user2_keywords = ['user 2', 'user2', 'agent 2', 'agent2', 'second user', 'user two', '2nd user', 'user two\'s', 'user2\'s']
        all_keywords = ['both', 'all users', 'all agents', 'everyone', 'each user', 'all of them', 'together', 'common', 'compare', 'between', 'shared']
        
        mentions_user1 = any(keyword in query_lower for keyword in user1_keywords)
        mentions_user2 = any(keyword in query_lower for keyword in user2_keywords)
        mentions_all = any(keyword in query_lower for keyword in all_keywords)
        
        # If explicitly mentioned in current query, return immediately
        if mentions_all or (mentions_user1 and mentions_user2):
            return 'both'
        if mentions_user1:
            return 'user1'
        if mentions_user2:
            return 'user2'
        
        # If no explicit mention, check conversation history
        if conversation_history:
            # Look through recent history (last 5 messages) for user mentions
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            
            for msg in reversed(recent_history):  # Check most recent first
                # Handle different message formats (frontend uses 'content', backend might use 'message' or 'query')
                msg_text = str(msg.get('content', '') or msg.get('message', '') or msg.get('query', '') or msg if isinstance(msg, str) else '').lower()
                if not msg_text:
                    continue
                
                # Check if this message mentioned a user
                hist_mentions_user1 = any(keyword in msg_text for keyword in user1_keywords)
                hist_mentions_user2 = any(keyword in msg_text for keyword in user2_keywords)
                hist_mentions_all = any(keyword in msg_text for keyword in all_keywords)
                
                if hist_mentions_all or (hist_mentions_user1 and hist_mentions_user2):
                    return 'both'
                if hist_mentions_user1:
                    return 'user1'
                if hist_mentions_user2:
                    return 'user2'
        
        # Check stored conversation history if provided
        if self.conversation_history:
            for msg in reversed(self.conversation_history[-5:]):
                msg_text = str(msg).lower()
                hist_mentions_user1 = any(keyword in msg_text for keyword in user1_keywords)
                hist_mentions_user2 = any(keyword in msg_text for keyword in user2_keywords)
                hist_mentions_all = any(keyword in msg_text for keyword in all_keywords)
                
                if hist_mentions_all or (hist_mentions_user1 and hist_mentions_user2):
                    return 'both'
                if hist_mentions_user1:
                    return 'user1'
                if hist_mentions_user2:
                    return 'user2'
        
        return None
    
    def _is_schedule_related_query(self, user_query: str):
        """
        Determine if the query is schedule-related or a general question
        
        Args:
            user_query: The user's query
            
        Returns:
            True if schedule-related, False if general question
        """
        query_lower = user_query.lower()
        
        # Schedule-related keywords
        schedule_keywords = [
            'schedule', 'availability', 'free time', 'busy', 'meeting', 'appointment',
            'when', 'what time', 'calendar', 'routine', 'plan', 'commitment',
            'free', 'available', 'occupied', 'booked', 'slot', 'time slot',
            'compare', 'common', 'overlap', 'conflict', 'both users', 'all users',
            'user 1', 'user 2', 'user1', 'user2', 'agent 1', 'agent 2'
        ]
        
        # Check if query contains schedule-related keywords
        is_schedule = any(keyword in query_lower for keyword in schedule_keywords)
        
        # Also check if it's asking about specific users (likely schedule-related)
        query_words = query_lower.split()
        user_mentions = any(word in ['user', 'agent'] for word in query_words)
        
        return is_schedule or user_mentions
    
    def _determine_relevant_agents(self, user_query: str, conversation_history: list = None):
        """
        Intelligently determine which agents should be queried based on the user's query
        Uses conversation history to infer user context if not explicitly mentioned
        
        Args:
            user_query: The user's query
            conversation_history: Optional conversation history for context
            
        Returns:
            Dictionary of relevant agents to query
        """
        # First, infer user from context (including conversation history)
        inferred_user = self._infer_user_from_context(user_query, conversation_history)
        
        # First, do a quick keyword check for common patterns
        query_lower = user_query.lower()
        
        # Expanded keyword matching for faster routing (skip LLM when possible)
        user1_keywords = ['user 1', 'user1', 'agent 1', 'agent1', 'first user', 'user one', '1st user', 'user one\'s', 'user1\'s']
        user2_keywords = ['user 2', 'user2', 'agent 2', 'agent2', 'second user', 'user two', '2nd user', 'user two\'s', 'user2\'s']
        all_keywords = ['both', 'all users', 'all agents', 'everyone', 'each user', 'all of them', 'together', 'common', 'compare', 'between', 'shared']
        
        mentions_user1 = any(keyword in query_lower for keyword in user1_keywords)
        mentions_user2 = any(keyword in query_lower for keyword in user2_keywords)
        mentions_all = any(keyword in query_lower for keyword in all_keywords)
        
        # Use inferred user if current query doesn't explicitly mention a user
        if not mentions_user1 and not mentions_user2 and not mentions_all:
            if inferred_user == 'user1':
                return {'Agent 1': self.agent1}
            elif inferred_user == 'user2':
                return {'Agent 2': self.agent2}
            elif inferred_user == 'both':
                return self.agents
        
        # Fast routing based on keywords - skip LLM call when possible
        if mentions_user1 and not mentions_user2 and not mentions_all:
            return {'Agent 1': self.agent1}
        elif mentions_user2 and not mentions_user1 and not mentions_all:
            return {'Agent 2': self.agent2}
        elif mentions_all or (mentions_user1 and mentions_user2):
            return self.agents
        
        # Only use LLM if keywords are unclear - with shorter, faster prompt
        routing_prompt = f"""Query: "{user_query[:100]}"

Route to: agent1 (User 1 only), agent2 (User 2 only), or all (both/multiple).

One word only: agent1/agent2/all"""

        try:
            # Use DeepSeek or Gemini based on initialization
            if self.use_deepseek:
                routing_response = generate_content_with_deepseek(self.client, routing_prompt, max_retries=1, base_delay=0.5)
                routing_decision = get_deepseek_response_text(routing_response).strip().lower().replace('"', '').replace("'", '')
            else:
                routing_response = generate_content_with_retry(self.model, routing_prompt, max_retries=1, base_delay=0.5)
                routing_decision = get_response_text(routing_response).strip().lower().replace('"', '').replace("'", '')
            
            agents_to_query = {}
            if 'agent1' in routing_decision or ('1' in routing_decision and '2' not in routing_decision):
                agents_to_query['Agent 1'] = self.agent1
            if 'agent2' in routing_decision or ('2' in routing_decision and '1' not in routing_decision):
                agents_to_query['Agent 2'] = self.agent2
            if 'all' in routing_decision or (len(agents_to_query) == 0):
                agents_to_query = self.agents
            
            return agents_to_query if agents_to_query else self.agents
            
        except Exception as e:
            # Fast fallback - default to all
            return self.agents
    
    def _answer_general_question(self, user_query: str):
        """
        Answer general (non-schedule) questions directly using LLM without agent coordination
        
        Args:
            user_query: The user's general question
            
        Returns:
            Direct LLM response
        """
        prompt = f"""You are a helpful AI assistant. Answer the following question naturally and conversationally.

Question: {user_query}

Provide a clear, helpful answer. Be concise (2-3 sentences maximum) and conversational. Do not use markdown formatting."""
        
        try:
            if self.use_deepseek:
                response = generate_content_with_deepseek(self.client, prompt, max_retries=2, base_delay=0.5)
                answer = get_deepseek_response_text(response).strip()
            else:
                response = generate_content_with_retry(self.model, prompt, max_retries=2, base_delay=0.5)
                answer = get_response_text(response).strip()
            
            # Clean markdown
            answer = answer.replace('**', '').replace('*', '').replace('__', '').replace('_', '').replace('•', '')
            return answer
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def query_all_agents(self, user_query: str, conversation_history: list = None):
        """
        Intelligently query relevant agents based on the user's query
        Only queries agents that are relevant to the query
        Answers general questions directly without agent coordination
        
        Args:
            user_query: The user's query
            conversation_history: Optional conversation history for context
            
        Returns:
            Aggregated response from relevant agents or direct LLM response for general questions
        """
        # Store in conversation history
        if conversation_history:
            self.conversation_history = conversation_history[-10:]  # Keep last 10 messages
        
        # Check if this is a general question (not schedule-related)
        if not self._is_schedule_related_query(user_query):
            print(f"\n{'='*70}")
            print("💬 ORCHESTRATOR AGENT - GENERAL QUESTION")
            print(f"{'='*70}")
            print(f"📥 [USER → ORCHESTRATOR]")
            print(f"   Query: {user_query}\n")
            print("🤖 [ORCHESTRATOR] Detected general question - answering directly without agent coordination\n")
            
            direct_response = self._answer_general_question(user_query)
            
            print(f"📤 [ORCHESTRATOR → USER]")
            print(f"   Status: ✓ Ready")
            print(f"   Direct response provided")
            print(f"{'='*70}\n")
            
            return {
                "user_query": user_query,
                "agent_responses": {},
                "aggregated_response": direct_response,
                "timestamp": datetime.now().isoformat(),
                "query_type": "general"
            }
        
        print(f"\n{'='*70}")
        print("🔀 ORCHESTRATOR AGENT - INTELLIGENT ROUTING")
        print(f"{'='*70}")
        print(f"📥 [USER → ORCHESTRATOR]")
        print(f"   Query: {user_query}\n")
        
        # Determine which agents are relevant (with context awareness)
        agents_to_query = self._determine_relevant_agents(user_query, conversation_history)
        
        if len(agents_to_query) == len(self.agents):
            print("📡 [ORCHESTRATOR → AGENTS] Routing query to all agents...\n")
        else:
            agent_names = ', '.join(agents_to_query.keys())
            print(f"📡 [ORCHESTRATOR → AGENTS] Routing query to: {agent_names}\n")
        
        print("-" * 70)
        
        # Collect responses from relevant agents in PARALLEL for faster communication
        agent_responses = {}
        
        def query_agent_parallel(agent_name, agent):
            """Query a single agent and return the response"""
            try:
                print(f"📤 [ORCHESTRATOR → {agent_name}]")
                print(f"   Sending query: \"{user_query}\"")
                print(f"   Status: Processing in parallel...")
                sys.stdout.flush()
                
                # Call agent with timeout handling
                try:
                    response = agent.query_schedule(user_query)
                except Exception as agent_error:
                    raise Exception(f"Agent query failed: {str(agent_error)}")
                
                # Validate response structure
                if not response or 'response' not in response:
                    raise Exception(f"Invalid response format from {agent_name}")
                
                print(f"📥 [{agent_name} → ORCHESTRATOR]")
                print(f"   Status: ✓ Success")
                print(f"   Response length: {len(response['response'])} characters")
                if response.get('relevant_data', {}).get('documents') and response['relevant_data']['documents'][0]:
                    print(f"   Found {len(response['relevant_data']['documents'][0])} relevant results")
                sys.stdout.flush()
                
                result = {
                    "agent_name": agent_name,
                    "response": response['response'],
                    "relevant_data": response.get('relevant_data', {}),
                    "status": "success"
                }
                
                print(f"   Preview: {response['response'][:100]}...")
                print("-" * 70 + "\n")
                sys.stdout.flush()
                
                return result
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"📥 [{agent_name} → ORCHESTRATOR]")
                print(f"   Status: ✗ Error")
                print(f"   Error: {str(e)}")
                print("-" * 70 + "\n")
                sys.stdout.flush()
                
                return {
                    "agent_name": agent_name,
                    "response": f"Error: {str(e)}",
                    "relevant_data": None,
                    "status": "error",
                    "error": str(e)
                }
        
        # Query all agents in parallel using ThreadPoolExecutor
        print("⚡ [ORCHESTRATOR] Querying agents in parallel for faster response...\n")
        with ThreadPoolExecutor(max_workers=len(agents_to_query)) as executor:
            # Submit all agent queries simultaneously
            future_to_agent = {
                executor.submit(query_agent_parallel, agent_name, agent): agent_name
                for agent_name, agent in agents_to_query.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    agent_responses[result["agent_name"]] = {
                        "response": result["response"],
                        "relevant_data": result.get("relevant_data", {}),
                        "status": result["status"]
                    }
                    if result.get("error"):
                        agent_responses[result["agent_name"]]["error"] = result["error"]
                except Exception as e:
                    agent_responses[agent_name] = {
                        "response": f"Error: {str(e)}",
                        "relevant_data": None,
                        "status": "error",
                        "error": str(e)
                    }
        
        if agent_responses:
            print("🔄 [ORCHESTRATOR] Aggregating responses from queried agents...")
            
            # Aggregate responses using Gemini
            aggregated_response = self._aggregate_responses(user_query, agent_responses)
            
            print(f"📤 [ORCHESTRATOR → USER]")
            print(f"   Status: ✓ Ready")
            print(f"   Aggregated response prepared")
            print(f"{'='*70}\n")
        else:
            aggregated_response = "No relevant agents were queried. Please try rephrasing your query."
            print(f"⚠️  [ORCHESTRATOR] No agents queried")
            print(f"{'='*70}\n")
        
        return {
            "user_query": user_query,
            "agent_responses": agent_responses,
            "aggregated_response": aggregated_response,
            "timestamp": datetime.now().isoformat()
        }
    
    def _aggregate_responses(self, user_query: str, agent_responses: dict):
        """
        Aggregate responses from all agents into a coherent, precise answer
        Compares schedules internally to provide unified answers
        
        Args:
            user_query: Original user query
            agent_responses: Dictionary of responses from each agent
            
        Returns:
            Aggregated response string
        """
        # Extract both responses and raw schedule data
        clean_responses = {}
        schedule_data = {}
        
        for agent_name, response_data in agent_responses.items():
            if response_data['status'] == 'success':
                resp = response_data.get('response', '')
                # Skip responses that contain error messages
                if resp and 'error' not in resp.lower() and 'rate limit' not in resp.lower():
                    clean_responses[agent_name] = resp
                    
                    # Extract raw schedule data from relevant_data
                    relevant_data = response_data.get('relevant_data', {})
                    if relevant_data and relevant_data.get('documents'):
                        docs = relevant_data['documents'][0] if len(relevant_data['documents']) > 0 else []
                        if docs:
                            schedule_data[agent_name] = docs
        
        # If no clean responses, return helpful message
        if not clean_responses:
            return "I couldn't retrieve schedule information at this time. Please try again in a moment."
        
        # If only one agent responded, return their response directly
        if len(clean_responses) == 1:
            return list(clean_responses.values())[0]
        
        # Prepare detailed context with both responses and raw schedule data
        context_parts = []
        schedule_info_parts = []
        
        user1_schedules = []
        user2_schedules = []
        
        for agent_name, resp in clean_responses.items():
            user_name = "User 1" if "Agent 1" in agent_name or "1" in agent_name else "User 2"
            context_parts.append(f"{user_name} Response:\n{resp}")
            
            # Extract and organize schedule data
            if agent_name in schedule_data:
                schedules = schedule_data[agent_name]
                schedule_list = []
                for doc in schedules[:5]:  # Use first 5 results
                    schedule_list.append(f"- {doc}")
                
                if schedule_list:
                    schedule_info_parts.append(f"{user_name} Schedule Data:\n" + "\n".join(schedule_list))
                    # Store for comparison
                    if "1" in agent_name or "Agent 1" in agent_name:
                        user1_schedules = schedules
                    else:
                        user2_schedules = schedules
        
        context = "\n\n---\n\n".join(context_parts)
        schedule_info = "\n\n---\n\n".join(schedule_info_parts) if schedule_info_parts else ""
        
        # Enhanced prompt that specifically asks for comparison and merging
        query_lower = user_query.lower()
        is_comparison_query = any(word in query_lower for word in [
            'common', 'both', 'all', 'together', 'everyone', 'compare', 
            'free time', 'available', 'meeting', 'when', 'schedule'
        ])
        
        if is_comparison_query and len(schedule_data) >= 2:
            # Concise comparison prompt - only summary
            prompt = f"""You are an Orchestrator Agent that COMPARES schedules from multiple users.

User's Question: "{user_query}"

Individual Agent Responses:
{context}

Raw Schedule Data from Database:
{schedule_info}

CRITICAL: Provide ONLY a concise summary answer. NO detailed breakdowns, NO bullet points, NO sections.

Instructions:
1. Compare both users' schedules
2. Find common free times (when both users are free)
3. Provide ONLY a brief summary (2-3 sentences maximum)

Format: Write a simple, conversational answer stating when both users are free together. If no common time, say so briefly.

Example: "Based on comparing both schedules, you both have free time on Sunday from 1:00 PM to 2:30 PM, and after 9:00 PM."

Provide ONLY the summary answer (no bullet points, no sections, no detailed breakdowns):"""
        else:
            # Standard aggregation for non-comparison queries - concise summary only
            prompt = f"""You are an Orchestrator Agent coordinating between multiple users' schedules.

User's Question: "{user_query}"

Responses from agents:
{context}

{schedule_info if schedule_info else ""}

Your task: Provide ONLY a concise summary answer (2-3 sentences maximum).

Guidelines:
- Be conversational and natural
- Provide specific information (times, days, activities) when available
- Keep it brief - just the essential answer
- NO bullet points, NO sections, NO detailed breakdowns
- Just a simple, direct answer to the question

Provide your concise response:"""

        try:
            # Use more retries for aggregation to ensure we get a response
            # Use DeepSeek or Gemini based on initialization
            if self.use_deepseek:
                response = generate_content_with_deepseek(self.client, prompt, max_retries=3, base_delay=1.0)
                aggregated_text = get_deepseek_response_text(response).strip()
            else:
                response = generate_content_with_retry(self.model, prompt, max_retries=3, base_delay=1.0)
                aggregated_text = get_response_text(response).strip()
            
            # Post-process to clean up response - remove ALL markdown formatting
            aggregated_text = aggregated_text.replace('**', '').replace('*', '').replace('__', '').replace('_', '').replace('•', '')
            
            if is_comparison_query:
                # If response has too much detail (multiple lines, sections), extract just the summary
                if aggregated_text.count('\n') > 5:
                    # Try to extract just the summary part
                    lines = aggregated_text.split('\n')
                    summary_lines = []
                    in_summary = False
                    
                    for line in lines:
                        line_lower = line.lower()
                        # Look for summary section
                        if 'summary' in line_lower or 'best' in line_lower or 'common free time' in line_lower:
                            in_summary = True
                            # Extract the actual summary text (skip headers)
                            if ':' in line and len(line.split(':')) > 1:
                                summary_lines.append(line.split(':', 1)[1].strip())
                            continue
                        
                        # If we're in summary and hit another section, stop
                        if in_summary and (line.strip().startswith('**') or line.strip().startswith('•') or 
                                          'conflict' in line_lower or 'schedule' in line_lower and ':' in line):
                            break
                        
                        if in_summary and line.strip():
                            summary_lines.append(line.strip())
                    
                    if summary_lines:
                        aggregated_text = ' '.join(summary_lines)
                    else:
                        # Fallback: use computation-based summary
                        aggregated_text = self._create_comparison_fallback(
                            user_query, clean_responses, schedule_data
                        )
                elif not any(word in aggregated_text.lower() for word in ['free time', 'common', 'available', 'overlap', 'conflict']):
                    # Response doesn't seem to compare - use our computation
                    aggregated_text = self._create_comparison_fallback(
                        user_query, clean_responses, schedule_data
                    )
            
            return aggregated_text
        except Exception as e:
            # Fallback: create comparison manually
            if is_comparison_query and len(schedule_data) >= 2:
                return self._create_comparison_fallback(user_query, clean_responses, schedule_data)
            
            # Standard fallback
            if len(clean_responses) == 1:
                return list(clean_responses.values())[0]
            
            responses_list = list(clean_responses.values())
            if len(responses_list) == 2:
                return f"{responses_list[0]}\n\n{responses_list[1]}"
            return "\n\n".join(responses_list)
    
    def _parse_schedule_times(self, schedule_text: str):
        """Parse schedule text to extract time ranges"""
        import re
        time_ranges = []
        
        # Pattern to match time ranges like "09:30-10:00" or "11:00-13:00"
        time_pattern = r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})'
        matches = re.findall(time_pattern, schedule_text)
        
        for match in matches:
            start_hour, start_min = int(match[0]), int(match[1])
            end_hour, end_min = int(match[2]), int(match[3])
            
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            time_ranges.append((start_minutes, end_minutes))
        
        # Also look for single times like "Break 14:30" - treat as 30 min block
        single_time_pattern = r'(\d{1,2}):(\d{2})(?!\s*-\s*\d)'
        single_matches = re.findall(single_time_pattern, schedule_text)
        
        for match in single_matches:
            hour, minute = int(match[0]), int(match[1])
            start_minutes = hour * 60 + minute
            end_minutes = start_minutes + 30  # Default 30 min for single times
            time_ranges.append((start_minutes, end_minutes))
        
        return sorted(time_ranges)
    
    def _merge_time_ranges(self, time_ranges):
        """Merge overlapping time ranges"""
        if not time_ranges:
            return []
        
        sorted_ranges = sorted(time_ranges)
        merged = [sorted_ranges[0]]
        
        for current_start, current_end in sorted_ranges[1:]:
            last_start, last_end = merged[-1]
            
            # If current range overlaps or is adjacent to last range, merge them
            if current_start <= last_end:
                merged[-1] = (last_start, max(last_end, current_end))
            else:
                merged.append((current_start, current_end))
        
        return merged
    
    def _find_common_free_time(self, user1_times, user2_times):
        """Find common free time between two users' schedules"""
        # Merge overlapping intervals for each user
        user1_merged = self._merge_time_ranges(user1_times)
        user2_merged = self._merge_time_ranges(user2_times)
        
        # Combine all busy times
        all_busy = sorted(user1_merged + user2_merged)
        
        # Merge overlapping intervals across both users
        merged = self._merge_time_ranges(all_busy)
        
        # Find free time gaps (assuming day is 0-1440 minutes = 24 hours)
        free_times = []
        day_start = 0  # 00:00
        day_end = 1440  # 24:00
        
        if not merged:
            return [(day_start, day_end)]
        
        # Check before first busy period
        if merged[0][0] > day_start:
            free_times.append((day_start, merged[0][0]))
        
        # Check between busy periods
        for i in range(len(merged) - 1):
            gap_start = merged[i][1]
            gap_end = merged[i + 1][0]
            if gap_end > gap_start:
                free_times.append((gap_start, gap_end))
        
        # Check after last busy period
        if merged[-1][1] < day_end:
            free_times.append((merged[-1][1], day_end))
        
        return free_times
    
    def _format_time(self, minutes):
        """Convert minutes since midnight to HH:MM format"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _create_comparison_fallback(self, user_query: str, clean_responses: dict, schedule_data: dict):
        """Create a comparison answer by actually computing overlaps and free times"""
        user1_resp = clean_responses.get("Agent 1", "")
        user2_resp = clean_responses.get("Agent 2", "")
        user1_sched = schedule_data.get("Agent 1", [])
        user2_sched = schedule_data.get("Agent 2", [])
        
        # Parse schedule times from raw schedule data
        user1_times = []
        user2_times = []
        
        for sched in user1_sched:
            user1_times.extend(self._parse_schedule_times(sched))
        
        for sched in user2_sched:
            user2_times.extend(self._parse_schedule_times(sched))
        
        # Merge time ranges to remove duplicates and overlaps
        user1_merged = self._merge_time_ranges(user1_times)
        user2_merged = self._merge_time_ranges(user2_times)
        
        # Build comparison answer
        query_lower = user_query.lower()
        answer = ""
        
        if "common" in query_lower or "free" in query_lower or "available" in query_lower:
            # Find common free time
            common_free = self._find_common_free_time(user1_times, user2_times)
            
            if common_free:
                # Create concise summary only - no detailed breakdown
                free_filtered = [(s, e) for s, e in common_free if e - s >= 30]
                if free_filtered:
                    free_times_str = []
                    for start, end in free_filtered[:3]:  # Limit to top 3
                        free_times_str.append(f"{self._format_time(start)} - {self._format_time(end)}")
                    
                    answer = f"Based on comparing both schedules, you both have free time at {', '.join(free_times_str)}."
                else:
                    answer = "After comparing both schedules, there is no significant common free time available (all gaps are less than 30 minutes)."
            else:
                answer = "After comparing both schedules, there is no common free time available. Both users have overlapping or consecutive busy periods throughout the day."
        else:
            # General comparison - concise summary only
            common_free = self._find_common_free_time(user1_times, user2_times)
            
            if common_free:
                free_filtered = [(s, e) for s, e in common_free if e - s >= 30]
                if free_filtered:
                    free_times_str = []
                    for start, end in free_filtered[:3]:  # Limit to top 3
                        free_times_str.append(f"{self._format_time(start)} - {self._format_time(end)}")
                    answer = f"Based on comparing both schedules, common free time is available at {', '.join(free_times_str)}."
                else:
                    answer = "After comparing both schedules, there is no significant common free time available (all gaps are less than 30 minutes)."
            else:
                answer = "After comparing both schedules, there is no common free time available. Both users have overlapping busy periods."
        
        return answer if answer else "I couldn't extract schedule times for comparison. Please ensure schedules include time information."
    
    def smart_query(self, user_query: str, conversation_history: list = None):
        """
        Intelligently route query to relevant agents or query all
        This method now uses the same intelligent routing as query_all_agents
        
        Args:
            user_query: The user's query
            conversation_history: Optional conversation history for context
            
        Returns:
            Response from relevant agents
        """
        # Use the same intelligent routing logic
        return self.query_all_agents(user_query, conversation_history)
    
    def get_all_agent_data_summary(self):
        """
        Get a summary of data stored in all agents
        
        Returns:
            Dictionary with summary from each agent
        """
        summary = {}
        
        for agent_name, agent in self.agents.items():
            try:
                all_data = agent.get_all_schedules()
                summary[agent_name] = {
                    "total_schedules": len(all_data['ids']),
                    "schedules": all_data['documents'][:5] if all_data['documents'] else []  # First 5
                }
            except Exception as e:
                summary[agent_name] = {
                    "error": str(e),
                    "total_schedules": 0
                }
        
        return summary
    
    def find_common_free_time(self, user_query: str):
        """
        Enable agents to communicate with each other to find common free time
        
        Args:
            user_query: User's query about finding common time
            
        Returns:
            Result with common free time analysis
        """
        print(f"\n{'='*70}")
        print("🤝 ORCHESTRATOR - ENABLING AGENT-TO-AGENT COMMUNICATION")
        print(f"{'='*70}")
        print(f"📥 [USER → ORCHESTRATOR]")
        print(f"   Query: {user_query}\n")
        
        print("🔄 [ORCHESTRATOR] Initiating agent-to-agent communication...\n")
        
        # Step 1: Get schedules from all agents
        print("📡 [ORCHESTRATOR → AGENTS] Requesting schedules from all agents...\n")
        all_agent_schedules = {}
        
        for agent_name, agent in self.agents.items():
            try:
                print(f"  📤 [ORCHESTRATOR → {agent_name}]")
                print(f"     Request: Get all schedules for comparison")
                schedules = agent.get_schedules_for_comparison()
                all_agent_schedules[agent_name] = schedules
                print(f"  📥 [{agent_name} → ORCHESTRATOR]")
                print(f"     Status: ✓ Success")
                print(f"     Schedules found: {len(schedules['ids'])}")
                print("-" * 70 + "\n")
            except Exception as e:
                print(f"  📥 [{agent_name} → ORCHESTRATOR]")
                print(f"     Status: ✗ Error - {str(e)}")
                print("-" * 70 + "\n")
                all_agent_schedules[agent_name] = {"ids": [], "documents": [], "metadatas": []}
        
        # Step 2: Enable agents to query each other
        print("🤝 [AGENTS] Agents communicating with each other...\n")
        
        agent_comparisons = {}
        agent_list = list(self.agents.items())
        
        for i, (agent1_name, agent1) in enumerate(agent_list):
            for j, (agent2_name, agent2) in enumerate(agent_list):
                if i != j:  # Don't compare agent with itself
                    try:
                        print(f"📤 [{agent1_name} → {agent2_name}]")
                        print(f"   Request: Share your schedules for comparison")
                        
                        # Agent 1 queries Agent 2's schedules
                        comparison = agent1.query_other_agent_schedule(all_agent_schedules[agent2_name])
                        agent_comparisons[f"{agent1_name}_to_{agent2_name}"] = comparison
                        
                        print(f"📥 [{agent2_name} → {agent1_name}]")
                        print(f"   Response: Shared {len(all_agent_schedules[agent2_name]['ids'])} schedules")
                        print("-" * 70 + "\n")
                    except Exception as e:
                        print(f"📥 [{agent2_name} → {agent1_name}]")
                        print(f"   Error: {str(e)}")
                        print("-" * 70 + "\n")
        
        # Step 3: Each agent analyzes for common free time
        print("🔍 [AGENTS] Analyzing schedules for common free time...\n")
        
        agent_analyses = {}
        
        for agent_name, agent in self.agents.items():
            try:
                print(f"🧠 [{agent_name}] Analyzing all schedules...")
                
                # Prepare context with all schedules, clearly labeled by user
                user_assignment = {
                    "Agent 1": "User 1",
                    "Agent 2": "User 2"
                }
                
                all_schedules_context = ""
                for agent_name_schedule, schedules in all_agent_schedules.items():
                    user_name = user_assignment.get(agent_name_schedule, "Unknown User")
                    all_schedules_context += f"\n[{agent_name_schedule} - {user_name}'s Schedule]:\n"
                    if schedules['documents']:
                        for idx, doc in enumerate(schedules['documents']):
                            metadata = schedules['metadatas'][idx] if schedules['metadatas'] else {}
                            all_schedules_context += f"- {doc}\n"
                            if metadata:
                                all_schedules_context += f"  Metadata: {metadata}\n"
                    else:
                        all_schedules_context += f"  {user_name} has no scheduled commitments\n"
                
                # Query agent to analyze common free time
                # Each agent represents a different user
                user_assignment = {
                    "Agent 1": "User 1",
                    "Agent 2": "User 2"
                }
                
                analysis_prompt = f"""You are {agent_name}, managing schedules for {user_assignment.get(agent_name, 'your user')}.

User Query: {user_query}

IMPORTANT: Each agent represents a DIFFERENT user:
- Agent 1 manages User 1's schedule
- Agent 2 manages User 2's schedule

All User Schedules (from all agents):
{all_schedules_context}

Your task:
1. Identify which schedules belong to which user (based on which agent provided them)
2. Extract busy times for each user separately
3. Find time slots when ALL users are free simultaneously
4. Provide SPECIFIC time recommendations when all users are available

Consider:
- Agent 1's schedules = User 1's commitments
- Agent 2's schedules = User 2's commitments
- Find overlapping FREE periods (not busy periods)
- Give specific time recommendations (e.g., "Both users are free from 2 PM to 3 PM")

Respond with a clear answer showing when ALL users are free together."""
                
                # Use DeepSeek or Gemini based on initialization
                if self.use_deepseek:
                    response = generate_content_with_deepseek(self.client, analysis_prompt, max_retries=2, base_delay=0.5)
                    analysis_text = get_deepseek_response_text(response)
                else:
                    response = generate_content_with_retry(self.model, analysis_prompt)
                    analysis_text = get_response_text(response)
                
                agent_analyses[agent_name] = {
                    "analysis": analysis_text,
                    "status": "success"
                }
                
                print(f"✓ [{agent_name}] Analysis complete")
                print(f"  Preview: {analysis_text[:150]}...")
                print("-" * 70 + "\n")
                
            except Exception as e:
                agent_analyses[agent_name] = {
                    "analysis": f"Error: {str(e)}",
                    "status": "error",
                    "error": str(e)
                }
                print(f"✗ [{agent_name}] Analysis failed: {str(e)}")
                print("-" * 70 + "\n")
        
        # Step 4: Aggregate final response
        print("🔄 [ORCHESTRATOR] Aggregating agent-to-agent communication results...\n")
        
        # Create final aggregated response
        aggregation_prompt = f"""You are the Orchestrator Agent. The agents have communicated with each other.

User Query: {user_query}

IMPORTANT CONTEXT:
- Agent 1 manages User 1's schedule
- Agent 2 manages User 2's schedule
- Each agent represents a DIFFERENT user

Agent Analyses:
"""
        
        for agent_name, analysis in agent_analyses.items():
            aggregation_prompt += f"\n[{agent_name} - Represents {('User 1' if '1' in agent_name else 'User 2')}]:\n{analysis['analysis']}\n"
        
        aggregation_prompt += """

Provide ONLY a PRECISE, CONCISE answer. No explanations, no theory, just the answer.

Format your response as:
"Common free time: [specific times when all users are free]"

If no common time exists, respond: "No common free time available"

Keep it brief - maximum 2-3 sentences. Just the answer."""
        
        try:
            # Use DeepSeek or Gemini based on initialization
            if self.use_deepseek:
                final_response = generate_content_with_deepseek(self.client, aggregation_prompt, max_retries=3, base_delay=1.0)
                aggregated_response = get_deepseek_response_text(final_response)
            else:
                final_response = generate_content_with_retry(self.model, aggregation_prompt)
                aggregated_response = get_response_text(final_response)
        except Exception as e:
            # Fallback aggregation
            aggregated_response = "\n\n".join([
                f"{name}: {analysis['analysis']}"
                for name, analysis in agent_analyses.items()
                if analysis['status'] == 'success'
            ])
        
        print(f"📤 [ORCHESTRATOR → USER]")
        print(f"   Status: ✓ Ready")
        print(f"   Final response prepared from agent-to-agent communication")
        print(f"{'='*70}\n")
        
        return {
            "user_query": user_query,
            "agent_schedules": all_agent_schedules,
            "agent_comparisons": agent_comparisons,
            "agent_analyses": agent_analyses,
            "aggregated_response": aggregated_response,
            "timestamp": datetime.now().isoformat()
        }

