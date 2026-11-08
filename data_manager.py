"""
Data Manager Module for Smart Electricity Usage and Bill Analyzer
Handles persistent storage of readings in CSV format, error logging in text format,
and engineering report generation. Demonstrates file handling and exception handling.
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Set
from config import READINGS_CSV_PATH, ERROR_LOG_PATH, REPORT_TXT_PATH, CURRENCY


def log_error(error_message: str, file_path: str = ERROR_LOG_PATH) -> None:
    """
    Append an error entry with a precise timestamp to a text log file.
    
    Parameters:
        error_message (str): Description of the error or invalid input.
        file_path (str): Target text file path for logs.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ERROR: {error_message}\n"
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Failed to write to error log: {e}")


def load_readings(file_path: str = READINGS_CSV_PATH) -> List[Dict[str, Any]]:
    """
    Read electricity meter records from a CSV file.
    Returns records as a list of dictionaries.
    
    Parameters:
        file_path (str): Path to CSV data file.
        
    Returns:
        list of dict: List containing all reading records.
    """
    if not os.path.exists(file_path):
        return []

    readings = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                record = {
                    "id": int(row["id"]),
                    "date": row["date"],
                    "prev_reading": float(row["prev_reading"]),
                    "curr_reading": float(row["curr_reading"]),
                    "units": float(row["units"]),
                    "bill_amount": float(row["bill_amount"]),
                    "status": row.get("status", "Normal")
                }
                readings.append(record)
    except Exception as e:
        log_error(f"Failed to read CSV file '{file_path}': {e}")
        print(f"Error loading readings: {e}")
        return []

    return readings


def save_reading(record: Dict[str, Any], file_path: str = READINGS_CSV_PATH) -> bool:
    """
    Append a new meter reading dictionary to the CSV file.
    
    Parameters:
        record (dict): Meter reading record.
        file_path (str): Target CSV file.
        
    Returns:
        bool: True if save succeeded, False otherwise.
    """
    file_exists = os.path.exists(file_path)
    fieldnames = ["id", "date", "prev_reading", "curr_reading", "units", "bill_amount", "status"]

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists or os.path.getsize(file_path) == 0:
                writer.writeheader()
            writer.writerow(record)
        return True
    except Exception as e:
        log_error(f"Failed to write record {record.get('id')} to '{file_path}': {e}")
        print(f"Error saving reading: {e}")
        return False


def seed_sample_data(file_path: str = READINGS_CSV_PATH, overwrite: bool = False) -> bool:
    """
    Pre-populate the CSV file with realistic household monthly meter readings
    (12 months across a full annual cycle) for immediate demonstration and visualization.
    
    Parameters:
        file_path (str): Target CSV file path.
        overwrite (bool): If True, replaces existing file.
        
    Returns:
        bool: True if seeded successfully.
    """
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0 and not overwrite:
        return False

    from tariff import calculate_bill

    sample_records = [
        {"id": 1, "date": "2025-01-31", "prev_reading": 1000.0, "curr_reading": 1180.0},
        {"id": 2, "date": "2025-02-28", "prev_reading": 1180.0, "curr_reading": 1375.0},
        {"id": 3, "date": "2025-03-31", "prev_reading": 1375.0, "curr_reading": 1610.0},
        {"id": 4, "date": "2025-04-30", "prev_reading": 1610.0, "curr_reading": 1920.0},  # Summer AC starts
        {"id": 5, "date": "2025-05-31", "prev_reading": 1920.0, "curr_reading": 2300.0},  # Peak Summer
        {"id": 6, "date": "2025-06-30", "prev_reading": 2300.0, "curr_reading": 2660.0},  # Peak Summer
        {"id": 7, "date": "2025-07-31", "prev_reading": 2660.0, "curr_reading": 2940.0},  # Monsoon
        {"id": 8, "date": "2025-08-31", "prev_reading": 2940.0, "curr_reading": 3195.0},
        {"id": 9, "date": "2025-09-30", "prev_reading": 3195.0, "curr_reading": 3435.0},
        {"id": 10, "date": "2025-10-31", "prev_reading": 3435.0, "curr_reading": 3660.0},
        {"id": 11, "date": "2025-11-30", "prev_reading": 3660.0, "curr_reading": 3870.0},
        {"id": 12, "date": "2025-12-31", "prev_reading": 3870.0, "curr_reading": 4120.0},
    ]

    fieldnames = ["id", "date", "prev_reading", "curr_reading", "units", "bill_amount", "status"]
    
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in sample_records:
                units = round(item["curr_reading"] - item["prev_reading"], 2)
                bill_info = calculate_bill(units)
                status = "High Usage" if units >= 250.0 else "Normal"
                
                row = {
                    "id": item["id"],
                    "date": item["date"],
                    "prev_reading": item["prev_reading"],
                    "curr_reading": item["curr_reading"],
                    "units": units,
                    "bill_amount": bill_info["total_bill"],
                    "status": status
                }
                writer.writerow(row)
        return True
    except Exception as e:
        log_error(f"Error seeding sample dataset: {e}")
        return False


