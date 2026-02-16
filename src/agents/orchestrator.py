# src/agents/orchestrator.py
from typing import Optional, Dict, Any, List, Tuple
from src.core.regime import MarketRegime
from src.core.market import MarketState
from src.core.classifier import classify_regime
from src.execution.executor import TradeSignal

# Import Agents
from src.agents.trend_hunter import TrendHunterAgent
from src.agents.mean_reversion import MeanReversionAgent
from src.agents.volatility_filter import VolatilityFilterAgent
from src.agents.breakout_hunter import BreakoutHunterAgent
from src.agents.sentiment_scout import SentimentScoutAgent

# Import Alphas
from src.alphas.base import Alpha
from src.alphas.combiner import AlphaCombiner
from src.alphas.ob_quality import Alpha_OB_Quality
from src.alphas.momentum import Alpha_Momentum
from src.alphas.volatility import Alpha_Volatility
from src.alphas.liquidity import Alpha_Liquidity
from src.alphas.ml_confidence import Alpha_ML_Confidence

class MSCOrchestrator:
    """
    Multi-Strategy Coordinator (MSC) Orchestrator (Layer 1).
    Selects the "Single Winner" specialized agent based on the market regime.
    Now also capable of Weighted Alpha Blending when parameters are provided (WFO).
    """
    
    def __init__(self):
        # 1. Map regimes to specialized agents
        self.agents = {
            MarketRegime.TRENDING_BULLISH: TrendHunterAgent(),
            MarketRegime.TRENDING_BEARISH: TrendHunterAgent(),
            MarketRegime.SIDEWAYS_RANGE: MeanReversionAgent(),
            MarketRegime.HIGH_VOLATILITY: VolatilityFilterAgent(),
            MarketRegime.BREAKOUT_PENDING: BreakoutHunterAgent(),
            MarketRegime.NEWS_DRIVEN: SentimentScoutAgent()
        }
        
        # 2. Initialize Alphas for WFO/Blending Mode
        self.alpha_ob = Alpha_OB_Quality()
        self.alpha_mom = Alpha_Momentum()
        self.alpha_vol = Alpha_Volatility()
        self.alpha_liq = Alpha_Liquidity()
        self.alpha_ml = Alpha_ML_Confidence() 
        
    def decide(self, market_state: MarketState, params: Dict[str, Any] = None) -> Optional[TradeSignal]:
        """
        Main decision method.
        If 'params' are provided (WFO), uses Weighted Alpha Logic.
        Otherwise, uses standard Regime Switching logic.
        """
        # 1. Classify with Params
        regime = classify_regime(market_state, params)
        
        if params:
            # --- WFO Dynamic Alpha Logic ---
            
            # Base Weights (Standard Portfolio)
            w_ob = 1.5 * params.get('alpha_ob_weight_mult', 1.0)
            w_mom = 2.0 * params.get('alpha_mom_weight_mult', 1.0)
            w_vol = 0.5 * params.get('alpha_vol_weight_mult', 1.0)
            w_liq = 0.8 * params.get('alpha_liq_weight_mult', 1.0)
            
            # Construct Weighted List
            alphas_list: List[Tuple[Alpha, float]] = [
                (self.alpha_ob, w_ob),
                (self.alpha_mom, w_mom),
                (self.alpha_vol, w_vol),
                (self.alpha_liq, w_liq)
            ]
            
            # Note: We create a light combiner just for the signal calculation
            combiner = AlphaCombiner(alphas_list)
            threshold = params.get('alpha_threshold', 0.6)
            
            signal = combiner.get_signal(market_state, threshold)
            
            # Inject Metadata
            if signal:
                object.__setattr__(signal, 'metadata', {
                    'agent': 'WFO_Alpha_Combiner',
                    'regime': regime.value,
                    'timestamp': getattr(market_state, 'timestamp', 0),
                    'params_hash': str(hash(str(params)))[:8]
                })
                
            return signal
            
        else:
            # --- Legacy / Standard Switching Logic ---
            return self.get_signal(market_state, regime_override=regime)
    
    def get_signal(self, market_state: MarketState, regime_override: Optional[MarketRegime] = None) -> Optional[TradeSignal]:
        """
        Coordinates the brain's decision.
        1. Classifies regime.
        2. Delegates to the specialist.
        3. Injects metadata for audit.
        """
        # 1. Classify Regime (The Brain)
        regime = regime_override if regime_override else classify_regime(market_state)
        
        # 2. Select Agent (The specialist)
        agent = self.agents.get(regime)
        if not agent:
            # Fallback to Sentiment Scout (Balanced) if for some reason regime is not mapped
            agent = self.agents[MarketRegime.NEWS_DRIVEN]
            
        # 3. Generate Signal
        signal = agent.generate_signal(market_state)
        
        # 4. Inject Metadata for audit (Layer 1 requirement)
        if signal:
            object.__setattr__(signal, 'metadata', {
                'agent': agent.__class__.__name__,
                'regime': regime.value,
                'timestamp': getattr(market_state, 'timestamp', 0)
            })
            
        return signal

# Backward-compatible alias
OrchestratorAgent = MSCOrchestrator
