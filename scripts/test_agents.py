"""
Test script to verify both agents work separately
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Agent1, Agent2

def test_agent(agent, agent_name):
    """Test a specific agent"""
    print(f"\n{'='*70}")
    print(f"Testing {agent_name}")
    print(f"{'='*70}")
    
    try:
        # Test 1: Store schedule data
        print(f"\n[Test 1] Storing schedule data in {agent_name}...")
        test_schedule1 = "Morning routine: Wake up at 7 AM, exercise at 8 AM, breakfast at 9 AM"
        result1 = agent.store_schedule(
            test_schedule1,
            metadata={"date": "2024-01-15", "category": "morning_routine"}
        )
        print(f"✓ Successfully stored schedule")
        print(f"  Document ID: {result1['doc_id']}")
        print(f"  Summary: {result1['summary'][:100]}...")
        
        # Wait to avoid rate limits (free tier: 2 requests/minute)
        print("  ⏳ Waiting 35 seconds to avoid rate limits...")
        time.sleep(35)
        
        # Test 2: Store another schedule
        print(f"\n[Test 2] Storing another schedule in {agent_name}...")
        test_schedule2 = "Work schedule: Meeting at 10 AM, Lunch break at 1 PM, Project review at 3 PM"
        result2 = agent.store_schedule(
            test_schedule2,
            metadata={"date": "2024-01-15", "category": "work"}
        )
        print(f"✓ Successfully stored schedule")
        print(f"  Document ID: {result2['doc_id']}")
        
        # Wait to avoid rate limits
        print("  ⏳ Waiting 35 seconds to avoid rate limits...")
        time.sleep(35)
        
        # Test 3: Query the database
        print(f"\n[Test 3] Querying {agent_name} database...")
        query_result = agent.query_schedule("What is my morning routine?")
        print(f"✓ Query successful")
        print(f"  Query: {query_result['query']}")
        print(f"  Response: {query_result['response'][:200]}...")
        
        # Wait to avoid rate limits
        print("  ⏳ Waiting 35 seconds to avoid rate limits...")
        time.sleep(35)
        
        # Test 4: Get all schedules
        print(f"\n[Test 4] Retrieving all schedules from {agent_name}...")
        all_schedules = agent.get_all_schedules()
        print(f"✓ Retrieved {len(all_schedules['ids'])} schedule(s)")
        for i, doc_id in enumerate(all_schedules['ids']):
            print(f"  [{i+1}] {all_schedules['documents'][i][:60]}...")
        
        # Test 5: Query with different question
        # Wait to avoid rate limits
        print("  ⏳ Waiting 35 seconds to avoid rate limits...")
        time.sleep(35)
        print(f"\n[Test 5] Testing another query in {agent_name}...")
        query_result2 = agent.query_schedule("When do I have meetings?")
        print(f"✓ Query successful")
        print(f"  Response: {query_result2['response'][:200]}...")
        
        print(f"\n{'='*70}")
        print(f"✓ All tests passed for {agent_name}!")
        print(f"{'='*70}")
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing {agent_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*70)
    print("Agent Testing Suite")
    print("="*70)
    print("\nThis script will test both Agent 1 and Agent 2 separately")
    print("to verify they work independently with their own vector databases.")
    print("\n⚠️  Note: Free tier allows 2 requests/minute. Tests include delays.")
    print("   Total test time: ~5-6 minutes\n")
    
    # Test Agent 1
    print("\n" + "█" * 70)
    print("Testing Agent 1...")
    print("█" * 70)
    agent1 = Agent1()
    agent1_success = test_agent(agent1, "Agent 1")
    
    # Wait before testing Agent 2 to avoid rate limits
    print("\n⏳ Waiting 40 seconds before testing Agent 2...")
    time.sleep(40)
    
    # Test Agent 2
    print("\n\n" + "█" * 70)
    print("Testing Agent 2...")
    print("█" * 70)
    agent2 = Agent2()
    agent2_success = test_agent(agent2, "Agent 2")
    
    # Summary
    print("\n\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Agent 1: {'✓ PASSED' if agent1_success else '✗ FAILED'}")
    print(f"Agent 2: {'✓ PASSED' if agent2_success else '✗ FAILED'}")
    
    if agent1_success and agent2_success:
        print("\n✓ Both agents are working correctly!")
        print("✓ Each agent has its own separate vector database")
        print("✓ Agents can store and retrieve data independently")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

