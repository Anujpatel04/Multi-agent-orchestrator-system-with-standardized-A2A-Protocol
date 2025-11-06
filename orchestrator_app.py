"""
Main application for Orchestrator Agent
This is the user interface - user only interacts here, not with individual agents
"""

from agents import OrchestratorAgent
import sys

def main():
    print("\n" + "="*70)
    print("Orchestrator Agent System")
    print("="*70)
    print("\nThis is an Agent-to-Agent interaction system.")
    print("You interact only with the Orchestrator Agent.")
    print("The Orchestrator queries all other agents and aggregates their responses.")
    print("\nAvailable Agents in System:")
    print("  - Agent 1 (with its own schedule database)")
    print("  - Agent 2 (with its own schedule database)")
    print("\n" + "="*70)
    
    # Initialize orchestrator
    try:
        print("\nInitializing Orchestrator Agent...")
        orchestrator = OrchestratorAgent()
        print("✓ Orchestrator Agent ready")
        print("✓ All sub-agents connected\n")
    except Exception as e:
        print(f"\n✗ Error initializing Orchestrator: {e}")
        sys.exit(1)
    
    # Show summary of all agents' data
    print("="*70)
    print("System Overview")
    print("="*70)
    summary = orchestrator.get_all_agent_data_summary()
    for agent_name, data in summary.items():
        print(f"\n{agent_name}:")
        if 'error' in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Total schedules: {data['total_schedules']}")
            if data['schedules']:
                print("  Sample schedules:")
                for i, schedule in enumerate(data['schedules'][:3], 1):
                    print(f"    [{i}] {schedule[:60]}...")
    
    print("\n" + "="*70)
    
    while True:
        print("\n" + "-"*70)
        print("Options:")
        print("1. Query all agents (aggregated response)")
        print("2. Smart query (intelligent routing)")
        print("3. Find common free time (agent-to-agent communication)")
        print("4. View system summary")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == "1":
            user_query = input("\nEnter your query: ").strip()
            if user_query:
                try:
                    result = orchestrator.query_all_agents(user_query)
                    
                    print("\n" + "="*70)
                    print("AGGREGATED RESPONSE")
                    print("="*70)
                    print(f"\n{result['aggregated_response']}")
                    print("\n" + "="*70)
                    
                    # Show individual agent responses
                    print("\nIndividual Agent Responses:")
                    print("-"*70)
                    for agent_name, response_data in result['agent_responses'].items():
                        print(f"\n[{agent_name}]:")
                        if response_data['status'] == 'success':
                            print(f"  {response_data['response'][:200]}...")
                        else:
                            print(f"  Error: {response_data.get('error', 'Unknown')}")
                    
                    print("\n" + "="*70)
                    
                except Exception as e:
                    print(f"\n✗ Error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Please enter a query.")
        
        elif choice == "2":
            user_query = input("\nEnter your query: ").strip()
            if user_query:
                try:
                    result = orchestrator.smart_query(user_query)
                    
                    print("\n" + "="*70)
                    print("SMART ROUTED RESPONSE")
                    print("="*70)
                    print(f"\nRouting Decision: {result.get('routing_decision', 'all')}")
                    print(f"Agents Queried: {', '.join(result.get('agents_queried', []))}")
                    
                    print("\n" + "="*70)
                    print("AGGREGATED RESPONSE")
                    print("="*70)
                    print(f"\n{result['aggregated_response']}")
                    print("\n" + "="*70)
                    
                    # Show individual agent responses
                    print("\nIndividual Agent Responses:")
                    print("-"*70)
                    for agent_name, response_data in result['agent_responses'].items():
                        print(f"\n[{agent_name}]:")
                        if response_data['status'] == 'success':
                            print(f"  {response_data['response'][:200]}...")
                        else:
                            print(f"  Error: {response_data.get('error', 'Unknown')}")
                    
                    print("\n" + "="*70)
                    
                except Exception as e:
                    print(f"\n✗ Error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Please enter a query.")
        
        elif choice == "3":
            user_query = input("\nEnter your query (e.g., 'Find common free time', 'When are both users free?'): ").strip()
            if user_query:
                try:
                    result = orchestrator.find_common_free_time(user_query)
                    
                    print("\n" + "="*70)
                    print("AGENT-TO-AGENT COMMUNICATION RESULT")
                    print("="*70)
                    print(f"\n{result['aggregated_response']}")
                    print("\n" + "="*70)
                    
                    # Show individual agent analyses
                    print("\nIndividual Agent Analyses:")
                    print("-"*70)
                    for agent_name, analysis in result['agent_analyses'].items():
                        print(f"\n[{agent_name}]:")
                        if analysis['status'] == 'success':
                            print(f"  {analysis['analysis'][:300]}...")
                        else:
                            print(f"  Error: {analysis.get('error', 'Unknown')}")
                    
                    print("\n" + "="*70)
                    
                except Exception as e:
                    print(f"\n✗ Error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("Please enter a query.")
        
        elif choice == "4":
            print("\n" + "="*70)
            print("System Summary")
            print("="*70)
            summary = orchestrator.get_all_agent_data_summary()
            for agent_name, data in summary.items():
                print(f"\n{agent_name}:")
                if 'error' in data:
                    print(f"  Error: {data['error']}")
                else:
                    print(f"  Total schedules: {data['total_schedules']}")
                    if data['schedules']:
                        print("  Schedules:")
                        for i, schedule in enumerate(data['schedules'], 1):
                            print(f"    [{i}] {schedule[:70]}...")
            print("\n" + "="*70)
        
        elif choice == "5":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please select 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

