"""
Main Execution File for Options Strategy
"""
import logging
from config import STRATEGY_CONFIG, DATA_CONFIG, logger as config_logger
from data_utils import DataHandler
from strategy import OptionsStrategy
import numpy as np  

def main():
    try:
        config_logger.info("STARTING STRATEGY EXECUTION")
        config_logger.info("=" * 30 + "\n")

        data_handler = DataHandler(DATA_CONFIG)
        strategy = OptionsStrategy(STRATEGY_CONFIG)

        config_logger.info("Loading market data...")
        futures_data, options_data = data_handler.load_data()

        if not futures_data:
            config_logger.error("No futures data found! Exiting.")
            return

        total_days = len(futures_data)
        config_logger.info("\nStarting strategy execution for %d trading days", total_days)

        # Initialize metrics tracking
        daily_pnl = []
        cumulative_pnl = 0
        profitable_days = 0
        losing_days = 0
        max_drawdown = 0
        max_cumulative_pnl = 0
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        most_profitable_day = None
        most_loss_day = None
        total_trades = 0

        for i, futures_day in enumerate(sorted(futures_data, key=lambda x: x['date']), 1):
            config_logger.info("DAY %d/%d: Processing %s", i, total_days, futures_day['date'])
            config_logger.info("=" * 30)

            try:
                day_options = [op for op in options_data if op['date'] == futures_day['date']]
                trades = strategy.execute_strategy(futures_day, day_options)

                # Calculate daily P&L
                total_pnl = sum(trade.get('pnl', 0) for trade in trades)
                daily_pnl.append({'date': futures_day['date'], 'pnl': total_pnl})
                cumulative_pnl += total_pnl
                total_trades += len(trades)

                # Track profitable and losing days
                if total_pnl > 0:
                    profitable_days += 1
                    consecutive_wins += 1
                    consecutive_losses = 0
                    if consecutive_wins > max_consecutive_wins:
                        max_consecutive_wins = consecutive_wins
                elif total_pnl < 0:
                    losing_days += 1
                    consecutive_losses += 1
                    consecutive_wins = 0
                    if consecutive_losses > max_consecutive_losses:
                        max_consecutive_losses = consecutive_losses

                # Track max drawdown
                if cumulative_pnl > max_cumulative_pnl:
                    max_cumulative_pnl = cumulative_pnl
                drawdown = max_cumulative_pnl - cumulative_pnl
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

                # Track most profitable and most loss-making days
                if most_profitable_day is None or total_pnl > most_profitable_day['pnl']:
                    most_profitable_day = {'date': futures_day['date'], 'pnl': total_pnl}
                if most_loss_day is None or total_pnl < most_loss_day['pnl']:
                    most_loss_day = {'date': futures_day['date'], 'pnl': total_pnl}

                config_logger.info("\nDaily Summary:")
                config_logger.info("Trades Executed: %d", len(trades))
                config_logger.info("Total P&L: Rs%.2f", total_pnl)

            except Exception as e:
                config_logger.error("Error processing day: %s", str(e), exc_info=True)
                continue

        # Calculate additional metrics
        average_return = np.mean([day['pnl'] for day in daily_pnl])
        win_rate = (profitable_days / total_days) * 100 if total_days > 0 else 0
        profit_factor = (sum(day['pnl'] for day in daily_pnl if day['pnl'] > 0) /
                         abs(sum(day['pnl'] for day in daily_pnl if day['pnl'] < 0))) if losing_days > 0 else float('inf')
        sharpe_ratio = (average_return / np.std([day['pnl'] for day in daily_pnl])) if len(daily_pnl) > 1 else 0
        daily_volatility = np.std([day['pnl'] for day in daily_pnl])
        average_trade_pnl = cumulative_pnl / total_trades if total_trades > 0 else 0

        # Log final metrics
        config_logger.info("\nSTRATEGY EXECUTION COMPLETED")
        config_logger.info("=" * 30)
        config_logger.info("Final Metrics:")
        config_logger.info("Average Return: Rs%.2f", average_return)
        config_logger.info("Total Win Days: %d", profitable_days)
        config_logger.info("Total Loss Days: %d", losing_days)  
        config_logger.info("Win Rate: %.2f%%", win_rate)
        config_logger.info("Profit Factor: %.2f", profit_factor)
        config_logger.info("Sharpe Ratio: %.2f", sharpe_ratio)
        config_logger.info("Max Drawdown: Rs%.2f", max_drawdown)
        config_logger.info("Most Profitable Day: %s (Rs%.2f)", most_profitable_day['date'], most_profitable_day['pnl'])
        config_logger.info("Most Loss-Making Day: %s (Rs%.2f)", most_loss_day['date'], most_loss_day['pnl'])
        config_logger.info("Max Consecutive Wins: %d", max_consecutive_wins)
        config_logger.info("Max Consecutive Losses: %d", max_consecutive_losses)
        config_logger.info("Cumulative P&L: Rs%.2f", cumulative_pnl)
        config_logger.info("Daily Volatility: Rs%.2f", daily_volatility)
        config_logger.info("Average Trade P&L: Rs%.2f", average_trade_pnl)

    except Exception as e:
        config_logger.error("Fatal error: %s", str(e), exc_info=True)
        raise

if __name__ == "__main__":
    main()