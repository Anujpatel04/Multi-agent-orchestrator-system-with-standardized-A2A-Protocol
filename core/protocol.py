
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid
import json

class MessageType(Enum):
    """Message types for agent communication"""
    QUERY = "query"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    REQUEST = "request"
    NOTIFY = "notify"
    ERROR = "error"
    ACK = "acknowledgment"
    HEARTBEAT = "heartbeat"
    SCHEDULE_SHARE = "schedule_share"
    SCHEDULE_COMPARE = "schedule_compare"
    AGGREGATE = "aggregate"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class AgentMessage:
    """Standardized message format for agent-to-agent communication"""
    
    def __init__(
        self,
        message_type: MessageType,
        from_agent: str,
        to_agent: str,
        payload: Dict[str, Any],
        message_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id or self.message_id
        self.message_type = message_type
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.payload = payload
        self.priority = priority
        self.timestamp = timestamp or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.protocol_version = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            "protocol_version": self.protocol_version,
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "message_type": self.message_type.value,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary"""
        return cls(
            message_type=MessageType(data["message_type"]),
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            payload=data["payload"],
            message_id=data.get("message_id"),
            correlation_id=data.get("correlation_id"),
            priority=MessagePriority(data.get("priority", 2)),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {})
        )
    
    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Deserialize message from JSON"""
        return cls.from_dict(json.loads(json_str))
    
    def create_response(
        self,
        to_agent: str,
        payload: Dict[str, Any],
        message_type: MessageType = MessageType.RESPONSE
    ) -> 'AgentMessage':
        """Create a response message using same correlation ID"""
        return AgentMessage(
            message_type=message_type,
            from_agent=to_agent,
            to_agent=self.from_agent,
            payload=payload,
            correlation_id=self.correlation_id,
            priority=self.priority,
            metadata={"responding_to": self.message_id}
        )
    
    def __repr__(self) -> str:
        return f"<AgentMessage {self.message_type.value} from:{self.from_agent} to:{self.to_agent} id:{self.message_id[:8]}>"


class AgentResponse:
    """Standardized response format"""
    
    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        message_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.data = data or {}
        self.error = error
        self.message_id = message_id or str(uuid.uuid4())
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message_id": self.message_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def success_response(cls, data: Dict[str, Any], message_id: Optional[str] = None) -> 'AgentResponse':
        return cls(success=True, data=data, message_id=message_id)
    
    @classmethod
    def error_response(cls, error: str, message_id: Optional[str] = None) -> 'AgentResponse':
        return cls(success=False, error=error, message_id=message_id)


class AgentRegistry:
    """Registry for agent discovery and management"""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register an agent in the system"""
        self.agents[agent_id] = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.agent_capabilities[agent_id] = capabilities
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "inactive"
            del self.agent_capabilities[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information"""
        return self.agents.get(agent_id)
    
    def get_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents with specific capability"""
        return [
            agent_id for agent_id, caps in self.agent_capabilities.items()
            if capability in caps
        ]
    
    def list_agents(self) -> List[str]:
        """List all active agents"""
        return [
            agent_id for agent_id, info in self.agents.items()
            if info["status"] == "active"
        ]
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered agents"""
        return self.agents.copy()


class MessageRouter:
    """Routes messages between agents"""
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.message_handlers: Dict[MessageType, callable] = {}
        self.message_history: List[AgentMessage] = []
        self.max_history = 1000
    
    def register_handler(self, message_type: MessageType, handler: callable):
        """Register a handler for specific message type"""
        self.message_handlers[message_type] = handler
    
    def route(self, message: AgentMessage) -> Optional[AgentResponse]:
        """
        Route a message to appropriate agent
        Returns response if available
        """
        # Validate message
        if not self._validate_message(message):
            return AgentResponse.error_response("Invalid message format")
        
        # Check if target agent exists
        if message.to_agent not in self.registry.list_agents():
            if message.to_agent != "broadcast":
                return AgentResponse.error_response(f"Agent {message.to_agent} not found")
        
        # Store in history
        self._add_to_history(message)
        
        # Route based on message type
        if message.to_agent == "broadcast":
            return self._broadcast(message)
        else:
            return self._route_to_agent(message)
    
    def _validate_message(self, message: AgentMessage) -> bool:
        """Validate message format"""
        if not message.from_agent or not message.to_agent:
            return False
        if not message.message_id:
            return False
        if not message.payload:
            return False
        return True
    
    def _route_to_agent(self, message: AgentMessage) -> Optional[AgentResponse]:
        """Route message to specific agent"""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                return handler(message)
            except Exception as e:
                return AgentResponse.error_response(f"Handler error: {str(e)}")
        return None
    
    def _broadcast(self, message: AgentMessage) -> AgentResponse:
        """Broadcast message to all agents"""
        responses = {}
        for agent_id in self.registry.list_agents():
            if agent_id != message.from_agent:
                handler = self.message_handlers.get(message.message_type)
                if handler:
                    try:
                        response = handler(message)
                        responses[agent_id] = response.to_dict() if response else None
                    except Exception as e:
                        responses[agent_id] = {"error": str(e)}
        
        return AgentResponse.success_response({
            "broadcast_responses": responses,
            "total_recipients": len(responses)
        })
    
    def _add_to_history(self, message: AgentMessage):
        """Add message to history"""
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
    
    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """Get message history with filters"""
        history = self.message_history
        
        if agent_id:
            history = [
                msg for msg in history
                if msg.from_agent == agent_id or msg.to_agent == agent_id
            ]
        
        if message_type:
            history = [msg for msg in history if msg.message_type == message_type]
        
        return history[-limit:]


class A2AProtocol:
    """
    Agent-to-Agent Protocol Framework
    Main interface for agent communication
    """
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.router = MessageRouter(self.registry)
        self.protocol_version = "1.0"
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register an agent"""
        self.registry.register_agent(agent_id, agent_name, capabilities, metadata)
    
    def send_message(
        self,
        message: AgentMessage,
        timeout: Optional[float] = None
    ) -> Optional[AgentResponse]:
        """Send a message and wait for response"""
        return self.router.route(message)
    
    def broadcast_message(self, message: AgentMessage) -> AgentResponse:
        """Broadcast message to all agents"""
        message.to_agent = "broadcast"
        return self.router.route(message)
    
    def query_agent(
        self,
        from_agent: str,
        to_agent: str,
        query: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentResponse]:
        """Send a query message to an agent"""
        message = AgentMessage(
            message_type=MessageType.QUERY,
            from_agent=from_agent,
            to_agent=to_agent,
            payload={"query": query},
            metadata=metadata or {}
        )
        return self.send_message(message)
    
    def share_schedule(
        self,
        from_agent: str,
        to_agent: str,
        schedule_data: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Share schedule data between agents"""
        message = AgentMessage(
            message_type=MessageType.SCHEDULE_SHARE,
            from_agent=from_agent,
            to_agent=to_agent,
            payload={"schedule_data": schedule_data},
            priority=MessagePriority.HIGH
        )
        return self.send_message(message)
    
    def compare_schedules(
        self,
        from_agent: str,
        to_agent: str,
        my_schedules: Dict[str, Any],
        other_schedules: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Request schedule comparison between agents"""
        message = AgentMessage(
            message_type=MessageType.SCHEDULE_COMPARE,
            from_agent=from_agent,
            to_agent=to_agent,
            payload={
                "my_schedules": my_schedules,
                "other_schedules": other_schedules
            },
            priority=MessagePriority.HIGH
        )
        return self.send_message(message)
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent"""
        return self.registry.get_agent(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return self.registry.list_agents()
    
    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[MessageType] = None
    ) -> List[AgentMessage]:
        """Get communication history"""
        return self.router.get_message_history(agent_id, message_type)
    
    def register_handler(self, message_type: MessageType, handler: callable):
        """Register a message handler"""
        self.router.register_handler(message_type, handler)

