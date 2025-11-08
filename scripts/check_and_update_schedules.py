"""
Quick script to check current schedules and update User 2's schedules if needed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent1, Agent2

def check_schedules():
    """Check what schedules are currently stored"""
    print("\n" + "="*70)
    print("Checking Current Schedules")
    print("="*70)
    
    agent1 = Agent1()
    agent2 = Agent2()
    
    # Check Agent 1
    agent1_schedules = agent1.get_all_schedules()
    print(f"\n[Agent 1 - User 1]")
    print(f"  Total schedules: {len(agent1_schedules['ids']) if agent1_schedules['ids'] else 0}")
    if agent1_schedules['ids']:
        for i, doc in enumerate(agent1_schedules['documents'], 1):
            print(f"  [{i}] {doc[:70]}...")
    else:
        print("  No schedules stored")
    
    # Check Agent 2
    agent2_schedules = agent2.get_all_schedules()
    print(f"\n[Agent 2 - User 2]")
    print(f"  Total schedules: {len(agent2_schedules['ids']) if agent2_schedules['ids'] else 0}")
    if agent2_schedules['ids']:
        for i, doc in enumerate(agent2_schedules['documents'], 1):
            print(f"  [{i}] {doc[:70]}...")
    else:
        print("  No schedules stored")
    
    # Compare if they're the same
    print("\n" + "="*70)
    if agent1_schedules['ids'] and agent2_schedules['ids']:
        agent1_docs = set(agent1_schedules['documents'])
        agent2_docs = set(agent2_schedules['documents'])
        
        if agent1_docs == agent2_docs:
            print("⚠️  WARNING: Both agents have the SAME schedules!")
            print("   User 2's schedules need to be updated.")
            return True
        else:
            print("✓ Schedules are different - good!")
            return False
    else:
        print("⚠️  One or both agents have no schedules.")
        return True

if __name__ == "__main__":
    try:
        needs_update = check_schedules()
        
        if needs_update:
            print("\n" + "="*70)
            print("To update User 2's schedules, run:")
            print("  python scripts/update_user2_schedule.py")
            print("="*70)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

