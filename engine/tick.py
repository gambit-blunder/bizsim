"""
Tick orchestrator.

Runs one game tick: production → sales → auto-purchase → advance clock.
Pure function — no threading, no Flask. The server layer calls this
on a timer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from engine.game_state import GameState
from engine.production import produce_all, ProductionResult
from engine.sales import sell_all, SaleResult
from engine.purchasing import auto_purchase_all, PurchaseResult
from engine import config

import numpy as np


@dataclass
class TickResult:
    """Summary of everything that happened in one tick."""
    game_day: int
    production: list[ProductionResult] = field(default_factory=list)
    sales: list[SaleResult] = field(default_factory=list)
    auto_purchases: list[PurchaseResult] = field(default_factory=list)
    total_revenue: float = 0.0
    total_units_sold: int = 0


def precompute_growth_factors(state: GameState, rng: np.random.Generator) -> dict[str, float]:
    """Compute per-product growth factors for the current year.

    Should be called once per year and cached, not every tick.
    """
    year = state.game_year
    factors = {}
    for product_id, params in config.PRODUCT_DEMAND.items():
        from engine.demand import growth_factor
        factors[product_id] = growth_factor(year, params, rng)
    return factors


def run_tick(
    state: GameState,
    growth_factors: dict[str, float] | None = None,
) -> TickResult:
    """Execute one game tick. Mutates state.

    Order matters:
      1. Produce (consume components → add to widget inventory)
      2. Sell (consume widget inventory → add to cash)
      3. Auto-purchase (consume cash → add to component inventory)
      4. Advance clock
    """
    result = TickResult(game_day=state.game_day)

    # 1. Production
    result.production = produce_all(state)

    # 2. Sales
    result.sales = sell_all(state, growth_factors)
    result.total_revenue = sum(s.revenue for s in result.sales)
    result.total_units_sold = sum(s.units_sold for s in result.sales)

    # 3. Auto-purchase
    result.auto_purchases = auto_purchase_all(state)

    # 4. Advance clock
    state.game_day += 1

    return result
