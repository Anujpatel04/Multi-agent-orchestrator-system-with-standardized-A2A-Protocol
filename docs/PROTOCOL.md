# Agent-to-Agent (A2A) Communication Protocol v1.0

## Overview

This document describes the standardized protocol for agent-to-agent communication in the multi-agent system. The protocol ensures reliable, structured, and extensible communication between agents.

## Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Orchestrator    │ ◄─── A2A Protocol Framework
│     Agent        │
└──────┬───────────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌─────┐ ┌─────┐
│Agent│ │Agent│
│  1  │ │  2  │
└─────┘ └─────┘
```

## Protocol Features

1. **Standardized Message Format**: All messages follow a consistent structure
2. **Message Types**: Defined message types for different communication patterns
3. **Agent Registry**: Dynamic agent discovery and registration
4. **Message Routing**: Intelligent routing of messages between agents
5. **Error Handling**: Standardized error responses
6. **Message History**: Track all communications for debugging
7. **Priority Levels**: Support for message prioritization
8. **Correlation IDs**: Track related messages in conversations

## Message Format

### AgentMessage Structure

```json
{
  "protocol_version": "1.0",
  "message_id": "uuid",
  "correlation_id": "uuid",
  "message_type": "query|response|broadcast|...",
  "from_agent": "agent_id",
  "to_agent": "agent_id|broadcast",
  "payload": {
    // Message-specific data
  },
  "priority": 1-4,
  "timestamp": "ISO8601",
  "metadata": {
    // Additional context
  }
}
```

## Message Types

### QUERY
Request information from an agent
```json
{
  "message_type": "query",
  "payload": {
    "query": "What is User 1's schedule?"
  }
}
```

### RESPONSE
Response to a query or request
```json
{
  "message_type": "response",
  "payload": {
    "data": { ... },
    "success": true
  }
}
```

### BROADCAST
Send message to all agents
```json
{
  "message_type": "broadcast",
  "to_agent": "broadcast"
}
```

### SCHEDULE_SHARE
Share schedule data between agents
```json
{
  "message_type": "schedule_share",
  "payload": {
    "schedule_data": { ... }
  }
}
```

### SCHEDULE_COMPARE
Request schedule comparison
```json
{
  "message_type": "schedule_compare",
  "payload": {
    "my_schedules": { ... },
    "other_schedules": { ... }
  }
}
```

## Priority Levels

- **LOW (1)**: Non-urgent messages
- **NORMAL (2)**: Standard messages (default)
- **HIGH (3)**: Important messages requiring quick response
- **URGENT (4)**: Critical messages requiring immediate attention

## Agent Registration

Agents must register with the system to participate in communication:

```python
protocol.register_agent(
    agent_id="agent1",
    agent_name="Agent 1",
    capabilities=["schedule_query", "schedule_management"],
    metadata={"user": "User 1"}
)
```

## Communication Patterns

### 1. Direct Query
```
Agent A → Query Message → Agent B
Agent B → Response Message → Agent A
```

### 2. Broadcast
```
Agent A → Broadcast Message → All Agents
Each Agent → Individual Response → Agent A
```

### 3. Orchestrated Communication
```
User → Orchestrator → Broadcast to Agents
Agents → Responses → Orchestrator
Orchestrator → Aggregate → User
```

## Error Handling

Standard error response format:
```json
{
  "success": false,
  "error": "Error message",
  "message_id": "uuid",
  "timestamp": "ISO8601"
}
```

## Best Practices

1. **Always use correlation IDs** for related messages
2. **Set appropriate priorities** for time-sensitive operations
3. **Include metadata** for context and debugging
4. **Handle errors gracefully** with proper error responses
5. **Register agents** with accurate capabilities
6. **Use message history** for debugging and auditing

## Future Enhancements

- Message encryption
- Async communication support
- Message queuing
- Protocol version negotiation
- Message compression
- Rate limiting
- Message validation schemas

