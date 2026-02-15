"""
Component purchasing engine.

Manual purchases and auto-purchase (threshold-based reordering).
"""

from __future__ import annotations

from dataclasses import dataclass
from engine import config
from engine.game_state import GameState


@dataclass
class PurchaseResult:
    component_id: int
    quantity: int
    total_cost: float
    success: bool
    reason: str = ""  # "ok", "insufficient_funds"


def purchase_component(state: GameState, component_id: int, quantity: int) -> PurchaseResult:
    """Buy components manually. Mutates state."""
    comp = state.components[component_id]
    total_cost = comp.price * quantity

    if state.cash < total_cost:
        return PurchaseResult(component_id, 0, 0.0, False, "insufficient_funds")

    state.cash -= total_cost
    comp.inventory += quantity
    return PurchaseResult(component_id, quantity, total_cost, True, "ok")


def auto_purchase_all(state: GameState) -> list[PurchaseResult]:
    """Run auto-purchase for all unlocked components. Mutates state."""
    results = []
    for comp_id, comp in state.components.items():
        if not comp.auto_purchase_unlocked:
            continue
        if comp.inventory < comp.auto_purchase_max_inventory:
            result = purchase_component(state, comp_id, comp.auto_purchase_quantity)
            results.append(result)
    return results
