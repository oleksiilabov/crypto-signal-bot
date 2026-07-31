"""
Core Application Entry Point.
Main orchestrator scanning asset universe and routing notifications.
"""

import logging
import sys
from config import ASSETS_TO_SCAN, StrategyConfig, TelegramConfig
from data_fetcher import DataFetcher
from strategy import EMABreakoutStrategy
from risk import RiskEngine
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("QuantScanner")


def run_scanner() -> None:
    """Executes market scanner pipeline across configured asset registry."""
    logger.info("Initializing Quant Scanner Run Cycle...")

    strategy_config = StrategyConfig()
    telegram_config = TelegramConfig()

    fetcher = DataFetcher()
    strategy = EMABreakoutStrategy(config=strategy_config)
    notifier = TelegramNotifier(config=telegram_config)

    for symbol, meta in ASSETS_TO_SCAN.items():
        asset_name = meta["name"]
        asset_type = meta["type"]
        platform = meta["platform"]

        try:
           df_15m = fetcher.fetch_ohlcv(
                symbol=symbol,
                period=strategy_config.lookback_period,
                interval=strategy_config.interval
            )
            df_4h = fetcher.fetch_ohlcv(
                symbol=symbol,
                period="60d",
                interval="4h"
            )

            if df_15m.empty:
                continue

            signal = strategy.analyze(df_15m, df_4h)
            if not signal:
                logger.debug(f"No signal detected for pair: {asset_name}")
                continue

            logger.info(f"SIGNAL TRIGGERED: {asset_name} ({signal.direction})")

            risk_params = RiskEngine.calculate_trade_levels(
                asset_type=asset_type,
                asset_name=asset_name,
                direction=signal.direction,
                entry_price=signal.entry_price,
                recent_extreme=signal.recent_extreme,
                risk_reward_ratio=strategy_config.risk_reward_ratio
            )

            notifier.send_signal_alert(
                asset_name=asset_name,
                asset_type=asset_type,
                platform=platform,
                direction=signal.direction,
                risk_params=risk_params,
                volume_ratio=signal.volume_ratio
            )

        except Exception as err:
            logger.error(f"Unexpected error processing symbol {symbol}: {err}", exc_info=True)

    logger.info("Scanner Run Cycle complete.")


if __name__ == "__main__":
    run_scanner()
