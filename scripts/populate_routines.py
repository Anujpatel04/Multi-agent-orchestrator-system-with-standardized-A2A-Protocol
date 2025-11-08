"""
Script to populate both agents with different daily routines
Each agent will have its own unique schedule data
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent1, Agent2

def populate_agent1_routines(agent1):
    """Populate Agent 1 with daily routines"""
    print("\n" + "="*70)
    print("Storing daily routines in Agent 1...")
    print("="*70)
    
    routines = [
        {
            "schedule": "Morning routine: Wake up at 6:30 AM, drink water, 20-minute meditation, morning yoga session at 7 AM, healthy breakfast at 8 AM, review daily goals",
            "metadata": {"time": "06:30-08:00", "category": "morning", "priority": "high"}
        },
        {
            "schedule": "Work schedule: Start work at 9 AM, team standup meeting at 9:30 AM, deep work session from 10 AM to 12 PM, lunch break at 12:30 PM",
            "metadata": {"time": "09:00-12:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Afternoon routine: Afternoon walk at 2 PM, client meetings from 3 PM to 5 PM, review and plan next day at 5:30 PM",
            "metadata": {"time": "14:00-17:30", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Evening routine: Gym workout at 6 PM, dinner at 7:30 PM, family time from 8 PM to 9 PM, reading time at 9:30 PM",
            "metadata": {"time": "18:00-21:30", "category": "personal", "priority": "high"}
        },
        {
            "schedule": "Night routine: Prepare for next day at 10 PM, skincare routine, journaling, lights out by 11 PM",
            "metadata": {"time": "22:00-23:00", "category": "night", "priority": "high"}
        }
    ]
    
    for i, routine in enumerate(routines, 1):
        print(f"\n[{i}/{len(routines)}] Storing routine in Agent 1...")
        try:
            result = agent1.store_schedule(routine["schedule"], routine["metadata"])
            print(f"✓ Stored: {routine['schedule'][:50]}...")
            print(f"  Document ID: {result['doc_id']}")
            
            # Wait 35 seconds between requests to avoid rate limits
            if i < len(routines):
                print("  ⏳ Waiting 35 seconds...")
                time.sleep(35)
        except Exception as e:
            print(f"✗ Error storing routine: {e}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                print("  ⏳ Waiting 40 seconds before retry...")
                time.sleep(40)
                try:
                    result = agent1.store_schedule(routine["schedule"], routine["metadata"])
                    print(f"✓ Stored after retry: {routine['schedule'][:50]}...")
                    if i < len(routines):
                        print("  ⏳ Waiting 35 seconds...")
                        time.sleep(35)
                except Exception as e2:
                    print(f"✗ Failed after retry: {e2}")
    
    print("\n" + "="*70)
    print("✓ Agent 1 routines populated successfully!")
    print("="*70)

def populate_agent2_routines(agent2):
    """Populate Agent 2 with completely different daily routines from User 1"""
    print("\n" + "="*70)
    print("Storing daily routines in Agent 2 (User 2)...")
    print("="*70)
    
    # Completely different schedule - User 2 is a night owl with different lifestyle
    routines = [
        {
            "schedule": "Late morning routine: Wake up at 9:30 AM, coffee and breakfast at 10 AM, check social media and messages, light stretching at 10:30 AM",
            "metadata": {"time": "09:30-10:30", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Work schedule: Start work at 11 AM, focus on coding and development tasks from 11 AM to 1 PM, team video call at 1:30 PM, lunch break at 2:30 PM",
            "metadata": {"time": "11:00-14:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Afternoon routine: Deep work session from 3 PM to 5:30 PM, afternoon coffee break at 5:30 PM, review code and documentation until 6:30 PM",
            "metadata": {"time": "15:00-18:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Evening routine: Online gaming session with friends from 7 PM to 9 PM, order dinner delivery at 9 PM, watch streaming series from 9:30 PM to 11:30 PM",
            "metadata": {"time": "19:00-23:30", "category": "personal", "priority": "high"}
        },
        {
            "schedule": "Night routine: Late night coding or creative projects from 12 AM to 2 AM, wind down with music, sleep by 3 AM",
            "metadata": {"time": "00:00-03:00", "category": "night", "priority": "medium"}
        },
        {
            "schedule": "Weekend schedule: Sleep in until 11 AM, brunch at 12 PM, casual activities or hobbies, evening social activities, late night entertainment",
            "metadata": {"time": "weekend", "category": "weekend", "priority": "low"}
        }
    ]
    
    for i, routine in enumerate(routines, 1):
        print(f"\n[{i}/{len(routines)}] Storing routine in Agent 2...")
        try:
            result = agent2.store_schedule(routine["schedule"], routine["metadata"])
            print(f"✓ Stored: {routine['schedule'][:50]}...")
            print(f"  Document ID: {result['doc_id']}")
            
            # Wait 35 seconds between requests to avoid rate limits
            if i < len(routines):
                print("  ⏳ Waiting 35 seconds...")
                time.sleep(35)
        except Exception as e:
            print(f"✗ Error storing routine: {e}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                print("  ⏳ Waiting 40 seconds before retry...")
                time.sleep(40)
                try:
                    result = agent2.store_schedule(routine["schedule"], routine["metadata"])
                    print(f"✓ Stored after retry: {routine['schedule'][:50]}...")
                    if i < len(routines):
                        print("  ⏳ Waiting 35 seconds...")
                        time.sleep(35)
                except Exception as e2:
                    print(f"✗ Failed after retry: {e2}")
    
    print("\n" + "="*70)
    print("✓ Agent 2 routines populated successfully!")
    print("="*70)

def main():
    print("\n" + "="*70)
    print("Daily Routine Population Script")
    print("="*70)
    print("\nThis script will store DIFFERENT daily routines in:")
    print("  - Agent 1's vector database")
    print("  - Agent 2's vector database")
    print("\n⚠️  Note: Free tier allows 2 requests/minute.")
    print("   Estimated time: ~10-12 minutes\n")
    
    input("Press Enter to start populating Agent 1...")
    
    # Initialize and populate Agent 1
    agent1 = Agent1()
    populate_agent1_routines(agent1)
    
    # Wait before populating Agent 2
    print("\n⏳ Waiting 40 seconds before populating Agent 2...")
    time.sleep(40)
    
    input("\nPress Enter to start populating Agent 2...")
    
    # Initialize and populate Agent 2
    agent2 = Agent2()
    populate_agent2_routines(agent2)
    
    # Summary
    print("\n\n" + "="*70)
    print("Summary")
    print("="*70)
    
    print("\nAgent 1 stored routines:")
    agent1_schedules = agent1.get_all_schedules()
    print(f"  Total: {len(agent1_schedules['ids'])} routines")
    for i, doc in enumerate(agent1_schedules['documents'], 1):
        print(f"  [{i}] {doc[:60]}...")
    
    print("\nAgent 2 stored routines:")
    agent2_schedules = agent2.get_all_schedules()
    print(f"  Total: {len(agent2_schedules['ids'])} routines")
    for i, doc in enumerate(agent2_schedules['documents'], 1):
        print(f"  [{i}] {doc[:60]}...")
    
    print("\n" + "="*70)
    print("✓ Both agents now have different daily routines stored!")
    print("✓ Each agent's data is stored in separate vector databases")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

