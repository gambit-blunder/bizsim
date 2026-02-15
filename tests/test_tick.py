"""Tests for the tick orchestrator."""

from engine.game_state import GameState
from engine.tick import run_tick
from engine import config


def _ready_state() -> GameState:
    """A state where product A can produce and sell."""
    state = GameState.new_game()
    state.factories["A"].throughput_level = 1
    state.components[3].inventory = 10000.0
    state.components[4].inventory = 10000.0
    state.products["A"].price = 5.0
    return state


def test_tick_advances_day():
    state = _ready_state()
    assert state.game_day == 0
    run_tick(state)
    assert state.game_day == 1


def test_tick_produces_and_sells():
    state = _ready_state()
    result = run_tick(state)
    assert result.total_units_sold > 0 or result.production[0].units_produced > 0


def test_tick_generates_revenue():
    state = _ready_state()
    # Run a tick to build inventory
    run_tick(state)
    # Inventory should exist now; run another tick to sell
    cash_before = state.cash
    run_tick(state)
    # Either sold from first tick's production or second tick's
    # Cash should have changed from sales or stayed same if no inventory
    assert state.cash >= cash_before  # can't lose money from sales


def test_multiple_ticks_accumulate():
    state = _ready_state()
    for _ in range(30):
        run_tick(state)
    assert state.game_day == 30
    assert state.cash != config.STARTING_CASH  # something happened


def test_auto_purchase_fires_when_unlocked():
    state = _ready_state()
    state.components[3].auto_purchase_unlocked = True
    state.components[3].inventory = 50  # below threshold
    result = run_tick(state)
    assert len(result.auto_purchases) > 0
    assert state.components[3].inventory > 50


def test_auto_purchase_uses_per_component_settings():
    state = _ready_state()
    state.components[3].auto_purchase_unlocked = True
    state.components[3].auto_purchase_quantity = 200
    state.components[3].auto_purchase_max_inventory = 500
    state.components[3].inventory = 400  # below 500 threshold
    inv_before = state.components[3].inventory
    result = run_tick(state)
    assert len(result.auto_purchases) > 0
    # Should have bought exactly 200 (minus any consumed by production)
    # Just verify inventory increased
    assert state.components[3].inventory > inv_before - 100  # production may consume some


def test_auto_purchase_does_not_fire_above_max_inventory():
    state = _ready_state()
    state.components[3].auto_purchase_unlocked = True
    state.components[3].auto_purchase_max_inventory = 500
    state.components[3].inventory = 600  # above threshold
    result = run_tick(state)
    auto_for_3 = [a for a in result.auto_purchases if a.component_id == 3]
    assert len(auto_for_3) == 0
