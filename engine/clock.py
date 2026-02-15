"""
Game clock — maps real time to in-game calendar.

The tick loop lives in the server layer (threading). This module only
provides calendar math so the engine stays pure and testable.
"""

from engine import config


def day_to_month(game_day: int) -> int:
    """Return current month (1-12) for a given game day."""
    return (game_day // config.DAYS_PER_MONTH) % config.MONTHS_PER_YEAR + 1


def day_to_year(game_day: int) -> int:
    """Return current year (1-based) for a given game day."""
    return game_day // (config.DAYS_PER_MONTH * config.MONTHS_PER_YEAR) + 1


def day_to_months_elapsed(game_day: int) -> int:
    """Total months since game start (used for seasonal sine input)."""
    return game_day // config.DAYS_PER_MONTH


def total_game_days() -> int:
    """Total days in a full game."""
    return config.GAME_YEARS * config.MONTHS_PER_YEAR * config.DAYS_PER_MONTH


def format_date(game_day: int) -> str:
    """Human-readable date string like 'Year 2, Month 5, Day 14'."""
    year = day_to_year(game_day)
    month = day_to_month(game_day)
    day_in_month = (game_day % config.DAYS_PER_MONTH) + 1
    return f"Year {year}, Month {month}, Day {day_in_month}"
