"""
Strategy Configuration Parameters
"""
import os
import logging
from datetime import datetime
    
# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Generate log filename with new convention
current_time = datetime.now()
log_filename = f"ST_Option_Selling_{current_time.hour:02d}_{current_time.minute:02d}_{current_time.day:02d}{current_time.month:02d}{current_time.year}.log"
log_path = os.path.join('logs', log_filename)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s - [Line: %(lineno)d] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)

STRATEGY_CONFIG = {
    'sl_multiplier': 1.5,
    'market_open_time': '09:15:00',
    'entry_time': '09:25:00',
    'exit_time': '15:15:00',
    'lot_size': 30
}

DATA_CONFIG = {
    'base_path': "APR_2022",
    'futures_pattern': "BANKNIFTY-I.NFO.csv",
    'options_pattern': r'BANKNIFTY\d{2}[A-Z]{3}\d{2}\d+(CE|PE)\.NFO\.csv$'
}

logger = logging.getLogger(__name__)
logger.info("Configuration loaded successfully. Log file: %s", log_path)