"""
Production engine.

Determines how many widgets each factory produces per tick, consuming
components from inventory. Produces whole units only — no fractional widgets.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from engine import config
from engine.game_state import GameState


@dataclass
class ProductionResult:
    """What happened during one tick of production for one product."""
    product_id: str
    units_produced: int
    components_consumed: dict[int, float]  # component_id -> amount used
    limited_by: str | None = None  # None, "no_factory", or "component_{id}"


def calculate_max_producible(state: GameState, product_id: str) -> tuple[int, str | None]:
    """How many units can be produced given current component inventory.

    Returns (max_units, limiting_factor).
    """
    factory = state.factories[product_id]
    if factory.throughput_level == 0:
        return 0, "no_factory"

    capacity = factory.capacity
    bom = config.BILL_OF_MATERIALS[product_id]
    eff = factory.efficiency_multiplier

    max_units = capacity  # start with factory capacity as ceiling
    limiter = None

    for comp_id, base_units in bom.items():
        if base_units is None:
            continue
        units_per_widget = base_units * eff
        available = state.components[comp_id].inventory
        can_make = int(available / units_per_widget) if units_per_widget > 0 else capacity
        if can_make < max_units:
            max_units = can_make
            limiter = f"component_{comp_id}"

    return max_units, limiter


def produce(state: GameState, product_id: str) -> ProductionResult:
    """Produce widgets for one product, consuming components. Mutates state."""
    factory = state.factories[product_id]
    if factory.throughput_level == 0:
        return ProductionResult(product_id, 0, {}, "no_factory")
    if factory.paused:
        return ProductionResult(product_id, 0, {}, "paused")

    max_units, limiter = calculate_max_producible(state, product_id)
    units = max_units  # produce as many as possible up to capacity

    if units <= 0:
        return ProductionResult(product_id, 0, {}, limiter)

    # Consume components
    bom = config.BILL_OF_MATERIALS[product_id]
    eff = factory.efficiency_multiplier
    consumed = {}

    for comp_id, base_units in bom.items():
        if base_units is None:
            continue
        amount = base_units * eff * units
        state.components[comp_id].inventory -= amount
        consumed[comp_id] = amount

    # Add to product inventory
    state.products[product_id].inventory += units

    return ProductionResult(product_id, units, consumed, limiter)


def produce_all(state: GameState) -> list[ProductionResult]:
    """Run production for all products. Mutates state."""
    results = []
    for product_id in state.factories:
        results.append(produce(state, product_id))
    return results
