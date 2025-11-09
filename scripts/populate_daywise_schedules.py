"""
Script to populate both agents with day-wise and time-wise schedules
Each agent will have detailed schedules for each day of the week
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent1, Agent2

def populate_user1_schedules(agent1):
    """Populate Agent 1 (User 1) with day-wise schedules"""
    print("\n" + "="*70)
    print("Storing day-wise schedules in Agent 1 (User 1)...")
    print("="*70)
    
    # User 1: Early riser, structured work schedule, fitness-focused
    schedules = [
        # Monday
        {
            "schedule": "Monday 06:30 AM - Wake up, morning meditation and yoga session",
            "metadata": {"day": "Monday", "time": "06:30", "category": "morning", "priority": "high"}
        },
        {
            "schedule": "Monday 08:00 AM - Breakfast and review daily goals",
            "metadata": {"day": "Monday", "time": "08:00", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Monday 09:00 AM - Start work, team standup meeting at 9:30 AM",
            "metadata": {"day": "Monday", "time": "09:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 10:00 AM - Deep work session on project tasks",
            "metadata": {"day": "Monday", "time": "10:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 12:30 PM - Lunch break",
            "metadata": {"day": "Monday", "time": "12:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Monday 02:00 PM - Afternoon walk and fresh air",
            "metadata": {"day": "Monday", "time": "14:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Monday 03:00 PM - Client meetings and collaboration",
            "metadata": {"day": "Monday", "time": "15:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 06:00 PM - Gym workout session",
            "metadata": {"day": "Monday", "time": "18:00", "category": "fitness", "priority": "high"}
        },
        {
            "schedule": "Monday 07:30 PM - Dinner with family",
            "metadata": {"day": "Monday", "time": "19:30", "category": "personal", "priority": "high"}
        },
        {
            "schedule": "Monday 09:30 PM - Reading time, prepare for next day",
            "metadata": {"day": "Monday", "time": "21:30", "category": "personal", "priority": "medium"}
        },
        
        # Tuesday
        {
            "schedule": "Tuesday 06:30 AM - Wake up, morning meditation",
            "metadata": {"day": "Tuesday", "time": "06:30", "category": "morning", "priority": "high"}
        },
        {
            "schedule": "Tuesday 08:00 AM - Breakfast",
            "metadata": {"day": "Tuesday", "time": "08:00", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Tuesday 09:00 AM - Work: Focus on coding and development",
            "metadata": {"day": "Tuesday", "time": "09:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Tuesday 11:00 AM - Code review session with team",
            "metadata": {"day": "Tuesday", "time": "11:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Tuesday 12:30 PM - Lunch break",
            "metadata": {"day": "Tuesday", "time": "12:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Tuesday 02:00 PM - Continue development work",
            "metadata": {"day": "Tuesday", "time": "14:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Tuesday 05:00 PM - Project planning and documentation",
            "metadata": {"day": "Tuesday", "time": "17:00", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Tuesday 06:30 PM - Evening run in the park",
            "metadata": {"day": "Tuesday", "time": "18:30", "category": "fitness", "priority": "high"}
        },
        {
            "schedule": "Tuesday 08:00 PM - Family time and dinner",
            "metadata": {"day": "Tuesday", "time": "20:00", "category": "personal", "priority": "high"}
        },
        
        # Wednesday
        {
            "schedule": "Wednesday 06:30 AM - Wake up, morning yoga",
            "metadata": {"day": "Wednesday", "time": "06:30", "category": "morning", "priority": "high"}
        },
        {
            "schedule": "Wednesday 09:00 AM - Work: Weekly team meeting at 9:30 AM",
            "metadata": {"day": "Wednesday", "time": "09:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 10:30 AM - Sprint planning and task assignment",
            "metadata": {"day": "Wednesday", "time": "10:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 12:30 PM - Lunch with colleagues",
            "metadata": {"day": "Wednesday", "time": "12:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Wednesday 02:00 PM - Focus on high-priority tasks",
            "metadata": {"day": "Wednesday", "time": "14:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 04:00 PM - One-on-one meeting with manager",
            "metadata": {"day": "Wednesday", "time": "16:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 06:00 PM - Gym: Strength training",
            "metadata": {"day": "Wednesday", "time": "18:00", "category": "fitness", "priority": "high"}
        },
        {
            "schedule": "Wednesday 08:00 PM - Dinner and relaxation",
            "metadata": {"day": "Wednesday", "time": "20:00", "category": "personal", "priority": "medium"}
        },
        
        # Thursday
        {
            "schedule": "Thursday 06:30 AM - Wake up, meditation",
            "metadata": {"day": "Thursday", "time": "06:30", "category": "morning", "priority": "high"}
        },
        {
            "schedule": "Thursday 09:00 AM - Work: Development and testing",
            "metadata": {"day": "Thursday", "time": "09:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Thursday 11:00 AM - Technical discussion with team",
            "metadata": {"day": "Thursday", "time": "11:00", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Thursday 12:30 PM - Lunch break",
            "metadata": {"day": "Thursday", "time": "12:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Thursday 02:00 PM - Bug fixing and code optimization",
            "metadata": {"day": "Thursday", "time": "14:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Thursday 05:00 PM - Review and update project documentation",
            "metadata": {"day": "Thursday", "time": "17:00", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Thursday 06:30 PM - Swimming session at local pool",
            "metadata": {"day": "Thursday", "time": "18:30", "category": "fitness", "priority": "high"}
        },
        {
            "schedule": "Thursday 08:00 PM - Dinner and movie night with family",
            "metadata": {"day": "Thursday", "time": "20:00", "category": "personal", "priority": "high"}
        },
        
        # Friday
        {
            "schedule": "Friday 06:30 AM - Wake up, light morning exercise",
            "metadata": {"day": "Friday", "time": "06:30", "category": "morning", "priority": "high"}
        },
        {
            "schedule": "Friday 09:00 AM - Work: Wrap up week's tasks",
            "metadata": {"day": "Friday", "time": "09:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Friday 10:00 AM - Weekly review and planning for next week",
            "metadata": {"day": "Friday", "time": "10:00", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Friday 12:30 PM - Team lunch celebration",
            "metadata": {"day": "Friday", "time": "12:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Friday 02:00 PM - Complete pending tasks and updates",
            "metadata": {"day": "Friday", "time": "14:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Friday 04:00 PM - End of week summary and reports",
            "metadata": {"day": "Friday", "time": "16:00", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Friday 06:00 PM - Gym: Cardio workout",
            "metadata": {"day": "Friday", "time": "18:00", "category": "fitness", "priority": "high"}
        },
        {
            "schedule": "Friday 08:00 PM - Dinner out with friends",
            "metadata": {"day": "Friday", "time": "20:00", "category": "social", "priority": "high"}
        },
        
        # Saturday
        {
            "schedule": "Saturday 07:00 AM - Wake up, longer morning routine",
            "metadata": {"day": "Saturday", "time": "07:00", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Saturday 09:00 AM - Weekend brunch with family",
            "metadata": {"day": "Saturday", "time": "09:00", "category": "personal", "priority": "high"}
        },
        {
            "schedule": "Saturday 11:00 AM - Grocery shopping and errands",
            "metadata": {"day": "Saturday", "time": "11:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Saturday 02:00 PM - Hobby time: Photography or reading",
            "metadata": {"day": "Saturday", "time": "14:00", "category": "hobby", "priority": "medium"}
        },
        {
            "schedule": "Saturday 04:00 PM - Afternoon walk or outdoor activity",
            "metadata": {"day": "Saturday", "time": "16:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Saturday 06:00 PM - Gym: Weekend workout",
            "metadata": {"day": "Saturday", "time": "18:00", "category": "fitness", "priority": "high"}
        },
        {
            "schedule": "Saturday 08:00 PM - Dinner and social gathering",
            "metadata": {"day": "Saturday", "time": "20:00", "category": "social", "priority": "high"}
        },
        
        # Sunday
        {
            "schedule": "Sunday 08:00 AM - Wake up, relaxed morning",
            "metadata": {"day": "Sunday", "time": "08:00", "category": "morning", "priority": "low"}
        },
        {
            "schedule": "Sunday 10:00 AM - Sunday brunch",
            "metadata": {"day": "Sunday", "time": "10:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Sunday 12:00 PM - Family time and activities",
            "metadata": {"day": "Sunday", "time": "12:00", "category": "personal", "priority": "high"}
        },
        {
            "schedule": "Sunday 03:00 PM - Plan and prepare for upcoming week",
            "metadata": {"day": "Sunday", "time": "15:00", "category": "planning", "priority": "medium"}
        },
        {
            "schedule": "Sunday 05:00 PM - Light exercise or yoga",
            "metadata": {"day": "Sunday", "time": "17:00", "category": "fitness", "priority": "medium"}
        },
        {
            "schedule": "Sunday 07:00 PM - Dinner and early rest",
            "metadata": {"day": "Sunday", "time": "19:00", "category": "personal", "priority": "medium"}
        }
    ]
    
    for i, schedule in enumerate(schedules, 1):
        print(f"\n[{i}/{len(schedules)}] Storing: {schedule['schedule'][:60]}...")
        try:
            result = agent1.store_schedule(schedule["schedule"], schedule["metadata"])
            print(f"✓ Stored successfully")
            
            # Wait between requests to avoid rate limits (free tier: 2 requests/minute)
            if i < len(schedules):
                wait_time = 35
                print(f"  ⏳ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"✗ Error: {e}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                print("  ⏳ Waiting 40 seconds before retry...")
                time.sleep(40)
                try:
                    result = agent1.store_schedule(schedule["schedule"], schedule["metadata"])
                    print(f"✓ Stored after retry")
                    if i < len(schedules):
                        time.sleep(35)
                except Exception as e2:
                    print(f"✗ Failed after retry: {e2}")
    
    print("\n" + "="*70)
    print("✓ User 1 day-wise schedules populated successfully!")
    print("="*70)

def populate_user2_schedules(agent2):
    """Populate Agent 2 (User 2) with different day-wise schedules"""
    print("\n" + "="*70)
    print("Storing day-wise schedules in Agent 2 (User 2)...")
    print("="*70)
    
    # User 2: Night owl, flexible schedule, creative work, different lifestyle
    schedules = [
        # Monday
        {
            "schedule": "Monday 09:30 AM - Wake up, coffee and breakfast",
            "metadata": {"day": "Monday", "time": "09:30", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Monday 10:30 AM - Check emails and messages",
            "metadata": {"day": "Monday", "time": "10:30", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Monday 11:00 AM - Start work: Creative projects and design",
            "metadata": {"day": "Monday", "time": "11:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 01:00 PM - Focused coding session",
            "metadata": {"day": "Monday", "time": "13:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 02:30 PM - Lunch break",
            "metadata": {"day": "Monday", "time": "14:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Monday 03:30 PM - Team video call and collaboration",
            "metadata": {"day": "Monday", "time": "15:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 05:30 PM - Continue development work",
            "metadata": {"day": "Monday", "time": "17:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Monday 07:00 PM - Online gaming session with friends",
            "metadata": {"day": "Monday", "time": "19:00", "category": "personal", "priority": "high"}
        },
        {
            "schedule": "Monday 09:00 PM - Order dinner delivery",
            "metadata": {"day": "Monday", "time": "21:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Monday 10:00 PM - Watch streaming series or movies",
            "metadata": {"day": "Monday", "time": "22:00", "category": "entertainment", "priority": "medium"}
        },
        
        # Tuesday
        {
            "schedule": "Tuesday 09:30 AM - Wake up, morning routine",
            "metadata": {"day": "Tuesday", "time": "09:30", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Tuesday 11:00 AM - Work: Design and UI/UX tasks",
            "metadata": {"day": "Tuesday", "time": "11:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Tuesday 01:00 PM - Deep work: Algorithm implementation",
            "metadata": {"day": "Tuesday", "time": "13:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Tuesday 02:30 PM - Lunch break",
            "metadata": {"day": "Tuesday", "time": "14:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Tuesday 03:30 PM - Code review and testing",
            "metadata": {"day": "Tuesday", "time": "15:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Tuesday 05:30 PM - Afternoon coffee break",
            "metadata": {"day": "Tuesday", "time": "17:30", "category": "break", "priority": "low"}
        },
        {
            "schedule": "Tuesday 06:30 PM - Review code and documentation",
            "metadata": {"day": "Tuesday", "time": "18:30", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Tuesday 08:00 PM - Social gaming or streaming",
            "metadata": {"day": "Tuesday", "time": "20:00", "category": "entertainment", "priority": "high"}
        },
        {
            "schedule": "Tuesday 11:00 PM - Late night coding or creative projects",
            "metadata": {"day": "Tuesday", "time": "23:00", "category": "work", "priority": "medium"}
        },
        
        # Wednesday
        {
            "schedule": "Wednesday 09:30 AM - Wake up",
            "metadata": {"day": "Wednesday", "time": "09:30", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Wednesday 11:00 AM - Work: Weekly sprint meeting",
            "metadata": {"day": "Wednesday", "time": "11:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 12:30 PM - Team brainstorming session",
            "metadata": {"day": "Wednesday", "time": "12:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 02:30 PM - Lunch break",
            "metadata": {"day": "Wednesday", "time": "14:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Wednesday 03:30 PM - Focus on high-priority features",
            "metadata": {"day": "Wednesday", "time": "15:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Wednesday 05:30 PM - Break and refresh",
            "metadata": {"day": "Wednesday", "time": "17:30", "category": "break", "priority": "low"}
        },
        {
            "schedule": "Wednesday 07:00 PM - Gaming session",
            "metadata": {"day": "Wednesday", "time": "19:00", "category": "entertainment", "priority": "high"}
        },
        {
            "schedule": "Wednesday 09:30 PM - Dinner and relaxation",
            "metadata": {"day": "Wednesday", "time": "21:30", "category": "personal", "priority": "medium"}
        },
        
        # Thursday
        {
            "schedule": "Thursday 09:30 AM - Wake up, morning coffee",
            "metadata": {"day": "Thursday", "time": "09:30", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Thursday 11:00 AM - Work: Development and debugging",
            "metadata": {"day": "Thursday", "time": "11:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Thursday 01:00 PM - Technical research and learning",
            "metadata": {"day": "Thursday", "time": "13:00", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Thursday 02:30 PM - Lunch break",
            "metadata": {"day": "Thursday", "time": "14:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Thursday 03:30 PM - Implementation of new features",
            "metadata": {"day": "Thursday", "time": "15:30", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Thursday 05:30 PM - Code optimization and refactoring",
            "metadata": {"day": "Thursday", "time": "17:30", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Thursday 07:00 PM - Online multiplayer gaming",
            "metadata": {"day": "Thursday", "time": "19:00", "category": "entertainment", "priority": "high"}
        },
        {
            "schedule": "Thursday 09:30 PM - Watch tech streams or tutorials",
            "metadata": {"day": "Thursday", "time": "21:30", "category": "learning", "priority": "medium"}
        },
        {
            "schedule": "Thursday 12:00 AM - Late night creative coding",
            "metadata": {"day": "Thursday", "time": "00:00", "category": "work", "priority": "low"}
        },
        
        # Friday
        {
            "schedule": "Friday 09:30 AM - Wake up",
            "metadata": {"day": "Friday", "time": "09:30", "category": "morning", "priority": "medium"}
        },
        {
            "schedule": "Friday 11:00 AM - Work: Wrap up week's tasks",
            "metadata": {"day": "Friday", "time": "11:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Friday 12:30 PM - Weekly review and planning",
            "metadata": {"day": "Friday", "time": "12:30", "category": "work", "priority": "medium"}
        },
        {
            "schedule": "Friday 02:30 PM - Team lunch and casual chat",
            "metadata": {"day": "Friday", "time": "14:30", "category": "break", "priority": "medium"}
        },
        {
            "schedule": "Friday 04:00 PM - Complete pending tasks",
            "metadata": {"day": "Friday", "time": "16:00", "category": "work", "priority": "high"}
        },
        {
            "schedule": "Friday 05:30 PM - End of week celebration",
            "metadata": {"day": "Friday", "time": "17:30", "category": "social", "priority": "medium"}
        },
        {
            "schedule": "Friday 07:00 PM - Extended gaming session with friends",
            "metadata": {"day": "Friday", "time": "19:00", "category": "entertainment", "priority": "high"}
        },
        {
            "schedule": "Friday 09:30 PM - Order dinner, watch movies",
            "metadata": {"day": "Friday", "time": "21:30", "category": "entertainment", "priority": "high"}
        },
        {
            "schedule": "Friday 12:00 AM - Late night social activities",
            "metadata": {"day": "Friday", "time": "00:00", "category": "social", "priority": "medium"}
        },
        
        # Saturday
        {
            "schedule": "Saturday 11:00 AM - Wake up late, weekend brunch",
            "metadata": {"day": "Saturday", "time": "11:00", "category": "morning", "priority": "low"}
        },
        {
            "schedule": "Saturday 12:30 PM - Casual activities or hobbies",
            "metadata": {"day": "Saturday", "time": "12:30", "category": "hobby", "priority": "medium"}
        },
        {
            "schedule": "Saturday 02:00 PM - Personal projects or side work",
            "metadata": {"day": "Saturday", "time": "14:00", "category": "work", "priority": "low"}
        },
        {
            "schedule": "Saturday 04:00 PM - Gaming or entertainment",
            "metadata": {"day": "Saturday", "time": "16:00", "category": "entertainment", "priority": "high"}
        },
        {
            "schedule": "Saturday 06:00 PM - Social gathering or online meetup",
            "metadata": {"day": "Saturday", "time": "18:00", "category": "social", "priority": "high"}
        },
        {
            "schedule": "Saturday 08:00 PM - Dinner and evening activities",
            "metadata": {"day": "Saturday", "time": "20:00", "category": "social", "priority": "medium"}
        },
        {
            "schedule": "Saturday 10:00 PM - Late night entertainment",
            "metadata": {"day": "Saturday", "time": "22:00", "category": "entertainment", "priority": "high"}
        },
        
        # Sunday
        {
            "schedule": "Sunday 11:00 AM - Wake up, relaxed morning",
            "metadata": {"day": "Sunday", "time": "11:00", "category": "morning", "priority": "low"}
        },
        {
            "schedule": "Sunday 12:30 PM - Brunch and plan for week",
            "metadata": {"day": "Sunday", "time": "12:30", "category": "planning", "priority": "medium"}
        },
        {
            "schedule": "Sunday 02:00 PM - Casual activities or rest",
            "metadata": {"day": "Sunday", "time": "14:00", "category": "personal", "priority": "low"}
        },
        {
            "schedule": "Sunday 04:00 PM - Prepare for upcoming week",
            "metadata": {"day": "Sunday", "time": "16:00", "category": "planning", "priority": "medium"}
        },
        {
            "schedule": "Sunday 06:00 PM - Gaming or streaming",
            "metadata": {"day": "Sunday", "time": "18:00", "category": "entertainment", "priority": "medium"}
        },
        {
            "schedule": "Sunday 08:00 PM - Dinner",
            "metadata": {"day": "Sunday", "time": "20:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Sunday 10:00 PM - Wind down, prepare for Monday",
            "metadata": {"day": "Sunday", "time": "22:00", "category": "personal", "priority": "medium"}
        },
        {
            "schedule": "Sunday 12:00 AM - Late night coding or projects",
            "metadata": {"day": "Sunday", "time": "00:00", "category": "work", "priority": "low"}
        }
    ]
    
    for i, schedule in enumerate(schedules, 1):
        print(f"\n[{i}/{len(schedules)}] Storing: {schedule['schedule'][:60]}...")
        try:
            result = agent2.store_schedule(schedule["schedule"], schedule["metadata"])
            print(f"✓ Stored successfully")
            
            # Wait between requests to avoid rate limits
            if i < len(schedules):
                wait_time = 35
                print(f"  ⏳ Waiting {wait_time} seconds...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"✗ Error: {e}")
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                print("  ⏳ Waiting 40 seconds before retry...")
                time.sleep(40)
                try:
                    result = agent2.store_schedule(schedule["schedule"], schedule["metadata"])
                    print(f"✓ Stored after retry")
                    if i < len(schedules):
                        time.sleep(35)
                except Exception as e2:
                    print(f"✗ Failed after retry: {e2}")
    
    print("\n" + "="*70)
    print("✓ User 2 day-wise schedules populated successfully!")
    print("="*70)

def main():
    print("\n" + "="*70)
    print("Day-wise Schedule Population Script")
    print("="*70)
    print("\nThis script will store detailed day-wise and time-wise schedules:")
    print("  - User 1: Early riser, structured schedule, fitness-focused")
    print("  - User 2: Night owl, flexible schedule, creative work, gaming")
    print("\n⚠️  Note: Free tier allows 2 requests/minute.")
    print("   Estimated time: ~30-35 minutes for User 1, ~35-40 minutes for User 2\n")
    
    input("Press Enter to start populating User 1 schedules...")
    
    # Initialize and populate Agent 1
    agent1 = Agent1()
    populate_user1_schedules(agent1)
    
    # Wait before populating Agent 2
    print("\n⏳ Waiting 40 seconds before populating User 2...")
    time.sleep(40)
    
    input("\nPress Enter to start populating User 2 schedules...")
    
    # Initialize and populate Agent 2
    agent2 = Agent2()
    populate_user2_schedules(agent2)
    
    # Summary
    print("\n\n" + "="*70)
    print("Summary")
    print("="*70)
    
    print("\nUser 1 stored schedules:")
    agent1_schedules = agent1.get_all_schedules()
    print(f"  Total: {len(agent1_schedules['ids'])} schedules")
    print("  Organized by: Day and Time")
    
    print("\nUser 2 stored schedules:")
    agent2_schedules = agent2.get_all_schedules()
    print(f"  Total: {len(agent2_schedules['ids'])} schedules")
    print("  Organized by: Day and Time")
    
    print("\n" + "="*70)
    print("✓ Both users now have comprehensive day-wise schedules!")
    print("✓ Each user has different schedules for each day of the week")
    print("✓ Schedules are organized by day and time")
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

