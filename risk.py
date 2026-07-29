"""
Risk Management Engine.
Calculates Stop-Loss, Take-Profit, and Pip scaling parameters.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeParameters:
    """Structured container for risk metrics and execution orders."""
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    decimals: int
    sl_pips: float = 0.0
    tp_pips: float = 0.0


class RiskEngine:
    """Calculates risk levels based on market parameters."""

    @staticmethod
    def calculate_trade_levels(
        asset_type: str,
        asset_name: str,
        direction: str,
        entry_price: float,
        recent_extreme: float,
        risk_reward_ratio: float = 2.0
    ) -> TradeParameters:
        """Computes Stop-Loss and Take-Profit bounds."""
        if asset_type == "FOREX":
            pip_factor = 0.01 if "JPY" in asset_name else 0.0001
            decimals = 3 if "JPY" in asset_name else 5

            if direction == "LONG":
                sl_pips = max(round((entry_price - recent_extreme) / pip_factor, 1), 10.0)
                tp_pips = round(sl_pips * risk_reward_ratio, 1)
                stop_loss = round(entry_price - (sl_pips * pip_factor), decimals)
                take_profit = round(entry_price + (tp_pips * pip_factor), decimals)
            else:  # SHORT
                sl_pips = max(round((recent_extreme - entry_price) / pip_factor, 1), 10.0)
                tp_pips = round(sl_pips * risk_reward_ratio, 1)
                stop_loss = round(entry_price + (sl_pips * pip_factor), decimals)
                take_profit = round(entry_price - (tp_pips * pip_factor), decimals)

            return TradeParameters(
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=risk_reward_ratio,
                decimals=decimals,
                sl_pips=sl_pips,
                tp_pips=tp_pips
            )

        else:  # CRYPTO
            decimals = 2 if entry_price > 10 else 4
            stop_loss = round(recent_extreme, decimals)

            if direction == "LONG":
                risk = entry_price - stop_loss
                take_profit = round(entry_price + (risk * risk_reward_ratio), decimals)
            else:  # SHORT
                risk = stop_loss - entry_price
                take_profit = round(entry_price - (risk * risk_reward_ratio), decimals)

            return TradeParameters(
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=risk_reward_ratio,
                decimals=decimals
            )
