"""
Interactive test script to check both agents separately
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent1, Agent2

def test_agent_interactive(agent, agent_name):
    """Interactive testing for a specific agent"""
    print(f"\n{'='*70}")
    print(f"Testing {agent_name} - Interactive Mode")
    print(f"{'='*70}")
    print(f"\nYou can now test {agent_name} with your own data.")
    print("Type 'back' to return to main menu or 'exit' to quit.\n")
    
    while True:
        print(f"\n[{agent_name} Options]")
        print("1. Store schedule/routine")
        print("2. Query schedule")
        print("3. View all stored schedules")
        print("4. Delete a schedule")
        print("5. Back to agent selection")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            print(f"\n[Storing data in {agent_name}]")
            schedule = input("Enter schedule/routine: ").strip()
            if schedule.lower() == 'back':
                continue
            if schedule.lower() == 'exit':
                sys.exit(0)
            
            if schedule:
                date = input("Date (optional, press Enter to skip): ").strip()
                category = input("Category (optional, press Enter to skip): ").strip()
                
                metadata = {}
                if date:
                    metadata['date'] = date
                if category:
                    metadata['category'] = category
                
                try:
                    result = agent.store_schedule(schedule, metadata if metadata else None)
                    print(f"\n✓ Successfully stored in {agent_name}!")
                    print(f"  Document ID: {result['doc_id']}")
                    print(f"  Summary: {result['summary']}")
                except Exception as e:
                    print(f"\n✗ Error: {e}")
            else:
                print("No data entered.")
        
        elif choice == "2":
            print(f"\n[Querying {agent_name}]")
            query = input("Enter your query: ").strip()
            if query.lower() == 'back':
                continue
            if query.lower() == 'exit':
                sys.exit(0)
            
            if query:
                try:
                    result = agent.query_schedule(query)
                    print(f"\n[{agent_name} Response]")
                    print(f"{result['response']}")
                    
                    if result['relevant_data']['documents'] and result['relevant_data']['documents'][0]:
                        print(f"\n[Found {len(result['relevant_data']['documents'][0])} relevant result(s)]")
                except Exception as e:
                    print(f"\n✗ Error: {e}")
            else:
                print("No query entered.")
        
        elif choice == "3":
            print(f"\n[All schedules in {agent_name}]")
            try:
                all_data = agent.get_all_schedules()
                if all_data['ids']:
                    print(f"\nTotal schedules: {len(all_data['ids'])}\n")
                    for i, doc_id in enumerate(all_data['ids']):
                        print(f"[{i+1}] ID: {doc_id}")
                        print(f"     Data: {all_data['documents'][i]}")
                        if all_data['metadatas'] and all_data['metadatas'][i]:
                            print(f"     Metadata: {all_data['metadatas'][i]}")
                        print()
                else:
                    print(f"\nNo schedules stored in {agent_name} yet.")
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "4":
            print(f"\n[Delete schedule from {agent_name}]")
            try:
                all_data = agent.get_all_schedules()
                if all_data['ids']:
                    print("\nAvailable schedules:")
                    for i, doc_id in enumerate(all_data['ids']):
                        print(f"  [{i+1}] {doc_id}: {all_data['documents'][i][:50]}...")
                    
                    doc_id = input("\nEnter document ID to delete: ").strip()
                    if doc_id.lower() == 'back':
                        continue
                    if doc_id.lower() == 'exit':
                        sys.exit(0)
                    
                    if doc_id in all_data['ids']:
                        result = agent.delete_schedule(doc_id)
                        print(f"\n✓ {result['message']}")
                    else:
                        print("Invalid document ID.")
                else:
                    print(f"\nNo schedules to delete in {agent_name}.")
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        elif choice == "5":
            break
        
        else:
            print("Invalid option. Please select 1-5.")

def main():
    print("\n" + "="*70)
    print("Agent Testing - Interactive Mode")
    print("="*70)
    print("\nTest both agents separately to verify they work independently.")
    print("Each agent has its own vector database.\n")
    
    # Initialize agents
    try:
        agent1 = Agent1()
        print("✓ Agent 1 initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Agent 1: {e}")
        sys.exit(1)
    
    try:
        agent2 = Agent2()
        print("✓ Agent 2 initialized")
    except Exception as e:
        print(f"✗ Failed to initialize Agent 2: {e}")
        sys.exit(1)
    
    while True:
        print("\n" + "-"*70)
        print("Select an agent to test:")
        print("  1. Test Agent 1")
        print("  2. Test Agent 2")
        print("  3. Exit")
        
        choice = input("\nYour choice (1-3): ").strip()
        
        if choice == "1":
            test_agent_interactive(agent1, "Agent 1")
        elif choice == "2":
            test_agent_interactive(agent2, "Agent 2")
        elif choice == "3":
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

