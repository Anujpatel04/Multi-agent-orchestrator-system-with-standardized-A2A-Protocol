"""
Main application to run and interact with Agent 1 and Agent 2
"""

from agents import Agent1, Agent2
import sys

def main():
    print("=" * 60)
    print("Agent System - Daily Routine & Schedule Manager")
    print("=" * 60)
    print("\nAvailable Agents:")
    print("1. Agent 1")
    print("2. Agent 2")
    print("3. Exit")
    
    # Initialize agents
    agent1 = Agent1()
    agent2 = Agent2()
    
    while True:
        print("\n" + "-" * 60)
        choice = input("\nSelect an agent (1/2) or exit (3): ").strip()
        
        if choice == "1":
            interact_with_agent(agent1, "Agent 1")
        elif choice == "2":
            interact_with_agent(agent2, "Agent 2")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

def interact_with_agent(agent, agent_name):
    """Interact with a specific agent"""
    print(f"\n{'=' * 60}")
    print(f"Interacting with {agent_name}")
    print(f"{'=' * 60}")
    
    while True:
        print("\nOptions:")
        print("1. Store schedule/routine")
        print("2. Query schedule")
        print("3. View all schedules")
        print("4. Delete schedule")
        print("5. Back to main menu")
        
        action = input("\nSelect an action: ").strip()
        
        if action == "1":
            schedule_data = input("\nEnter schedule/routine information: ").strip()
            if schedule_data:
                # Optional: Add metadata
                print("\nAdd metadata? (optional, press Enter to skip)")
                date = input("Date (YYYY-MM-DD): ").strip()
                category = input("Category: ").strip()
                
                metadata = {}
                if date:
                    metadata['date'] = date
                if category:
                    metadata['category'] = category
                
                result = agent.store_schedule(schedule_data, metadata if metadata else None)
                print(f"\n✓ {result['message']}")
                print(f"Document ID: {result['doc_id']}")
                print(f"Summary: {result['summary']}")
            else:
                print("No data provided.")
        
        elif action == "2":
            query = input("\nEnter your query: ").strip()
            if query:
                result = agent.query_schedule(query)
                print(f"\nQuery: {query}")
                print(f"\nResponse:\n{result['response']}")
            else:
                print("No query provided.")
        
        elif action == "3":
            all_data = agent.get_all_schedules()
            if all_data['ids']:
                print("\nAll stored schedules:")
                print("-" * 60)
                for i, doc_id in enumerate(all_data['ids']):
                    print(f"\n[{i+1}] ID: {doc_id}")
                    print(f"    Data: {all_data['documents'][i]}")
                    if all_data['metadatas']:
                        print(f"    Metadata: {all_data['metadatas'][i]}")
            else:
                print("\nNo schedules stored yet.")
        
        elif action == "4":
            all_data = agent.get_all_schedules()
            if all_data['ids']:
                print("\nAvailable schedule IDs:")
                for i, doc_id in enumerate(all_data['ids']):
                    print(f"{i+1}. {doc_id}")
                doc_id = input("\nEnter document ID to delete: ").strip()
                if doc_id in all_data['ids']:
                    result = agent.delete_schedule(doc_id)
                    print(f"\n✓ {result['message']}")
                else:
                    print("Invalid document ID.")
            else:
                print("\nNo schedules to delete.")
        
        elif action == "5":
            break
        
        else:
            print("Invalid action. Please select 1-5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
