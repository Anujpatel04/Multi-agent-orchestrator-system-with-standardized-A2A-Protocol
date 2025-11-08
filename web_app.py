
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from agents import OrchestratorAgent, Agent1, Agent2
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Initialize orchestrator and agents
orchestrator = None
agent1 = None
agent2 = None

def init_agents():
    global orchestrator, agent1, agent2
    try:
        orchestrator = OrchestratorAgent()
        agent1 = Agent1()
        agent2 = Agent2()
        return True
    except Exception as e:
        print(f"Error initializing agents: {e}")
        return False

init_agents()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/agents/status')
def get_agents_status():
    """Get status of all agents"""
    try:
        status = {
            'orchestrator': {
                'status': 'ready' if orchestrator else 'not_ready',
                'name': 'Orchestrator Agent',
                'description': 'Master coordinator that manages all agents'
            },
            'agent1': {
                'status': 'ready' if agent1 else 'not_ready',
                'name': 'Agent 1',
                'description': 'Specialized agent with its own schedule database'
            },
            'agent2': {
                'status': 'ready' if agent2 else 'not_ready',
                'name': 'Agent 2',
                'description': 'Specialized agent with its own schedule database'
            }
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/data')
def get_agents_data():
    """Get data from all agents"""
    try:
        data = {}
        
        # Get Agent 1 data
        if agent1:
            agent1_schedules = agent1.get_all_schedules()
            data['agent1'] = {
                'total_schedules': len(agent1_schedules['ids']),
                'schedules': [
                    {
                        'id': agent1_schedules['ids'][i],
                        'content': agent1_schedules['documents'][i],
                        'metadata': agent1_schedules['metadatas'][i] if agent1_schedules['metadatas'] else {}
                    }
                    for i in range(len(agent1_schedules['ids']))
                ]
            }
        else:
            data['agent1'] = {'total_schedules': 0, 'schedules': []}
        
        # Get Agent 2 data
        if agent2:
            agent2_schedules = agent2.get_all_schedules()
            data['agent2'] = {
                'total_schedules': len(agent2_schedules['ids']),
                'schedules': [
                    {
                        'id': agent2_schedules['ids'][i],
                        'content': agent2_schedules['documents'][i],
                        'metadata': agent2_schedules['metadatas'][i] if agent2_schedules['metadatas'] else {}
                    }
                    for i in range(len(agent2_schedules['ids']))
                ]
            }
        else:
            data['agent2'] = {'total_schedules': 0, 'schedules': []}
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_agents():
    """Query agents through orchestrator"""
    try:
        data = request.json
        user_query = data.get('query', '')
        query_type = data.get('type', 'all')  # 'all', 'smart', or 'common_time'
        conversation_history = data.get('conversation_history', [])  # Optional conversation context
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Create communication log
        communication_log = []
        communication_log.append({
            'timestamp': datetime.now().isoformat(),
            'from': 'user',
            'to': 'orchestrator',
            'message': user_query,
            'type': 'query'
        })
        
        # Query through orchestrator
        if query_type == 'common_time':
            result = orchestrator.find_common_free_time(user_query)
            
            # Add agent-to-agent communication logs
            communication_log.append({
                'timestamp': datetime.now().isoformat(),
                'from': 'orchestrator',
                'to': 'all_agents',
                'message': 'Requesting schedules for agent-to-agent communication',
                'type': 'broadcast'
            })
            
            # Add agent-to-agent communication
            for agent_name in result.get('agent_schedules', {}).keys():
                communication_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'from': agent_name.lower().replace(' ', '_'),
                    'to': 'orchestrator',
                    'message': f'Shared {len(result["agent_schedules"][agent_name]["ids"])} schedules',
                    'type': 'response'
                })
            
            # Add inter-agent communication
            agent_list = list(result.get('agent_schedules', {}).keys())
            for i, agent1 in enumerate(agent_list):
                for j, agent2 in enumerate(agent_list):
                    if i != j:
                        communication_log.append({
                            'timestamp': datetime.now().isoformat(),
                            'from': agent1.lower().replace(' ', '_'),
                            'to': agent2.lower().replace(' ', '_'),
                            'message': 'Requesting schedule comparison',
                            'type': 'agent_to_agent'
                        })
            
            # Add agent analyses
            for agent_name, analysis in result.get('agent_analyses', {}).items():
                communication_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'from': agent_name.lower().replace(' ', '_'),
                    'to': 'orchestrator',
                    'message': analysis['analysis'][:200] if analysis['status'] == 'success' else f"Error: {analysis.get('error', 'Unknown')}",
                    'type': 'analysis'
                })
            
        elif query_type == 'smart':
            result = orchestrator.smart_query(user_query)
            communication_log.append({
                'timestamp': datetime.now().isoformat(),
                'from': 'orchestrator',
                'to': 'all_agents',
                'message': f"Routing decision: {result.get('routing_decision', 'all')}",
                'type': 'routing'
            })
        else:
            result = orchestrator.query_all_agents(user_query)
            communication_log.append({
                'timestamp': datetime.now().isoformat(),
                'from': 'orchestrator',
                'to': 'all_agents',
                'message': 'Broadcasting query to all agents',
                'type': 'broadcast'
            })
        
        # Add agent responses to log (for non-common_time queries)
        if query_type != 'common_time':
            for agent_name, response_data in result['agent_responses'].items():
                communication_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'from': agent_name.lower().replace(' ', '_'),
                    'to': 'orchestrator',
                    'message': response_data['response'][:200] if response_data['status'] == 'success' else f"Error: {response_data.get('error', 'Unknown')}",
                    'type': 'response' if response_data['status'] == 'success' else 'error'
                })
        
        # Add aggregated response
        communication_log.append({
            'timestamp': datetime.now().isoformat(),
            'from': 'orchestrator',
            'to': 'user',
            'message': result['aggregated_response'],
            'type': 'aggregated_response'
        })
        
        return jsonify({
            'result': result,
            'communication_log': communication_log
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_name>/query', methods=['POST'])
def query_single_agent(agent_name):
    """Query a single agent directly"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if agent_name == 'agent1' and agent1:
            result = agent1.query_schedule(query)
            return jsonify({
                'agent': 'Agent 1',
                'query': query,
                'response': result['response'],
                'relevant_data': result['relevant_data']
            })
        elif agent_name == 'agent2' and agent2:
            result = agent2.query_schedule(query)
            return jsonify({
                'agent': 'Agent 2',
                'query': query,
                'response': result['response'],
                'relevant_data': result['relevant_data']
            })
        else:
            return jsonify({'error': 'Agent not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 Starting Web Frontend for Agent System")
    print("="*70)
    print("\n📡 Server will be available at: http://localhost:5001")
    print("📊 Open your browser to visualize all agents")
    print("\n" + "="*70 + "\n")
    
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

