# Multi-Agent Orchestrator System

A production-ready multi-agent system with an orchestrator pattern for coordinating specialized agents. Each agent maintains its own vector database and uses Google's Gemini API for intelligent interactions.

## Features

- **Orchestrator Agent**: Coordinates queries across all agents and aggregates responses
- **Agent-to-Agent Protocol**: Standardized communication framework (A2A Protocol v1.0)
- **Independent Agents**: Each agent has separate vector database storage
- **Web Dashboard**: Professional frontend for visualizing agent interactions
- **Smart Routing**: Intelligent query routing based on agent capabilities
- **Schedule Management**: Store and query daily routines using natural language
- **Real-time Communication Log**: Track all agent-to-agent communications

## Architecture

```
User → Orchestrator Agent → Agent 1
                        → Agent 2
                        ↓
                  [Aggregate Responses]
                        ↓
                    User Response
```

## Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Anujpatel04/Multi-agent-orchestrator-system-with-standardized-A2A-Protocol.git
cd Multi-agent-orchestrator-system-with-standardized-A2A-Protocol
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

5. Run the web application:
```bash
python web_app.py
```

Access the dashboard at `http://localhost:5001`

## Project Structure

```
.
├── agents/              # Agent implementations
│   ├── agent1.py        # Agent 1 (User 1)
│   ├── agent2.py        # Agent 2 (User 2)
│   └── orchestrator.py  # Orchestrator agent
├── core/                # Core framework
│   ├── protocol.py      # A2A Protocol implementation
│   ├── a2a_framework.py # Framework integration
│   ├── vector_db.py      # Vector database wrapper
│   ├── config.py        # Configuration
│   └── model_helper.py  # Gemini API helpers
├── scripts/             # Utility scripts
├── static/              # Web assets
│   ├── css/
│   └── js/
├── templates/           # HTML templates
├── docs/                # Documentation
│   ├── PROTOCOL.md      # Protocol specification
│   └── IMPROVEMENTS.md  # Framework improvements
├── web_app.py           # Flask web application
├── orchestrator_app.py  # CLI interface
└── requirements.txt     # Dependencies
```

## Usage

### Web Interface

Start the web server:
```bash
python web_app.py
```

The dashboard provides:
- Chat interface for agent queries
- Real-time agent status monitoring
- Schedule visualization
- Communication log viewer

### CLI Interface

```bash
python orchestrator_app.py
```

Options:
1. Query all agents
2. Smart routing
3. Find common free time
4. View system summary

### Scripts

Populate sample schedules:
```bash
python scripts/populate_routines.py
```

Query agents separately:
```bash
python scripts/query_agents.py
```

## Agent-to-Agent Protocol

The system implements a standardized A2A Protocol v1.0 for inter-agent communication:

- Standardized message format
- Message types (Query, Response, Broadcast, etc.)
- Agent registry for discovery
- Message routing and history
- Priority levels and correlation IDs

See `docs/PROTOCOL.md` for full specification.

## Configuration

Environment variables (`.env`):
```
GEMINI_API_KEY=your_api_key_here
```

## Technology Stack

- **Backend**: Python 3.9+, Flask
- **AI**: Google Gemini 2.5 Pro
- **Database**: ChromaDB (vector database)
- **Frontend**: HTML, CSS, JavaScript
- **Communication**: REST API, A2A Protocol

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
