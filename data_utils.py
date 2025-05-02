"""
Data Handling Utilities
"""
import os
import re
import logging
import pandas as pd
from datetime import datetime
from glob import glob

class DataHandler:
    """Handles all data loading and processing operations"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('DataHandler')
        self.logger.info("Initializing DataHandler with config: %s", config)
    
    def load_data(self):
        """Load all data files from base directory"""
        self.logger.info("Starting data loading process from: %s", self.config['base_path'])
        futures, options = [], []

        # Filter date folders for the specific date
        date_folders = self._find_date_folders()
        #specific_date = '01042022'
        #date_folders = [folder for folder in date_folders if specific_date in folder]

        if not date_folders:
            self.logger.warning("No data folder found for the dates")
            return futures, options

        self.logger.info("Found %d date folder(s) to process.", len(date_folders))

        for date_folder in sorted(date_folders):
            date_str = self._extract_date_from_path(date_folder)
            self.logger.info("Processing date: %s", date_str)

            futures_data = self._load_futures_data(date_folder, date_str)
            if futures_data:
                futures.append(futures_data)

            date_options = self._load_options_data(date_folder, date_str)
            options.extend(date_options)
            self.logger.info("Loaded %d options contracts", len(date_options))

        self.logger.info("\nData loading completed. Total: %d futures, %d options",
                     len(futures), len(options))
        return futures, options
    

    def _find_date_folders(self):
        """Find all date folders in base directory"""
        path = os.path.join(self.config['base_path'], 'GFDLNFO_TICK_*')
        self.logger.debug("Looking for date folders at: %s", path)
        return glob(path)

    def _load_futures_data(self, date_folder, date_str):
        """Load futures data for specific date"""
        futures_path = os.path.join(
            date_folder,
            os.path.basename(date_folder),
            'Futures',
            '-I',
            self.config['futures_pattern']
        )

        self.logger.debug("Looking for futures data at: %s", futures_path)

        if os.path.exists(futures_path):
            try:
                df = pd.read_csv(futures_path)
                self.logger.info("Successfully loaded futures data for %s", date_str)
                return {
                    'date': date_str,
                    'path': futures_path,
                    'data': df,
                    'type': 'futures'
                }
            except Exception as e:
                self.logger.error("Error loading futures %s: %s", date_str, str(e), exc_info=True)
        else:
            self.logger.warning("Futures file not found at: %s", futures_path)
        return None

    def _load_options_data(self, date_folder, date_str):
        """Load all options data for specific date"""
        options_path = os.path.join(
            date_folder,
            os.path.basename(date_folder),
            'Options'
        )

        options_files = []
        if os.path.exists(options_path):
            self.logger.debug("Processing options directory: %s", options_path)
            for root, _, files in os.walk(options_path):
                for file in files:
                    if re.match(self.config['options_pattern'], file, re.IGNORECASE):
                        try:
                            expiry = self._extract_expiry(file)
                            # Filter for expiry 28APR22
                            if expiry != "28APR22":
                                continue
                            
                            file_path = os.path.join(root, file)
                            df = pd.read_csv(file_path)
                            options_files.append({
                                'date': date_str,
                                'path': file_path,
                                'data': df,
                                'type': 'options',
                                'strike': self._extract_strike(file),
                                'option_type': self._extract_option_type(file),
                                'expiry': expiry
                            })
                            self.logger.debug("Loaded options contract: %s", file)
                        except Exception as e:
                            self.logger.error("Error loading options %s: %s", file, str(e), exc_info=True)
        else:
            self.logger.warning("Options directory not found at: %s", options_path)
        return options_files

    @staticmethod
    def _extract_date_from_path(path):
        """Extract date from folder path"""
        return os.path.basename(path).replace('GFDLNFO_TICK_', '')

    @staticmethod
    def _extract_expiry(filename):
        """Extract expiry date from filename"""
        match = re.search(r'BANKNIFTY(\d{2}[A-Z]{3}\d{2})', filename, re.IGNORECASE)
        return match.group(1) if match else None
    
    @staticmethod
    def _extract_strike(filename):
        """Extract strike price from filename"""
        match = re.search(r'BANKNIFTY\d{2}[A-Z]{3}\d{2}(\d+)(CE|PE)', filename, re.IGNORECASE)
        return int(match.group(1)) if match else None

    @staticmethod
    def _extract_option_type(filename):
        """Extract option type (CE/PE) from filename"""
        match = re.search(r'BANKNIFTY\d{2}[A-Z]{3}\d{2}\d+(CE|PE)', filename, re.IGNORECASE)
        return match.group(1).upper() if match else None