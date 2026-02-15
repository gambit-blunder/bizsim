"""
Sales engine.

Each tick, sell min(inventory, demand) units at the current price.
"""

from __future__ import annotations

from dataclasses import dataclass
from engine.game_state import GameState
from engine.demand import calculate_demand


@dataclass
class SaleResult:
    product_id: str
    units_sold: int
    revenue: float
    demand: float           # what the market wanted
    unmet_demand: float     # demand we couldn't fill (future: out-of-stock penalty)


def sell(
    state: GameState,
    product_id: str,
    growth_factors: dict[str, float] | None = None,
) -> SaleResult:
    """Sell product into the market for one tick. Mutates state."""
    product = state.products[product_id]

    demand = calculate_demand(
        product_id=product_id,
        price=product.price,
        quality=product.quality,
        game_day=state.game_day,
        growth_factors=growth_factors,
    )

    units_sold = min(product.inventory, int(demand))
    revenue = units_sold * product.price

    product.inventory -= units_sold
    state.cash += revenue

    unmet = max(0.0, demand - units_sold)

    return SaleResult(product_id, units_sold, revenue, demand, unmet)


def sell_all(
    state: GameState,
    growth_factors: dict[str, float] | None = None,
) -> list[SaleResult]:
    """Run sales for all products. Mutates state."""
    results = []
    for product_id in state.products:
        results.append(sell(state, product_id, growth_factors))
    return results
