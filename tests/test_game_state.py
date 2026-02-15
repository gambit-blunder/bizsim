"""Smoke tests for GameState and config wiring."""

from engine.game_state import GameState, FactoryState
from engine import config


def test_new_game_creates_all_products():
    state = GameState.new_game()
    assert set(state.products.keys()) == {"A", "B", "C", "D", "E"}
    assert set(state.factories.keys()) == {"A", "B", "C", "D", "E"}


def test_new_game_creates_all_components():
    state = GameState.new_game()
    assert set(state.components.keys()) == {1, 2, 3, 4, 5}


def test_starting_cash():
    state = GameState.new_game()
    assert state.cash == config.STARTING_CASH


def test_factory_capacity_scales_with_throughput():
    f = FactoryState(throughput_level=3)
    assert f.capacity == 3 * config.CAPACITY_PER_THROUGHPUT_LEVEL


def test_factory_efficiency_multiplier():
    f = FactoryState(efficiency_level=0)
    assert f.efficiency_multiplier == 1.0

    f = FactoryState(efficiency_level=1)
    assert f.efficiency_multiplier == 0.8  # 20% reduction

    f = FactoryState(efficiency_level=2)
    assert abs(f.efficiency_multiplier - 0.64) < 1e-9


def test_game_calendar():
    state = GameState.new_game()
    assert state.game_year == 1
    assert state.game_month == 1
    assert state.game_day == 0

    # Advance one month (30 days)
    state.game_day = 30
    assert state.game_month == 2
    assert state.game_year == 1

    # Advance one year (360 days)
    state.game_day = 360
    assert state.game_year == 2
    assert state.game_month == 1


def test_game_over():
    state = GameState.new_game()
    assert not state.game_over

    # Last day of year 10
    state.game_day = 10 * 12 * 30 - 1
    assert not state.game_over

    # First day of year 11
    state.game_day = 10 * 12 * 30
    assert state.game_over
