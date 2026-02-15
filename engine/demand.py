"""
Demand calculation engine.

Combines three layers:
  1. Price-quality elasticity:  a * exp(-b * price / quality^alpha)
  2. Seasonal modifier:         mean + amplitude * sin(2π/T * (month - phase))
  3. Market growth:             compounding annual growth with noise

Final demand = elasticity * (seasonal / seasonal_mean) * growth_factor
"""

from __future__ import annotations

import math
import numpy as np
from engine import config


def price_quality_demand(price: float, quality: float, params: dict) -> float:
    """Base demand from price-quality elasticity curve.

    From notebook: demand = a * exp(-b * P / Qlt^alpha)
    """
    a = params["a"]
    b = params["b"]
    alpha = params["alpha"]

    if quality <= 0:
        return 0.0
    return a * math.exp(-b * price / (quality ** alpha))


def seasonal_modifier(month: int, params: dict) -> float:
    """Seasonal demand multiplier based on sine wave.

    Returns a multiplier centered around 1.0 so it scales the base demand.
    month is 1-indexed (1 = January).
    """
    mean = params["seasonal_mean"]
    amplitude = params["seasonal_amplitude"]
    period = params["seasonal_period"]
    phase = params["seasonal_phase"]

    if mean == 0:
        return 1.0

    raw = mean + amplitude * math.sin(2 * math.pi / period * (month - phase))
    return raw / mean


def growth_factor(year: int, params: dict, rng: np.random.Generator | None = None) -> float:
    """Cumulative market growth multiplier for a given game year.

    Compounds annual_growth_rate with per-year random noise.
    Uses a seeded RNG for reproducibility within a game.
    """
    base_rate = 1 + params["annual_growth_rate"]
    noise_lo, noise_hi = params["growth_noise_range"]

    factor = 1.0
    for y in range(1, year + 1):
        if rng is not None:
            noise = rng.uniform(noise_lo, noise_hi)
        else:
            noise = 1.0  # deterministic fallback
        factor *= base_rate * noise

    return factor


def calculate_demand(
    product_id: str,
    price: float,
    quality: float,
    game_day: int,
    growth_factors: dict[str, float] | None = None,
) -> float:
    """Full demand calculation combining all three layers.

    Args:
        product_id: Which product ("A" through "E").
        price: Current selling price.
        quality: Current product quality level.
        game_day: Current game day (for calendar lookups).
        growth_factors: Pre-computed per-product growth factors for the current
                        year. If None, growth is treated as 1.0.

    Returns:
        Demand as a float (caller should floor to int for actual sales).
    """
    params = config.PRODUCT_DEMAND[product_id]

    # Layer 1: price-quality elasticity
    base = price_quality_demand(price, quality, params)

    # Layer 2: seasonal modifier
    month = (game_day // config.DAYS_PER_MONTH) % config.MONTHS_PER_YEAR + 1
    season = seasonal_modifier(month, params)

    # Layer 3: market growth
    gf = 1.0
    if growth_factors and product_id in growth_factors:
        gf = growth_factors[product_id]

    return base * season * gf
