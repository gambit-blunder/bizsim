"""
Flask application — thin web layer over the engine.

Handles:
  - Serving the UI
  - JSON API for AJAX polling (no more full-page refresh)
  - Player action routes (upgrades, purchases, price changes)
  - Background tick thread
"""

from __future__ import annotations

import threading
import time
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify

from engine.game_state import GameState
from engine.tick import run_tick, precompute_growth_factors
from engine.upgrades import upgrade_throughput, upgrade_efficiency, unlock_auto_purchase, calculate_upgrade_cost
from engine.purchasing import purchase_component
from engine.clock import format_date
from engine import config

app = Flask(__name__)

# ── Global game state ─────────────────────────────────────────────────────────
game = GameState.new_game()
rng = np.random.default_rng(42)
growth_factors: dict[str, float] = precompute_growth_factors(game, rng)
last_tick_result = None
tick_lock = threading.Lock()


def tick_loop():
    """Background thread that runs the game simulation."""
    global growth_factors, last_tick_result

    while True:
        with tick_lock:
            if game.game_over:
                break

            # Recompute growth factors at the start of each new year
            current_year = game.game_year
            result = run_tick(game, growth_factors)
            last_tick_result = result

            if game.game_year != current_year:
                growth_factors = precompute_growth_factors(game, rng)

        time.sleep(config.TICK_SECONDS)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    """JSON snapshot of the full game state for AJAX polling."""
    with tick_lock:
        products = {}
        for pid, prod in game.products.items():
            factory = game.factories[pid]
            products[pid] = {
                "price": round(prod.price, 2),
                "quality": round(prod.quality, 1),
                "inventory": prod.inventory,
                "throughput_level": factory.throughput_level,
                "efficiency_level": factory.efficiency_level,
                "capacity": factory.capacity,
                "efficiency_multiplier": round(factory.efficiency_multiplier, 4),
                "throughput_upgrade_cost": round(calculate_upgrade_cost(factory.throughput_level), 0),
                "efficiency_upgrade_cost": round(calculate_upgrade_cost(factory.efficiency_level), 0),
            }

            # Add last tick sales data if available
            if last_tick_result:
                for s in last_tick_result.sales:
                    if s.product_id == pid:
                        products[pid]["last_sold"] = s.units_sold
                        products[pid]["last_revenue"] = round(s.revenue, 2)
                        products[pid]["last_demand"] = round(s.demand, 1)
                        break

        components = {}
        for cid, comp in game.components.items():
            components[str(cid)] = {
                "price": comp.price,
                "inventory": round(comp.inventory, 1),
                "auto_purchase_unlocked": comp.auto_purchase_unlocked,
            }

        # Adjusted BOM for display
        bom_display = {}
        for pid in game.products:
            bom_display[pid] = {}
            eff = game.factories[pid].efficiency_multiplier
            for cid, base in config.BILL_OF_MATERIALS[pid].items():
                if base is not None:
                    bom_display[pid][str(cid)] = round(base * eff, 2)
                else:
                    bom_display[pid][str(cid)] = None

        return jsonify({
            "cash": round(game.cash, 2),
            "game_day": game.game_day,
            "game_date": format_date(game.game_day),
            "game_year": game.game_year,
            "game_month": game.game_month,
            "game_over": game.game_over,
            "products": products,
            "components": components,
            "bom": bom_display,
            "auto_purchase_unlock_cost": config.AUTO_PURCHASE_UNLOCK_COST,
        })


# ── Player actions ────────────────────────────────────────────────────────────

@app.route("/action/upgrade_throughput", methods=["POST"])
def action_upgrade_throughput():
    pid = request.form["product_id"]
    with tick_lock:
        upgrade_throughput(game, pid)
    return redirect(url_for("index"))


@app.route("/action/upgrade_efficiency", methods=["POST"])
def action_upgrade_efficiency():
    pid = request.form["product_id"]
    with tick_lock:
        upgrade_efficiency(game, pid)
    return redirect(url_for("index"))


@app.route("/action/set_price", methods=["POST"])
def action_set_price():
    pid = request.form["product_id"]
    new_price = float(request.form["price"])
    with tick_lock:
        game.products[pid].price = max(0.0, round(new_price, 2))
    return redirect(url_for("index"))


@app.route("/action/purchase_component", methods=["POST"])
def action_purchase_component():
    cid = int(request.form["component_id"])
    qty = int(request.form["quantity"])
    with tick_lock:
        purchase_component(game, cid, qty)
    return redirect(url_for("index"))


@app.route("/action/unlock_auto_purchase", methods=["POST"])
def action_unlock_auto_purchase():
    cid = int(request.form["component_id"])
    with tick_lock:
        unlock_auto_purchase(game, cid)
    return redirect(url_for("index"))


@app.route("/action/new_game", methods=["POST"])
def action_new_game():
    global game, rng, growth_factors, last_tick_result
    with tick_lock:
        game = GameState.new_game()
        rng = np.random.default_rng(42)
        growth_factors = precompute_growth_factors(game, rng)
        last_tick_result = None
    return redirect(url_for("index"))


# ── Start ─────────────────────────────────────────────────────────────────────

def start_app():
    tick_thread = threading.Thread(target=tick_loop, daemon=True)
    tick_thread.start()
    app.run(debug=False, port=5000)


if __name__ == "__main__":
    start_app()
