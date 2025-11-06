
from core.protocol import (
    A2AProtocol, AgentMessage, MessageType, MessagePriority,
    AgentResponse, AgentRegistry
)
from typing import Dict, Any, Optional, List
import json

class A2AFramework:
    """High-level framework for agent-to-agent communication"""
    
    def __init__(self):
        self.protocol = A2AProtocol()
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Initialize default message handlers"""
        # Handler registration will be done by agents
        pass
    
    def register_agent_handler(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str],
        handler_func: callable,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register an agent with a handler function
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name
            capabilities: List of agent capabilities
            handler_func: Function to handle messages (takes AgentMessage, returns AgentResponse)
            metadata: Additional agent metadata
        """
        self.protocol.register_agent(agent_id, agent_name, capabilities, metadata)
        
        # Register handler for QUERY messages
        def message_handler(message: AgentMessage) -> AgentResponse:
            if message.to_agent == agent_id:
                try:
                    result = handler_func(message)
                    if isinstance(result, AgentResponse):
                        return result
                    elif isinstance(result, dict):
                        return AgentResponse.success_response(result)
                    else:
                        return AgentResponse.success_response({"data": result})
                except Exception as e:
                    return AgentResponse.error_response(str(e))
            return None
        
        self.protocol.register_handler(MessageType.QUERY, message_handler)
    
    def query_agent(
        self,
        from_agent: str,
        to_agent: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[AgentResponse]:
        """Send a query to an agent"""
        metadata = {"context": context} if context else {}
        return self.protocol.query_agent(from_agent, to_agent, query, metadata)
    
    def broadcast_query(
        self,
        from_agent: str,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AgentResponse]:
        """Broadcast query to all agents"""
        message = AgentMessage(
            message_type=MessageType.QUERY,
            from_agent=from_agent,
            to_agent="broadcast",
            payload={"query": query},
            metadata={"context": context} if context else {}
        )
        
        response = self.protocol.broadcast_message(message)
        if response and response.success:
            return response.data.get("broadcast_responses", {})
        return {}
    
    def share_schedule_data(
        self,
        from_agent: str,
        to_agent: str,
        schedule_data: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Share schedule data between agents"""
        return self.protocol.share_schedule(from_agent, to_agent, schedule_data)
    
    def compare_schedules(
        self,
        agent1_id: str,
        agent2_id: str,
        agent1_schedules: Dict[str, Any],
        agent2_schedules: Dict[str, Any]
    ) -> Optional[AgentResponse]:
        """Compare schedules between two agents"""
        return self.protocol.compare_schedules(
            agent1_id, agent2_id, agent1_schedules, agent2_schedules
        )
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent"""
        return self.protocol.get_agent_info(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return self.protocol.list_agents()
    
    def get_communication_log(
        self,
        agent_id: Optional[str] = None,
        message_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get communication history"""
        msg_type = None
        if message_type:
            msg_type = MessageType(message_type)
        
        messages = self.protocol.get_message_history(agent_id, msg_type)
        return [msg.to_dict() for msg in messages]
    
    def get_framework_stats(self) -> Dict[str, Any]:
        """Get framework statistics"""
        agents = self.protocol.registry.get_all_agents()
        history = self.protocol.router.message_history
        
        return {
            "protocol_version": self.protocol.protocol_version,
            "total_agents": len([a for a in agents.values() if a["status"] == "active"]),
            "total_messages": len(history),
            "agents": {
                agent_id: {
                    "name": info["agent_name"],
                    "capabilities": info["capabilities"],
                    "status": info["status"]
                }
                for agent_id, info in agents.items()
            }
        }

