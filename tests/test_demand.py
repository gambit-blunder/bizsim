"""Tests for the demand engine."""

import math
from engine.demand import price_quality_demand, seasonal_modifier, growth_factor, calculate_demand
from engine import config


def test_demand_decreases_with_price():
    params = config.PRODUCT_DEMAND["A"]
    d_low = price_quality_demand(2.0, 1.0, params)
    d_high = price_quality_demand(8.0, 1.0, params)
    assert d_low > d_high


def test_demand_increases_with_quality():
    params = config.PRODUCT_DEMAND["A"]
    d_low_q = price_quality_demand(5.0, 1.0, params)
    d_high_q = price_quality_demand(5.0, 5.0, params)
    assert d_high_q > d_low_q


def test_demand_at_zero_quality_is_zero():
    params = config.PRODUCT_DEMAND["A"]
    assert price_quality_demand(5.0, 0.0, params) == 0.0


def test_seasonal_modifier_averages_around_one():
    params = config.PRODUCT_DEMAND["A"]
    modifiers = [seasonal_modifier(m, params) for m in range(1, 13)]
    avg = sum(modifiers) / len(modifiers)
    assert abs(avg - 1.0) < 0.15  # should be close to 1.0


def test_seasonal_flat_for_low_amplitude():
    params = config.PRODUCT_DEMAND["D"]  # CPG, amplitude=10
    modifiers = [seasonal_modifier(m, params) for m in range(1, 13)]
    spread = max(modifiers) - min(modifiers)
    assert spread < 0.2  # should be nearly flat


def test_growth_factor_increases_over_years():
    params = config.PRODUCT_DEMAND["A"]
    import numpy as np
    rng = np.random.default_rng(42)
    g1 = growth_factor(1, params, rng)

    rng = np.random.default_rng(42)
    g5 = growth_factor(5, params, rng)

    assert g5 > g1


def test_calculate_demand_returns_positive():
    d = calculate_demand("A", 5.0, 1.0, 0)
    assert d > 0
