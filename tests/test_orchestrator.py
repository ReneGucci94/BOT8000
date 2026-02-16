# tests/test_orchestrator.py
"""
Tests for MSCOrchestrator (Layer 1 Brain).
Covers both WFO alpha-blending mode and standard regime-switching mode.
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal

from src.agents.orchestrator import MSCOrchestrator, OrchestratorAgent
from src.core.market import MarketState
from src.core.regime import MarketRegime
from src.execution.executor import TradeSignal
from src.execution.broker import OrderSide


@pytest.fixture
def orchestrator():
    """Create a fresh MSCOrchestrator instance."""
    return MSCOrchestrator()


@pytest.fixture
def mock_market_state():
    """Build a minimal MarketState for testing."""
    state = MarketState.empty("BTCUSDT")
    return state


# ── alias ───────────────────────────────────────────────────────
def test_orchestrator_agent_alias():
    """OrchestratorAgent must be the same class as MSCOrchestrator."""
    assert OrchestratorAgent is MSCOrchestrator


# ── decide() with WFO params (alpha-blending) ──────────────────
@patch("src.agents.orchestrator.classify_regime")
def test_decide_with_params_returns_signal_or_none(mock_classify, orchestrator, mock_market_state):
    """When WFO params are provided, decide() uses AlphaCombiner path."""
    mock_classify.return_value = MarketRegime.TRENDING_BULLISH

    params = {
        "alpha_threshold": 0.01,       # Very low threshold → likely to produce signal
        "alpha_ob_weight_mult": 1.0,
        "alpha_mom_weight_mult": 1.0,
        "alpha_vol_weight_mult": 1.0,
        "alpha_liq_weight_mult": 1.0,
    }

    # decide() should not crash; result is either a TradeSignal or None
    result = orchestrator.decide(mock_market_state, params=params)
    assert result is None or isinstance(result, TradeSignal)

    # classify_regime must have been called with params
    mock_classify.assert_called_once_with(mock_market_state, params)


@patch("src.agents.orchestrator.classify_regime")
def test_decide_with_params_injects_metadata(mock_classify, orchestrator, mock_market_state):
    """If AlphaCombiner produces a signal, metadata must contain WFO marker."""
    mock_classify.return_value = MarketRegime.TRENDING_BULLISH

    # Patch combiner to guarantee a signal
    fake_signal = TradeSignal(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        entry_price=Decimal("50000"),
        stop_loss=Decimal("49000"),
        take_profit=Decimal("52000"),
        confidence=0.9,
        metadata={},
    )

    with patch("src.agents.orchestrator.AlphaCombiner") as MockCombiner:
        MockCombiner.return_value.get_signal.return_value = fake_signal
        result = orchestrator.decide(mock_market_state, params={"alpha_threshold": 0.5})

    assert result is not None
    assert result.metadata["agent"] == "WFO_Alpha_Combiner"
    assert result.metadata["regime"] == MarketRegime.TRENDING_BULLISH.value


# ── decide() without params (regime switching) ─────────────────
@patch("src.agents.orchestrator.classify_regime")
def test_decide_without_params_uses_regime_switching(mock_classify, orchestrator, mock_market_state):
    """When no params are passed, decide() delegates to get_signal (regime switching)."""
    mock_classify.return_value = MarketRegime.SIDEWAYS_RANGE

    with patch.object(orchestrator, "get_signal", return_value=None) as mock_gs:
        orchestrator.decide(mock_market_state)
        mock_gs.assert_called_once()


# ── get_signal() ────────────────────────────────────────────────
@patch("src.agents.orchestrator.classify_regime")
def test_get_signal_selects_correct_agent(mock_classify, orchestrator, mock_market_state):
    """get_signal must delegate to the agent mapped to the classified regime."""
    mock_classify.return_value = MarketRegime.TRENDING_BULLISH

    # Replace the mapped agent with a mock
    mock_agent = MagicMock()
    mock_agent.generate_signal.return_value = TradeSignal(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        entry_price=Decimal("50000"),
        stop_loss=Decimal("49000"),
        take_profit=Decimal("52000"),
        confidence=0.8,
        metadata={},
    )
    orchestrator.agents[MarketRegime.TRENDING_BULLISH] = mock_agent

    signal = orchestrator.get_signal(mock_market_state)

    mock_agent.generate_signal.assert_called_once_with(mock_market_state)
    assert signal is not None
    assert signal.metadata["agent"] == mock_agent.__class__.__name__


@patch("src.agents.orchestrator.classify_regime")
def test_get_signal_with_regime_override(mock_classify, orchestrator, mock_market_state):
    """regime_override skips classify_regime and uses the given regime directly."""
    # Should NOT be called because override is provided
    mock_classify.return_value = MarketRegime.SIDEWAYS_RANGE

    mock_agent = MagicMock()
    mock_agent.generate_signal.return_value = None
    orchestrator.agents[MarketRegime.HIGH_VOLATILITY] = mock_agent

    orchestrator.get_signal(mock_market_state, regime_override=MarketRegime.HIGH_VOLATILITY)

    mock_agent.generate_signal.assert_called_once_with(mock_market_state)
