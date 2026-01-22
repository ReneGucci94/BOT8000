# src/agents/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import uuid

from src.agents.types import AgentStatus, AgentProgress
from src.database import get_db_session
from src.database.repository import AgentLogRepository

class BaseAgent(ABC):
    """Clase base para todos los agentes del sistema"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_id = uuid.uuid4()
        self.status = AgentStatus.IDLE
        self.progress: Optional[AgentProgress] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self._setup_logging()
    
    def _setup_logging(self):
        """Configurar logging del agente"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'[{self.agent_name}] %(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Log con persistencia en DB"""
        # Log a consola
        log_method = getattr(self.logger, level.lower())
        log_method(message)
        
        # Log a DB
        try:
            with get_db_session() as db:
                AgentLogRepository.log(db, self.agent_name, level.upper(), message, context)
        except Exception as e:
            self.logger.error(f"Error logging to DB: {e}")
    
    def update_progress(self, current: int, total: int, message: str):
        """Actualizar progreso del agente"""
        self.progress = AgentProgress.create(
            current=current,
            total=total,
            status=self.status,
            message=message
        )
        self.log('INFO', f"Progress: {self.progress.percentage}% - {message}")
    
    def start(self):
        """Iniciar agente"""
        self.status = AgentStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.log('INFO', f"Agent {self.agent_name} started")
    
    def complete(self):
        """Marcar agente como completado"""
        self.status = AgentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        duration = (self.completed_at - self.started_at).total_seconds() if self.started_at else 0
        self.log('INFO', f"Agent {self.agent_name} completed in {duration:.2f}s")
    
    def fail(self, error: str):
        """Marcar agente como fallido"""
        self.status = AgentStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()
        self.log('ERROR', f"Agent {self.agent_name} failed: {error}")
    
    @abstractmethod
    def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar lógica del agente (debe ser implementado por subclases)"""
        pass
    
    def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar agente con manejo de errores"""
        try:
            self.start()
            result = self.run(config)
            self.complete()
            return result
        except Exception as e:
            self.fail(str(e))
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener status actual del agente"""
        return {
            'agent_name': self.agent_name,
            'agent_id': str(self.agent_id),
            'status': self.status.value,
            'progress': {
                'current': self.progress.current if self.progress else 0,
                'total': self.progress.total if self.progress else 0,
                'percentage': self.progress.percentage if self.progress else 0,
                'message': self.progress.message if self.progress else ''
            } if self.progress else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error
        }
