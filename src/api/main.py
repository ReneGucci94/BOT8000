# src/api/main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import threading
import asyncio

from src.database import get_db_session, init_db
from src.database.repository import TradeRepository, StrategyRepository, PatternRepository, BacktestRunRepository
from src.database.models import Trade, Strategy, Pattern
from src.agents.orchestrator import OrchestratorAgent

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BOT8000 Trading System", version="3.0.0")
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State (para demo)
active_tasks = {}

class OrchestratorConfig(BaseModel):
    pairs: List[str] = ["BTCUSDT"]
    years: List[int] = [2024]
    num_mutations: int = 3
    train_months: List[int] = [1, 2, 3]
    val_months: List[int] = [4]

@app.on_event("startup")
def startup_event():
    init_db()

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")

@app.post("/api/run-pipeline")
async def run_pipeline(config: OrchestratorConfig, background_tasks: BackgroundTasks):
    """Inicia el pipeline completo de ML en background."""
    task_id = str(uuid.uuid4())
    
    def run_task(tid, cfg):
        orchestrator = OrchestratorAgent()
        try:
            res = orchestrator.execute(cfg.dict())
            active_tasks[tid]['status'] = 'COMPLETED'
            active_tasks[tid]['result'] = res
        except Exception as e:
            active_tasks[tid]['status'] = 'FAILED'
            active_tasks[tid]['error'] = str(e)

    active_tasks[task_id] = {'status': 'RUNNING', 'config': config.dict()}
    background_tasks.add_task(run_task, task_id, config)
    
    return {"task_id": task_id, "status": "started"}

@app.get("/api/tasks/{task_id}")
def get_task_status(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return active_tasks[task_id]

@app.get("/api/stats/trades")
def get_trades_stats():
    with get_db_session() as db:
        trades = db.query(Trade).limit(100).all()
        # Simple stats
        if not trades:
            return {"count": 0}
        
        wins = [t for t in trades if t.profit_loss is not None and t.profit_loss > 0]
        losses = [t for t in trades if t.profit_loss is not None and t.profit_loss <= 0]
        
        return {
            "total_trades": len(trades),
            "win_rate": len(wins) / len(trades) * 100 if trades else 0,
            "recent_trades": [
                {
                    "pair": t.pair,
                    "side": t.side,
                    "pnl": float(t.profit_loss) if t.profit_loss is not None else 0.0,
                    "result": t.result,
                    "date": t.timestamp
                } for t in trades[-10:]
            ]
        }

@app.get("/api/strategies/approved")
def get_approved_strategies():
    with get_db_session() as db:
        strats = StrategyRepository.get_by_status(db, "APPROVED")
        return [
            {
                "name": s.name,
                "pf": float(s.profit_factor) if s.profit_factor else 0,
                "wr": float(s.win_rate) if s.win_rate else 0,
                "params": s.parameters
            } for s in strats
        ]

@app.get("/api/ml/patterns")
def get_patterns():
    with get_db_session() as db:
        patterns = PatternRepository.get_active_patterns(db)
        return [
            {
                "desc": p.description,
                "win_rate": float(p.win_rate),
                "samples": p.sample_size
            } for p in patterns
        ]
