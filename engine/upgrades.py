"""
Upgrade system.

Handles factory throughput/efficiency upgrades and auto-purchase unlocks.
"""

from __future__ import annotations

from engine import config
from engine.game_state import GameState


def calculate_upgrade_cost(current_level: int) -> float:
    """Cost to upgrade from current_level to current_level + 1."""
    next_level = current_level + 1
    return config.UPGRADE_BASE_COST * (config.UPGRADE_COST_MULTIPLIER ** (next_level - 1))


def upgrade_throughput(state: GameState, product_id: str) -> bool:
    """Upgrade factory throughput. Returns True if successful. Mutates state."""
    factory = state.factories[product_id]
    cost = calculate_upgrade_cost(factory.throughput_level)

    if state.cash < cost:
        return False

    state.cash -= cost
    factory.throughput_level += 1
    return True


def upgrade_efficiency(state: GameState, product_id: str) -> bool:
    """Upgrade factory efficiency. Returns True if successful. Mutates state."""
    factory = state.factories[product_id]
    cost = calculate_upgrade_cost(factory.efficiency_level)

    if state.cash < cost:
        return False

    state.cash -= cost
    factory.efficiency_level += 1
    return True


def unlock_auto_purchase(state: GameState, component_id: int) -> bool:
    """Unlock auto-purchase for a component. Returns True if successful. Mutates state."""
    if state.cash < config.AUTO_PURCHASE_UNLOCK_COST:
        return False

    comp = state.components[component_id]
    if comp.auto_purchase_unlocked:
        return False  # already unlocked

    state.cash -= config.AUTO_PURCHASE_UNLOCK_COST
    comp.auto_purchase_unlocked = True
    return True
