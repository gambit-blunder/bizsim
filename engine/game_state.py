"""
Single source of truth for all mutable game state.

Replaces the scattered global dicts (balances, factory_state, business,
flows_state, features_unlocked) from the prototype. All mutation goes
through methods on this class so the engine stays testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from engine import config


@dataclass
class FactoryState:
    throughput_level: int = 0
    efficiency_level: int = 0
    paused: bool = False

    @property
    def capacity(self) -> int:
        """Units produced per tick at current throughput level."""
        return self.throughput_level * config.CAPACITY_PER_THROUGHPUT_LEVEL

    @property
    def efficiency_multiplier(self) -> float:
        """Component usage multiplier (lower = less waste)."""
        return (1 - config.EFFICIENCY_REDUCTION_PER_LEVEL) ** self.efficiency_level


@dataclass
class ProductState:
    price: float = 0.0
    quality: float = 1.0
    inventory: int = 0


@dataclass
class ComponentState:
    price: float = 1.0
    inventory: float = 0.0
    auto_purchase_unlocked: bool = False
    auto_purchase_quantity: int = 100       # units per auto-buy
    auto_purchase_max_inventory: int = 1000 # reorder when below this level


@dataclass
class GameState:
    """Complete snapshot of the game at any point in time."""

    cash: float = 0.0
    game_day: int = 0  # days elapsed since game start

    factories: dict[str, FactoryState] = field(default_factory=dict)
    products: dict[str, ProductState] = field(default_factory=dict)
    components: dict[int, ComponentState] = field(default_factory=dict)

    @classmethod
    def new_game(cls) -> GameState:
        """Create a fresh game state from config defaults."""
        state = cls(cash=config.STARTING_CASH)

        for product_id, price in config.PRODUCT_STARTING_PRICES.items():
            state.factories[product_id] = FactoryState()
            state.products[product_id] = ProductState(
                price=price,
                quality=config.PRODUCT_STARTING_QUALITY[product_id],
            )

        for comp_id, price in config.COMPONENT_PRICES.items():
            state.components[comp_id] = ComponentState(price=price)

        return state

    # ── Convenience accessors ─────────────────────────────────────────────

    @property
    def game_month(self) -> int:
        """Current month (1-12) in the game calendar."""
        return (self.game_day // config.DAYS_PER_MONTH) % config.MONTHS_PER_YEAR + 1

    @property
    def game_year(self) -> int:
        """Current year (1-based) in the game calendar."""
        return self.game_day // (config.DAYS_PER_MONTH * config.MONTHS_PER_YEAR) + 1

    @property
    def months_elapsed(self) -> int:
        """Total months since game start (for seasonal calculations)."""
        return self.game_day // config.DAYS_PER_MONTH

    @property
    def game_over(self) -> bool:
        """Whether the game has reached its time limit."""
        return self.game_year > config.GAME_YEARS
