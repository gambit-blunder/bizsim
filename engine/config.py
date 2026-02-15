"""
All game tuning parameters in one place.

Every magic number lives here — demand curves, costs, BOM, seasonal patterns,
growth rates, upgrade scaling. Change this file to rebalance the game.
"""

# ── Game Clock ────────────────────────────────────────────────────────────────
TICK_SECONDS = 1                    # Real-time seconds per game day
DAYS_PER_MONTH = 30                 # Simplified calendar
MONTHS_PER_YEAR = 12
GAME_YEARS = 10                     # Default game length

# ── Starting Conditions ──────────────────────────────────────────────────────
STARTING_CASH = 10_000

# ── Components ───────────────────────────────────────────────────────────────
# component_id -> base price per unit
COMPONENT_PRICES = {
    1: 1.0,
    2: 1.0,
    3: 1.0,
    4: 1.0,
    5: 1.0,
}

# ── Bill of Materials ────────────────────────────────────────────────────────
# product_id -> { component_id: units_required | None }
BILL_OF_MATERIALS = {
    "A": {1: None, 2: None, 3: 2.1, 4: 2.9, 5: None},
    "B": {1: None, 2: None, 3: None, 4: 1.7, 5: 2.2},
    "C": {1: None, 2: 1.5, 3: None, 4: None, 5: 2.5},
    "D": {1: 2.5, 2: 2.9, 3: None, 4: None, 5: 1.4},
    "E": {1: None, 2: 2.9, 3: 2.5, 4: 1.9, 5: 1.7},
}

# ── Demand Curve Parameters ──────────────────────────────────────────────────
# From your notebook: demand = a * exp(-b * P / Qlt^alpha)
# Then multiplied by seasonal_modifier * growth_modifier * noise
#
# Seasonal archetypes (phase_shift controls peak timing):
#   Fall/Winter peak  -> phase_shift ≈ 6.5  (peaks ~November)
#   Spring/Summer     -> phase_shift ≈ 0.5  (peaks ~May)
#   Summer-only       -> phase_shift ≈ 3.0  (peaks ~July)
#   Spring + Fall     -> use double-sine (handled in demand module)
#   CPG flat          -> amplitude ≈ 0      (no seasonality)

PRODUCT_DEMAND = {
    "A": {
        # Price-quality elasticity
        "a": 100,           # Max demand at price 0
        "b": 0.5,           # Price decay rate
        "alpha": 2.0,       # Quality exponent (higher = quality matters more)

        # Seasonal pattern (sine wave)
        "seasonal_mean": 150,
        "seasonal_amplitude": 50,
        "seasonal_period": 18,      # months for full cycle
        "seasonal_phase": 6.5,      # Fall/Winter peak

        # Market growth
        "annual_growth_rate": 0.10,         # 10% base annual growth
        "growth_noise_range": (0.9, 1.1),   # random annual multiplier
    },
    "B": {
        "a": 100,
        "b": 0.5,
        "alpha": 2.0,

        "seasonal_mean": 150,
        "seasonal_amplitude": 50,
        "seasonal_period": 18,
        "seasonal_phase": 0.5,      # Spring/Summer peak

        "annual_growth_rate": 0.12,
        "growth_noise_range": (0.9, 1.1),
    },
    "C": {
        "a": 100,
        "b": 0.5,
        "alpha": 2.0,

        "seasonal_mean": 150,
        "seasonal_amplitude": 50,
        "seasonal_period": 18,
        "seasonal_phase": 3.0,      # Summer peak

        "annual_growth_rate": 0.08,
        "growth_noise_range": (0.9, 1.1),
    },
    "D": {
        "a": 100,
        "b": 0.5,
        "alpha": 2.0,

        "seasonal_mean": 150,
        "seasonal_amplitude": 10,   # CPG — nearly flat seasonality
        "seasonal_period": 18,
        "seasonal_phase": 0.0,

        "annual_growth_rate": 0.15,
        "growth_noise_range": (0.9, 1.1),
    },
    "E": {
        "a": 100,
        "b": 0.5,
        "alpha": 2.0,

        "seasonal_mean": 150,
        "seasonal_amplitude": 40,
        "seasonal_period": 12,      # 12-month period for double-peak
        "seasonal_phase": 3.0,      # Spring + Fall archetype

        "annual_growth_rate": 0.20,
        "growth_noise_range": (0.9, 1.1),
    },
}

# ── Product Starting Prices ──────────────────────────────────────────────────
PRODUCT_STARTING_PRICES = {
    "A": 10.0,
    "B": 5.0,
    "C": 5.0,
    "D": 5.0,
    "E": 5.0,
}

# ── Product Starting Quality ─────────────────────────────────────────────────
PRODUCT_STARTING_QUALITY = {
    "A": 1.0,
    "B": 1.0,
    "C": 1.0,
    "D": 1.0,
    "E": 1.0,
}

# ── Factory Upgrades ─────────────────────────────────────────────────────────
UPGRADE_BASE_COST = 1_000           # Cost for level 1
UPGRADE_COST_MULTIPLIER = 1.5       # Each level costs 50% more
CAPACITY_PER_THROUGHPUT_LEVEL = 10  # Units/tick per throughput level
EFFICIENCY_REDUCTION_PER_LEVEL = 0.20  # 20% component savings per level

# ── Auto-Purchase ────────────────────────────────────────────────────────────
AUTO_PURCHASE_UNLOCK_COST = 2_000
AUTO_PURCHASE_THRESHOLD = 1_000     # Reorder point
AUTO_PURCHASE_QUANTITY = 100        # Units per auto-buy
