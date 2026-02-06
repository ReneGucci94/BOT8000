"""
Window generation para Walk-Forward Optimization.
Spec: Codex PARTE 2 - Función generate_windows()
"""
from dataclasses import dataclass
from typing import List
from datetime import datetime, timezone
from calendar import monthrange
from src.core.market import Candle


@dataclass
class WindowConfig:
    """
    Configuración de ventanas WFO.
    Spec: Codex PARTE 7.1
    """
    train_months: int      # Ej: 4
    test_months: int       # Ej: 1
    step_months: int       # Ej: 1
    year: int              # Ej: 2024
    warmup_bars: int       # Ej: 240 para 4H


@dataclass
class Window:
    """
    Una ventana de WFO con train/test/warmup data.
    Spec: Codex PARTE 2 - Window dataclass
    """
    window_id: int
    label: str
    
    train_start_month: int
    train_end_month: int
    test_start_month: int
    test_end_month: int
    
    train_data: List[Candle]
    test_data: List[Candle]
    warmup_data: List[Candle]


def generate_windows(
    full_data: List[Candle],
    config: WindowConfig
) -> List[Window]:
    """
    Genera ventanas de WFO según Codex PARTE 2.
    """
    if config.step_months != config.test_months:
        raise ValueError(
            f"step_months ({config.step_months}) debe == test_months ({config.test_months})"
        )
    
    if len(full_data) == 0:
        raise ValueError("full_data está vacío")

    windows = []
    
    # Rango de meses total para el año
    # El año tiene 12 meses.
    # Necesitamos calcular cuántas ventanas caben.
    # Empezamos en start_month = 1.
    # La última ventana debe terminar su TEST en o antes del mes 12.
    # Test end month = train_start + train_months + test_months - 1
    # Example 4+1: Start=1 -> Train=1..4, Test=5. End=5.
    # Max End = 12.
    # Solve for max Start: Start + train + test - 1 <= 12
    # Start <= 12 - train - test + 1
    
    max_start_month = 12 - config.train_months - config.test_months + 1
    
    for i in range(max_start_month):
        window_id = i
        
        # Calcular meses
        # Nota: start_month es 1-based para la lógica interna
        train_start_month = 1 + i * config.step_months
        train_end_month = train_start_month + config.train_months - 1
        
        test_start_month = train_end_month + 1
        test_end_month = test_start_month + config.test_months - 1
        
        # Labels
        # Format: Train:YYYY-MMtoYYYY-MM_Test:YYYY-MM
        # Helper para formato 02d
        def fmt_m(m): return f"{config.year}-{m:02d}"
        
        label = (
            f"Train:{fmt_m(train_start_month)}to{fmt_m(train_end_month)}_"
            f"Test:{fmt_m(test_start_month)}"
            # Nota: Si test_months > 1, el label podría necesitar ajuste, 
            # pero el spec dice "Test:YYYY-MM" para el bloque. 
            # Asumimos que si test > 1, indicamos el rango o solo el inicio?
            # El spec ejemplo es "Test:YYYY-MM". Si es 1 mes, es obvio.
            # Si son más, mejor poner rango o seguir convención. 
            # Codex 7.2 ejemplos son de 1 mes. 
            # Para test_months > 1, la spec es ambigua en el label exacto, 
            # pero el formato dado es fijo. Nos adherimos al formato del test:
            # "Test:YYYY-MM" (probablemente start chart).
            # Revisando el test `test_window_labels_correct` que escribí, 
            # espera solo el mes de inicio si es 1 mes.
        )
        # Si test dura un mes, start==end.
        
        # Slice Train Data
        train_data = _slice_candles_by_month(
            full_data, config.year, train_start_month, train_end_month
        )
        
        # Slice Test Data
        test_data = _slice_candles_by_month(
            full_data, config.year, test_start_month, test_end_month
        )
        
        if not train_data:
             # Puede pasar si no hay datos para esos meses
             # Si es estricto, raise error. Si es flexible, warn.
             # Codex no especifica comportamiento ante data missing, 
             # pero WFO sin data no sirve.
             # Asumimos que full_data cubre todo el año.
             pass
        
        # Warmup Data
        # Se toma relativo al primer candle del test set (para asegurar continuidad inmediata)
        # O relativo al primer candle del trai set?
        # Spec 4.1: "warmup_bars = 240 prior to the Test window start (or Train start?)"
        # Corrección en el log: "warmup data validada vs test start".
        # PERO, un sistema real entrena con indicadores ya calientes. 
        # Asi que el Train Set necesita warmup. 
        # Y el Test Set necesita warmup (que es el final del Train Set).
        # El objeto `warmup_data` en el dataclass Window suele ser "datos anteriores al Train" 
        # para que el primer candle de Train ya tenga RSi, etc.
        # SIN EMBARGO, el test `test_warmup_exactly_240_bars` verifica `win.warmup_data`.
        # Si la red neuronal entrena con features, necesita features desde la vela 0 de Train.
        # Por ende, warmup debe ser PRE-TRAIN.
        #
        # Re-reading Spec Note in `specification.md`:
        # "Warmup... prior to the Test window start (or Train start? ... Correction ... win.warmup_data checks vs Test Start)"
        # Espera, si el test checkea `win.warmup_data[-1].timestamp < win.test_data[0].timestamp`, 
        # eso es trivial si warmup es pre-train.
        #
        # Vamos a asumir Warmup es PRE-TRAIN, porque es lo necesario para entrenar.
        # Si fuera Pre-Test, sería train_data.
        #
        # Wait, el test: `assert win.warmup_data[-1].timestamp < win.test_data[0].timestamp`
        # Eso se cumple tanto si es Pre-Train como si es Pre-Test (pero overlapping Train).
        #
        # El standard de backtesting es:
        # Full Stream: [Warmup][Train][Test] -> No, Train incluye features.
        # Entonces: [Warmup para Train][Train] ... luego Test usa final de Train como warmup.
        # El Window object explícitamente tiene `warmup_data`.
        # Si usamos `_get_warmup_candles` con `train_data[0].timestamp`, obtenemos 240 velas antes de Train.
        # Esto permite calcular indicadores para el primer punto de Train. OK.
        
        if train_data:
            train_start_ts = train_data[0].timestamp
            warmup_data = _get_warmup_candles(full_data, train_start_ts, config.warmup_bars)
        else:
            warmup_data = []

        # Crear Ventana
        win = Window(
            window_id=window_id,
            label=label,
            train_start_month=train_start_month,
            train_end_month=train_end_month,
            test_start_month=test_start_month,
            test_end_month=test_end_month,
            train_data=train_data,
            test_data=test_data,
            warmup_data=warmup_data
        )
        windows.append(win)
        
    return windows


