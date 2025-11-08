
from core.model_helper import get_gemini_model, get_response_text, generate_content_with_retry
from core.config import GEMINI_API_KEY
from agents.agent1 import Agent1
from agents.agent2 import Agent2
from datetime import datetime
import sys

class OrchestratorAgent:
    """Master orchestrator agent that coordinates queries across all agents"""
    
    def __init__(self):
        # Initialize Gemini model
        self.model = get_gemini_model(GEMINI_API_KEY)
        
        # Initialize all sub-agents
        self.agent1 = Agent1()
        self.agent2 = Agent2()
        
        # Store all available agents
        self.agents = {
            "Agent 1": self.agent1,
            "Agent 2": self.agent2
        }
        
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
    
    def query_all_agents(self, user_query: str):
        """
        Query all agents in the system and aggregate their responses
        
        Args:
            user_query: The user's query
            
        Returns:
            Aggregated response from all agents
        """
        print(f"\n{'='*70}")
        print("🔀 ORCHESTRATOR AGENT - COMMUNICATION LOG")
        print(f"{'='*70}")
        print(f"📥 [USER → ORCHESTRATOR]")
        print(f"   Query: {user_query}\n")
        
        # Collect responses from all agents
        agent_responses = {}
        
        print("📡 [ORCHESTRATOR → AGENTS] Broadcasting query to all agents...\n")
        print("-" * 70)
        
        for agent_name, agent in self.agents.items():
            try:
                print(f"📤 [ORCHESTRATOR → {agent_name}]")
                print(f"   Sending query: \"{user_query}\"")
                print(f"   Status: Processing...")
                sys.stdout.flush()  # Ensure output is displayed immediately
                
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
                
                agent_responses[agent_name] = {
                    "response": response['response'],
                    "relevant_data": response.get('relevant_data', {}),
                    "status": "success"
                }
                
                print(f"   Preview: {response['response'][:100]}...")
                print("-" * 70 + "\n")
                sys.stdout.flush()
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"📥 [{agent_name} → ORCHESTRATOR]")
                print(f"   Status: ✗ Error")
                print(f"   Error: {str(e)}")
                print(f"   Details: {error_details}")
                print("-" * 70 + "\n")
                sys.stdout.flush()
                
                agent_responses[agent_name] = {
                    "response": f"Error: {str(e)}",
                    "relevant_data": None,
                    "status": "error",
                    "error": str(e)
                }
        
        print("🔄 [ORCHESTRATOR] Aggregating responses from all agents...")
        
        # Aggregate responses using Gemini
        aggregated_response = self._aggregate_responses(user_query, agent_responses)
        
        print(f"📤 [ORCHESTRATOR → USER]")
        print(f"   Status: ✓ Ready")
        print(f"   Aggregated response prepared")
        print(f"{'='*70}\n")
        
        return {
            "user_query": user_query,
            "agent_responses": agent_responses,
            "aggregated_response": aggregated_response,
            "timestamp": datetime.now().isoformat()
        }
    
    def _aggregate_responses(self, user_query: str, agent_responses: dict):
        """
        Aggregate responses from all agents into a coherent answer
        
        Args:
            user_query: Original user query
            agent_responses: Dictionary of responses from each agent
            
        Returns:
            Aggregated response string
        """
        # Prepare context from all agent responses
        context = "Responses from all agents:\n\n"
        
        for agent_name, response_data in agent_responses.items():
            context += f"[{agent_name}]\n"
            if response_data['status'] == 'success':
                context += f"Response: {response_data['response']}\n"
                
                # Add relevant data if available
                if response_data['relevant_data'] and response_data['relevant_data']['documents']:
                    docs = response_data['relevant_data']['documents'][0]
                    if docs:
                        context += f"Found {len(docs)} relevant results in {agent_name}'s database.\n"
            else:
                context += f"Error: {response_data.get('error', 'Unknown error')}\n"
            context += "\n"
        
        # Generate aggregated response using Gemini
        prompt = f"""{self.system_prompt}

User Query: {user_query}

{context}

Provide ONLY a PRECISE, CONCISE answer. No explanations, no theory.
- Give direct answer to the user's query
- Maximum 2-3 sentences
- If information not available, respond briefly: "Information not found"
- Focus on the answer, not the process"""

        try:
            response = generate_content_with_retry(self.model, prompt)
            aggregated_text = get_response_text(response)
            return aggregated_text
        except Exception as e:
            # Fallback: return simple aggregation
            aggregated_parts = []
            for agent_name, response_data in agent_responses.items():
                if response_data['status'] == 'success':
                    aggregated_parts.append(f"{agent_name}: {response_data['response']}")
            
            return "\n\n".join(aggregated_parts) if aggregated_parts else "No responses available from agents."
    
    def smart_query(self, user_query: str):
        """
        Intelligently route query to relevant agents or query all
        
        Args:
            user_query: The user's query
            
        Returns:
            Response from relevant agents
        """
        # Use Gemini to determine which agents to query
        routing_prompt = f"""Based on this user query, determine which agents should be queried:
        
User Query: {user_query}

Available Agents:
- Agent 1: Has schedule/routine database 1
- Agent 2: Has schedule/routine database 2

Respond with:
- "all" if query should go to all agents
- "agent1" if only Agent 1 is relevant
- "agent2" if only Agent 2 is relevant
- "both" if both agents are relevant

Just respond with one word: all, agent1, agent2, or both"""
        
        try:
            print(f"\n{'='*70}")
            print("🧠 ORCHESTRATOR AGENT - SMART ROUTING")
            print(f"{'='*70}")
            print(f"📥 [USER → ORCHESTRATOR]")
            print(f"   Query: {user_query}\n")
            
            print("🔍 [ORCHESTRATOR] Analyzing query for intelligent routing...")
            routing_response = generate_content_with_retry(self.model, routing_prompt)
            routing_decision = get_response_text(routing_response).strip().lower()
            
            print(f"💡 [ORCHESTRATOR] Routing Decision: {routing_decision}\n")
            
            # Query based on routing decision
            agents_to_query = {}
            
            if routing_decision in ['all', 'both'] or 'agent1' in routing_decision:
                agents_to_query['Agent 1'] = self.agent1
            if routing_decision in ['all', 'both'] or 'agent2' in routing_decision:
                agents_to_query['Agent 2'] = self.agent2
            
            # If routing failed, default to all agents
            if not agents_to_query:
                agents_to_query = self.agents
            
            # Collect responses from selected agents
            agent_responses = {}
            for agent_name, agent in agents_to_query.items():
                try:
                    print(f"  → Querying {agent_name}...")
                    response = agent.query_schedule(user_query)
                    agent_responses[agent_name] = {
                        "response": response['response'],
                        "relevant_data": response['relevant_data'],
                        "status": "success"
                    }
                    print(f"    ✓ {agent_name} responded successfully")
                except Exception as e:
                    agent_responses[agent_name] = {
                        "response": f"Error: {str(e)}",
                        "status": "error",
                        "error": str(e)
                    }
                    print(f"    ✗ {agent_name} encountered an error: {str(e)}")
            
            # Aggregate responses
            aggregated_response = self._aggregate_responses(user_query, agent_responses)
            
            return {
                "user_query": user_query,
                "routing_decision": routing_decision,
                "agents_queried": list(agents_to_query.keys()),
                "agent_responses": agent_responses,
                "aggregated_response": aggregated_response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Fallback to querying all agents
            print(f"\nRouting failed, querying all agents...\n")
            return self.query_all_agents(user_query)
    
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

