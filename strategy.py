"""
Option SELL Strategy:
Sell ATM CALL / PUT at 09:25 AM and square off at 03:15 PM.
"""

import logging
import pandas as pd
from datetime import datetime

class OptionsStrategy:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('strategy')
        self.active_trades = []

    def execute_strategy(self, futures_day, options_data):
        """
        Executes the strategy for a given day and options data.
        Returns a list of trades with their P&L.
        """
        self.logger.info("Executing simple SELL CALL PUT strategy")
        entry_time = self.config['entry_time']
        exit_time = self.config['exit_time']
        lot_size = self.config['lot_size']
        date = futures_day['date']
        market_open_time = self.config['market_open_time']

        self.logger.info("Date: %s", date)

        # Step 1: Determine ATM strike from Futures LTP at entry time
        futures_df = futures_day['data']

        entry_row = futures_df[futures_df['Time'] == entry_time]
        market_open_row = futures_df[futures_df['Time'] == market_open_time]

        # Handle missing data by searching for the closest time
        for i in range(1, 60):
            entry_time = f"09:25:{i:02d}"
            market_open_time = f"09:15:{i:02d}"

            entry_row = futures_df[futures_df['Time'] == entry_time]
            market_open_row = futures_df[futures_df['Time'] == market_open_time]

            if not entry_row.empty and not market_open_row.empty:
                entry_time = '09:25:00'
                market_open_time = '09:15:00'
                break

        if entry_row.empty:
            self.logger.warning("Entry time %s not found in futures data", '09:25:00')
            return []

        if market_open_row.empty:
            self.logger.warning("Market open time not found in futures data")
            return []

        future_ltp_925 = entry_row.iloc[0]['LTP']
        future_ltp_915 = market_open_row.iloc[0]['LTP']

        # Compare LTP at 9:25 with LTP at 9:15
        option_type = 'CE' if future_ltp_925 < future_ltp_915 else 'PE'

        atm_strike = round(future_ltp_925 / 100) * 100
        self.logger.info("ATM Strike determined: %d (Future LTP: %.2f)", atm_strike, future_ltp_925)
        self.logger.info("Selected Option Type: %s", option_type)

        # Step 2: Find corresponding option contract
        option_df = None
        for opt in options_data:
            if opt['option_type'] == option_type and opt['strike'] == atm_strike:
                option_df = opt['data']
                break

        if option_df is None:
            self.logger.warning("No option data found for %d strike %s", atm_strike, option_type)
            return []

        # Step 3: Entry price at 09:25
        entry_option_row = option_df[option_df['Time'] == entry_time]

        for i in range(1, 60):
            entry_time = f"09:25:{i:02d}"
            entry_option_row = option_df[option_df['Time'] == entry_time]

            if not entry_option_row.empty:
                entry_time = '09:25:00'
                break

        if entry_option_row.empty:
            self.logger.warning("Entry time %s not found in option data", entry_time)
            return []

        entry_price = entry_option_row.iloc[0]['LTP']

        # Step 4: Exit price at 15:15
        exit_option_row = option_df[option_df['Time'] == exit_time]

        for i in range(1, 60):
            exit_time = f"15:15:{i:02d}"
            exit_option_row = option_df[option_df['Time'] == exit_time]

            if not exit_option_row.empty:
                exit_time = '15:15:00'
                break

        if exit_option_row.empty:
            self.logger.warning("Exit time %s not found in option data", exit_time)
            return []

        exit_price = exit_option_row.iloc[0]['LTP']

        # Step 5: P&L calculation
        pnl_per_lot = entry_price - exit_price
        total_pnl = pnl_per_lot * lot_size

        self.logger.info("-" * 50)
        self.logger.info("TRADE LOG")
        self.logger.info("Strike Price      : %d %s", atm_strike, option_type)
        self.logger.info("Entry Time        : %s", '9:25')
        self.logger.info("Entry Price       : Rs%.2f", entry_price)
        self.logger.info("Exit Time         : %s", '15:15')
        self.logger.info("Exit Price        : Rs%.2f", exit_price)
        self.logger.info("P&L per Qty       : Rs%.2f", pnl_per_lot)
        self.logger.info("Lot Size          : %d", lot_size)
        self.logger.info("Total P&L (1 lot) : Rs%.2f", total_pnl)
        self.logger.info("-" * 50)

        # Save trade summary
        trade_summary = {
            'date': date,
            'strike': atm_strike,
            'option_type': option_type,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl': total_pnl
        }
        self.active_trades.append(trade_summary)

        return [trade_summary]