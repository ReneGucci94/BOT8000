# src/agents/types.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class AgentStatus(Enum):
    """Estados posibles de un agente"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentMessage:
    """Mensaje entre agentes"""
    id: uuid.UUID
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    
    @classmethod
    def create(cls, from_agent: str, to_agent: str, message_type: str, payload: Dict[str, Any]):
        return cls(
            id=uuid.uuid4(),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.utcnow()
        )

@dataclass
class AgentProgress:
    """Progreso de un agente"""
    current: int
    total: int
    percentage: float
    status: AgentStatus
    message: str
    
    @classmethod
    def create(cls, current: int, total: int, status: AgentStatus, message: str):
        percentage = (current / total * 100) if total > 0 else 0
        return cls(
            current=current,
            total=total,
            percentage=round(percentage, 2),
            status=status,
            message=message
        )
