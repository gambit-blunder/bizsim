"""Tests for the production engine."""

from engine.game_state import GameState
from engine.production import produce, produce_all, calculate_max_producible
from engine import config


def _setup_state() -> GameState:
    """Create a game state with factory A at throughput 1 and enough components."""
    state = GameState.new_game()
    state.factories["A"].throughput_level = 1
    # Widget A needs: comp 3 (2.1), comp 4 (2.9)
    state.components[3].inventory = 1000.0
    state.components[4].inventory = 1000.0
    return state


def test_produce_creates_whole_units():
    state = _setup_state()
    result = produce(state, "A")
    assert result.units_produced == config.CAPACITY_PER_THROUGHPUT_LEVEL
    assert isinstance(result.units_produced, int)


def test_produce_consumes_components():
    state = _setup_state()
    comp3_before = state.components[3].inventory
    comp4_before = state.components[4].inventory
    result = produce(state, "A")

    assert state.components[3].inventory < comp3_before
    assert state.components[4].inventory < comp4_before
    assert result.components_consumed[3] > 0
    assert result.components_consumed[4] > 0


def test_produce_adds_to_inventory():
    state = _setup_state()
    result = produce(state, "A")
    assert state.products["A"].inventory == result.units_produced


def test_produce_nothing_without_factory():
    state = GameState.new_game()  # all throughput = 0
    result = produce(state, "A")
    assert result.units_produced == 0
    assert result.limited_by == "no_factory"


def test_produce_limited_by_components():
    state = _setup_state()
    state.components[3].inventory = 1.0  # barely any
    max_units, limiter = calculate_max_producible(state, "A")
    assert max_units < config.CAPACITY_PER_THROUGHPUT_LEVEL
    assert "component_3" in limiter


def test_efficiency_reduces_component_usage():
    state = _setup_state()
    state.factories["A"].efficiency_level = 2
    state.components[3].inventory = 1000.0
    state.components[4].inventory = 1000.0

    comp3_before = state.components[3].inventory
    produce(state, "A")
    used = comp3_before - state.components[3].inventory

    # With efficiency 2: multiplier = 0.64, base = 2.1, capacity = 10
    # used should be 2.1 * 0.64 * 10 = 13.44
    expected = 2.1 * (0.8 ** 2) * 10
    assert abs(used - expected) < 0.01


def test_produce_nothing_when_paused():
    state = _setup_state()
    state.factories["A"].paused = True
    result = produce(state, "A")
    assert result.units_produced == 0
    assert result.limited_by == "paused"


def test_produce_resumes_after_unpause():
    state = _setup_state()
    state.factories["A"].paused = True
    produce(state, "A")
    state.factories["A"].paused = False
    result = produce(state, "A")
    assert result.units_produced > 0
