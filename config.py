"""
Configuration Module for Smart Electricity Usage and Bill Analyzer
Defines file paths, configurable tariff slabs, fixed charges, and analysis thresholds.
"""

import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
CHARTS_DIR = os.path.join(REPORTS_DIR, "charts")

# Ensure required directories exist
for folder in [DATA_DIR, LOGS_DIR, REPORTS_DIR, CHARTS_DIR]:
    os.makedirs(folder, exist_ok=True)

# File Paths
READINGS_CSV_PATH = os.path.join(DATA_DIR, "readings.csv")
ERROR_LOG_PATH = os.path.join(LOGS_DIR, "error_log.txt")
REPORT_TXT_PATH = os.path.join(REPORTS_DIR, "consumption_report.txt")

# Configurable Tariff Structure (Tiered / Slab Tariff)
# Represented as a list of immutable tuples: (min_units, max_units, rate_per_unit)
# Currency: Rs. (standard currency units)
CURRENCY = "Rs."

DEFAULT_TARIFF_SLABS = [
    (0, 100, 3.00),         # Slab 1: 0 to 100 units @ Rs. 3.00 / unit
    (101, 300, 4.50),       # Slab 2: 101 to 300 units @ Rs. 4.50 / unit
    (301, 500, 6.50),       # Slab 3: 301 to 500 units @ Rs. 6.50 / unit
    (501, float('inf'), 8.00) # Slab 4: Above 500 units @ Rs. 8.00 / unit
]

# Additional Charges
DEFAULT_FIXED_CHARGE = 50.00       # Fixed meter maintenance charge
DEFAULT_TAX_RATE = 0.05            # 5% electricity duty / tax

# Engineering Thresholds
DEFAULT_HIGH_USAGE_THRESHOLD = 250.0  # Units above which consumption is flagged as 'High'