def generate_consumption_report(
    readings: List[Dict[str, Any]],
    stats: Dict[str, Any],
    high_usage_set: Set[str],
    file_path: str = REPORT_TXT_PATH
) -> str:
    """
    Generate an engineering text report summarizing energy consumption,
    bill distributions, and high usage anomalies.
    
    Parameters:
        readings (list): List of all reading records.
        stats (dict): Statistical metrics computed from readings.
        high_usage_set (set): Set of dates with high consumption.
        file_path (str): Output text file destination.
        
    Returns:
        str: Report content.
    """
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "=" * 70
    sub_sep = "-" * 70

    lines = [
        separator,
        "   SMART ELECTRICITY USAGE AND BILL ANALYZER - ENGINEERING REPORT",
        f"   Generated on: {report_time}",
        separator,
        "",
        "1. EXECUTIVE SUMMARY & STATISTICAL METRICS",
        sub_sep,
        f" Total Billing Cycles Recorded : {stats.get('count', 0)}",
        f" Total Units Consumed (kWh)   : {stats.get('total_units', 0.0):.2f} kWh",
        f" Total Electricity Billed     : {CURRENCY} {stats.get('total_cost', 0.0):.2f}",
        f" Average Consumption per Period: {stats.get('avg_units', 0.0):.2f} kWh",
        f" Average Bill per Period      : {CURRENCY} {stats.get('avg_cost', 0.0):.2f}",
        f" Minimum Consumption          : {stats.get('min_units', 0.0):.2f} kWh ({stats.get('min_date', 'N/A')})",
        f" Maximum (Peak) Consumption   : {stats.get('max_units', 0.0):.2f} kWh ({stats.get('max_date', 'N/A')})",
        "",
        "2. HIGH CONSUMPTION PERIODS (EXCEEDING THRESHOLD)",
        sub_sep,
    ]

    if high_usage_set:
        lines.append(f" Total High-Usage Periods Detected: {len(high_usage_set)}")
        for date in sorted(high_usage_set):
            # Find the corresponding record
            matching = next((r for r in readings if r["date"] == date), None)
            if matching:
                lines.append(
                    f"   [!] Date: {date} | Units: {matching['units']} kWh | Bill: {CURRENCY} {matching['bill_amount']:.2f}"
                )
    else:
        lines.append("  No high energy consumption periods detected. Consumption is within normal limits.")

    lines.extend([
        "",
        "3. COMPLETE CONSUMPTION LOG TABLE",
        sub_sep,
        f"{'ID':<4} {'Date':<12} {'Prev (kWh)':<12} {'Curr (kWh)':<12} {'Units':<10} {'Bill (Rs)':<12} {'Status'}",
        sub_sep,
    ])

    for r in readings:
        lines.append(
            f"{r['id']:<4} {r['date']:<12} {r['prev_reading']:<12.1f} {r['curr_reading']:<12.1f} "
            f"{r['units']:<10.1f} {r['bill_amount']:<12.2f} {r['status']}"
        )

    lines.extend([
        sub_sep,
        "",
        "4. ENGINEERING RECOMMENDATIONS FOR ENERGY CONSERVATION",
        sub_sep,
        " * High consumption periods usually correlate with seasonal cooling/heating appliances.",
        " * Transitioning to BEE 5-Star rated appliances can reduce power load by up to 25%.",
        " * Shifting energy-intensive operations to off-peak slots prevents entering higher tariff slabs.",
        " * Future Scope: Interfacing IoT CT sensor modules for automated real-time meter telemetry.",
        separator
    ])

    report_text = "\n".join(lines)

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="w", encoding="utf-8") as f:
            f.write(report_text)
    except Exception as e:
        log_error(f"Failed to save consumption report: {e}")
        print(f"Error saving report: {e}")

    return report_text
