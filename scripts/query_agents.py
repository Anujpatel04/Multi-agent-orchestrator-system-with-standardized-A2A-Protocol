"""
Simple script to query both agents separately
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent1, Agent2

def query_agent(agent, agent_name):
    """Query a specific agent"""
    print(f"\n{'='*70}")
    print(f"Querying {agent_name}")
    print(f"{'='*70}")
    
    # Show what's in the database
    all_data = agent.get_all_schedules()
    if all_data['ids']:
        print(f"\n{agent_name} has {len(all_data['ids'])} stored schedule(s):")
        for i, doc in enumerate(all_data['documents'], 1):
            print(f"  [{i}] {doc[:70]}...")
    else:
        print(f"\n{agent_name} has no schedules stored yet.")
        return
    
    print("\n" + "-"*70)
    
    while True:
        query = input(f"\nEnter your query for {agent_name} (or 'back' to return, 'exit' to quit): ").strip()
        
        if query.lower() == 'back':
            break
        if query.lower() == 'exit':
            sys.exit(0)
        
        if not query:
            print("Please enter a query.")
            continue
        
        try:
            print(f"\n[{agent_name} is thinking...]")
            result = agent.query_schedule(query)
            
            print(f"\n{agent_name} Response:")
            print("-"*70)
            print(result['response'])
            print("-"*70)
            
            # Show if relevant data was found
            if result['relevant_data']['documents'] and result['relevant_data']['documents'][0]:
                print(f"\n[Found {len(result['relevant_data']['documents'][0])} relevant result(s) from {agent_name}'s database]")
            
        except Exception as e:
            print(f"\n✗ Error querying {agent_name}: {e}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                print("\n⚠️  Rate limit hit. Please wait a moment and try again.")

def main():
    print("\n" + "="*70)
    print("Agent Query Interface")
    print("="*70)
    print("\nQuery both agents separately to see their different data.")
    print("Each agent has its own vector database with unique routines.\n")
    
    # Initialize agents
    try:
        print("Initializing agents...")
        agent1 = Agent1()
        print("✓ Agent 1 ready")
        agent2 = Agent2()
        print("✓ Agent 2 ready")
    except Exception as e:
        print(f"\n✗ Error initializing agents: {e}")
        sys.exit(1)
    
    while True:
        print("\n" + "="*70)
        print("Select an agent to query:")
        print("  1. Query Agent 1")
        print("  2. Query Agent 2")
        print("  3. Compare both agents (view stored data)")
        print("  4. Exit")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == "1":
            query_agent(agent1, "Agent 1")
        elif choice == "2":
            query_agent(agent2, "Agent 2")
        elif choice == "3":
            print("\n" + "="*70)
            print("Comparing Both Agents")
            print("="*70)
            
            print("\n[Agent 1 stored routines:]")
            agent1_data = agent1.get_all_schedules()
            if agent1_data['ids']:
                print(f"  Total: {len(agent1_data['ids'])} routines")
                for i, doc in enumerate(agent1_data['documents'], 1):
                    print(f"  [{i}] {doc[:60]}...")
            else:
                print("  No routines stored yet.")
            
            print("\n[Agent 2 stored routines:]")
            agent2_data = agent2.get_all_schedules()
            if agent2_data['ids']:
                print(f"  Total: {len(agent2_data['ids'])} routines")
                for i, doc in enumerate(agent2_data['documents'], 1):
                    print(f"  [{i}] {doc[:60]}...")
            else:
                print("  No routines stored yet.")
            
            print("\n" + "="*70)
            print("✓ Notice: Each agent has its own separate database!")
            print("="*70)
            
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please select 1-4.")

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

