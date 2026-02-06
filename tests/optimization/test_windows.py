"""
Tests para window generation según Codex spec PARTE 2.
Usamos las clases existentes de src.core.market (Candle).
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from src.core.market import Candle
from src.optimization.windows import (
    generate_windows,
    WindowConfig,
    Window
)


def test_window_count_4_plus_1_step_1():
    """
    Para 2024 con config 4+1 step 1, debe generar exactamente 8 ventanas.
    Spec: Codex PARTE 7.2
    """
    # Arrange
    config = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    
    candles = generate_mock_candles_2024_4h()
    
    # Act
    windows = generate_windows(candles, config)
    
    # Assert
    assert len(windows) == 8, "Config 4+1 step 1 debe generar 8 ventanas"
    
    # Verificar primera ventana (Train Jan-Apr, Test May)
    assert windows[0].train_start_month == 1
    assert windows[0].train_end_month == 4
    assert windows[0].test_start_month == 5
    assert windows[0].test_end_month == 5
    
    # Verificar última ventana (Train Aug-Nov, Test Dec)
    assert windows[7].train_start_month == 8
    assert windows[7].train_end_month == 11
    assert windows[7].test_start_month == 12
    assert windows[7].test_end_month == 12


def test_train_test_separation():
    """
    No debe haber leakage: max(train_ts) < min(test_ts).
    Spec: Codex PARTE 9 - test_train_test_separation
    """
    config = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    candles = generate_mock_candles_2024_4h()
    windows = generate_windows(candles, config)
    
    for win in windows:
        # Última vela de train < Primera vela de test
        assert win.train_data[-1].timestamp < win.test_data[0].timestamp, \
            f"Window {win.window_id}: train/test overlap detected"
        
        # Última vela de warmup < Primera vela de test
        if len(win.warmup_data) > 0:
            assert win.warmup_data[-1].timestamp < win.test_data[0].timestamp, \
                f"Window {win.window_id}: warmup/test overlap detected"


def test_warmup_exactly_240_bars():
    """
    Cada ventana debe tener exactamente 240 velas de warmup.
    Spec: Codex PARTE 4.1 - warmup_bars = 240 para 4H
    """
    config = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    candles = generate_mock_candles_2024_4h()
    windows = generate_windows(candles, config)
    
    for win in windows:
        assert len(win.warmup_data) == 240, \
            f"Window {win.window_id} tiene {len(win.warmup_data)} warmup bars, esperado 240"


def test_no_overlap_between_test_windows():
    """
    Test windows no deben solaparse (step_months = test_months).
    Spec: Codex PARTE 2 - generate_windows constraint
    """
    config = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    candles = generate_mock_candles_2024_4h()
    windows = generate_windows(candles, config)
    
    for i in range(len(windows) - 1):
        win_current = windows[i]
        win_next = windows[i + 1]
        
        # Último timestamp test actual < Primer timestamp test siguiente
        last_ts_current = win_current.test_data[-1].timestamp
        first_ts_next = win_next.test_data[0].timestamp
        
        assert last_ts_current < first_ts_next, \
            f"Test overlap entre window {i} y {i+1}"


def test_window_labels_correct():
    """
    Labels deben seguir formato: Train:YYYY-MMtoYYYY-MM_Test:YYYY-MM
    Spec: Codex PARTE 2 - Window dataclass
    """
    config = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    candles = generate_mock_candles_2024_4h()
    windows = generate_windows(candles, config)
    
    expected_labels = [
        "Train:2024-01to2024-04_Test:2024-05",
        "Train:2024-02to2024-05_Test:2024-06",
        "Train:2024-03to2024-06_Test:2024-07",
        "Train:2024-04to2024-07_Test:2024-08",
        "Train:2024-05to2024-08_Test:2024-09",
        "Train:2024-06to2024-09_Test:2024-10",
        "Train:2024-07to2024-10_Test:2024-11",
        "Train:2024-08to2024-11_Test:2024-12",
    ]
    
    for i, win in enumerate(windows):
        assert win.label == expected_labels[i], \
            f"Window {i} label incorrecto: {win.label}"


def test_train_data_not_empty():
    """
    Train data de cada ventana debe contener candles.
    """
    config = WindowConfig(
        train_months=4,
        test_months=1,
        step_months=1,
        year=2024,
        warmup_bars=240
    )
    candles = generate_mock_candles_2024_4h()
    windows = generate_windows(candles, config)
    
    for win in windows:
        assert len(win.train_data) > 0, \
            f"Window {win.window_id} train_data está vacío"
        assert len(win.test_data) > 0, \
            f"Window {win.window_id} test_data está vacío"


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTION
# ═══════════════════════════════════════════════════════════

def generate_mock_candles_2024_4h():
    """
    Genera candles mock de 4H para todo 2024 + warmup previo.
    
    Warmup: 240 velas 4H antes de 2024-01-01
    240 velas * 4 horas = 960 horas = 40 días
    Start: 2023-11-22 00:00 UTC
    End: 2024-12-31 23:59 UTC
    
    Returns:
        List[Candle] ordenados por timestamp
    """
    # Inicio: 40 días antes de 2024-01-01
    start_ts = int(datetime(2023, 11, 22, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
    
    # Fin: último día de 2024
    end_ts = int(datetime(2024, 12, 31, 23, 59, tzinfo=timezone.utc).timestamp() * 1000)
    
    candles = []
    ts = start_ts
    interval_ms = 4 * 60 * 60 * 1000  # 4 horas en milisegundos
    
    price = Decimal("45000")  # Precio inicial
    
    while ts <= end_ts:
        # Crear candle simple con variación
        candles.append(Candle(
            timestamp=ts,
            open=price,
            high=price * Decimal("1.005"),
            low=price * Decimal("0.995"),
            close=price + Decimal("50"),  # Pequeño drift
            volume=Decimal("100.0"),
            timeframe="4h",
            complete=True
        ))
        
        ts += interval_ms
        price = price + Decimal("50")  # Trend simple para tests
        
        # Ocasional volatilidad para tests
        if len(candles) % 100 == 0:
            price = price * Decimal("0.98")  # Small dip
    
    return candles
