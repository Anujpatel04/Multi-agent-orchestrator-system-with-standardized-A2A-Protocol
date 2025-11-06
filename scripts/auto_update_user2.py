"""
Automated script to update User 2's schedule with different routines
This will clear existing schedules and add new ones
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent2

def update_user2_schedule():
    """Clear and update User 2's schedule with different routines"""
    print("\n" + "="*70)
    print("Updating User 2's Schedule Automatically")
    print("="*70)
    
    # Initialize Agent 2
    agent2 = Agent2()
    
    # Get current schedules
    current_schedules = agent2.get_all_schedules()
    current_count = len(current_schedules['ids']) if current_schedules['ids'] else 0
    
    print(f"\nCurrent schedules in Agent 2: {current_count}")
    
    if current_count > 0:
        print("\nClearing existing schedules...")
        deleted_count = agent2.vector_db.delete_all()
        print(f"✓ Deleted {deleted_count} existing schedules")
        print("⏳ Waiting 5 seconds...")
        time.sleep(5)
    
    # New completely different schedules for User 2
    print("\n" + "="*70)
    print("Storing NEW schedules for User 2...")
    print("="*70)
    
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
        }
    ]
    
    print(f"\n⚠️  Note: Free tier allows 2 requests/minute.")
    print(f"   Storing {len(routines)} routines will take approximately {len(routines) * 35 / 60:.1f} minutes.")
    print(f"   Please wait...\n")
    
    for i, routine in enumerate(routines, 1):
        print(f"\n[{i}/{len(routines)}] Storing routine in Agent 2...")
        try:
            result = agent2.store_schedule(routine["schedule"], routine["metadata"])
            print(f"✓ Stored: {routine['schedule'][:60]}...")
            print(f"  Document ID: {result['doc_id']}")
            
            # Wait 35 seconds between requests to avoid rate limits
            if i < len(routines):
                print(f"  ⏳ Waiting 35 seconds... ({len(routines) - i} remaining)")
                time.sleep(35)
        except Exception as e:
            print(f"✗ Error storing routine: {e}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                print("  ⏳ Waiting 40 seconds before retry...")
                time.sleep(40)
                try:
                    result = agent2.store_schedule(routine["schedule"], routine["metadata"])
                    print(f"✓ Stored after retry: {routine['schedule'][:60]}...")
                    if i < len(routines):
                        print(f"  ⏳ Waiting 35 seconds... ({len(routines) - i} remaining)")
                        time.sleep(35)
                except Exception as e2:
                    print(f"✗ Failed after retry: {e2}")
    
    print("\n" + "="*70)
    print("✓ User 2's schedules updated successfully!")
    print("="*70)
    
    # Show summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    
    agent2_schedules = agent2.get_all_schedules()
    print(f"\nAgent 2 (User 2) stored routines: {len(agent2_schedules['ids'])}")
    for i, doc in enumerate(agent2_schedules['documents'], 1):
        print(f"  [{i}] {doc[:70]}...")
    
    print("\n" + "="*70)
    print("✓ User 2 now has completely different schedules from User 1!")
    print("="*70)
    print("\nKey differences:")
    print("  - User 1: Early riser (6:30 AM), traditional work hours, early bedtime")
    print("  - User 2: Late riser (9:30 AM), later work hours, night owl (sleeps at 3 AM)")
    print("="*70)

if __name__ == "__main__":
    try:
        update_user2_schedule()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