def _slice_candles_by_month(
    candles: List[Candle],
    year: int,
    start_month: int,
    end_month: int
) -> List[Candle]:
    """
    Helper: extrae candles de meses específicos.
    """
    if not candles:
        return []
        
    # Calcular timestamps límite
    # Start: día 1 del start_month a las 00:00:00
    # End: último día del end_month a las 23:59:59.999...
    
    start_dt = datetime(year, start_month, 1, 0, 0, 0, tzinfo=timezone.utc)
    start_ts = int(start_dt.timestamp() * 1000)
    
    last_day = monthrange(year, end_month)[1]
    end_dt = datetime(year, end_month, last_day, 23, 59, 59, 999999, tzinfo=timezone.utc)
    end_ts = int(end_dt.timestamp() * 1000)
    
    # Filtrado eficiente (asumiendo ordenados, pero O(N) es aceptable para configs típicas)
    # Optimización: binary search si fuera muy grande, pero linear scan ok aquí.
    
    result = []
    for c in candles:
        if c.timestamp >= start_ts and c.timestamp <= end_ts:
            result.append(c)
        elif c.timestamp > end_ts:
            # Si asumimos orden, podemos romper early
            break
            
    return result


def _get_warmup_candles(
    candles: List[Candle],
    reference_ts: int,
    warmup_bars: int
) -> List[Candle]:
    """
    Helper: extrae últimas N velas antes de reference_ts (exclusivo).
    """
    # Recolectar candidatos
    candidates = []
    for c in candles:
        if c.timestamp < reference_ts:
            candidates.append(c)
        else:
            # Asumiendo orden, alcanzamos el target
            break
            
    if len(candidates) < warmup_bars:
        # No hay suficiente data histórica para el warmup
        # Dependiendo de la severidad, retornamos lo que hay o vacío o error.
        # Para consistencia estricta:
        # raise ValueError(f"Insufficient warmup data: required {warmup_bars}, got {len(candidates)}")
        # Pero mejor retornamos candidates y dejamos que el validador decida,
        # O seguimos el test que espera len == 240.
        return candidates # El test fallará si len != 240, que es correcto.
        
    return candidates[-warmup_bars:]
