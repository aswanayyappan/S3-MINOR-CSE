"""
===============================================================================
SMART ELECTRICITY USAGE AND BILL ANALYZER
===============================================================================
Course: Programming Foundations for Engineers (25MNCST309) - Regulation 2025
Category: Project-Based Learning (PBL)

A comprehensive, self-contained Python engineering project designed to monitor,
calculate, and analyze household electricity consumption.

Syllabus Coverage:
  - Unit 1: Variables, operators, conditionals (if-elif-else), loops (while/for),
            robust input validation, and exception handling (try-except).
  - Unit 2: User-defined functions, parameters, return values, variable scope,
            standard libraries (csv, os, sys, datetime, typing).
  - Unit 3: Data structures: Lists, Tuples, Dictionaries, Sets.
            File handling: CSV data storage, error logging, engineering reports.
  - Unit 4: Data visualization using Matplotlib (Line charts, Bar charts, Scatter plots).
            Git & GitHub version control integration.
===============================================================================
"""

import os
import sys
import csv
from datetime import datetime
from typing import List, Tuple, Dict, Set, Any

# Ensure terminal stdout/stderr handles UTF-8 gracefully across all platforms (Windows safe)
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import matplotlib.pyplot as plt


# =============================================================================
# SECTION 1: CONFIGURATION & CONSTANTS
# =============================================================================

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
CHARTS_DIR = os.path.join(REPORTS_DIR, "charts")

# Ensure all application directories exist
for folder in [DATA_DIR, LOGS_DIR, REPORTS_DIR, CHARTS_DIR]:
    os.makedirs(folder, exist_ok=True)

# Target file paths
READINGS_CSV_PATH = os.path.join(DATA_DIR, "readings.csv")
ERROR_LOG_PATH = os.path.join(LOGS_DIR, "error_log.txt")
REPORT_TXT_PATH = os.path.join(REPORTS_DIR, "consumption_report.txt")

# Currency standard
CURRENCY = "Rs."

# Configurable Progressive Tariff Slabs
# Represented as a list of immutable tuples: (min_units, max_units, rate_per_unit)
DEFAULT_TARIFF_SLABS: List[Tuple[float, float, float]] = [
    (0, 100, 3.00),           # Slab 1: 0 to 100 units @ Rs. 3.00 / unit
    (101, 300, 4.50),         # Slab 2: 101 to 300 units @ Rs. 4.50 / unit
    (301, 500, 6.50),         # Slab 3: 301 to 500 units @ Rs. 6.50 / unit
    (501, float('inf'), 8.00) # Slab 4: Above 500 units @ Rs. 8.00 / unit
]

# Fixed Charges & Electricity Tax Rate
DEFAULT_FIXED_CHARGE = 50.00       # Fixed meter maintenance charge (Rs.)
DEFAULT_TAX_RATE = 0.05            # 5% regulatory electricity duty
DEFAULT_HIGH_USAGE_THRESHOLD = 250.0  # Threshold in kWh for high-consumption detection


# =============================================================================
# SECTION 2: TARIFF ENGINE & ENGINEERING COMPUTATION (Units 1 & 2)
# =============================================================================

def calculate_units_consumed(previous_reading: float, current_reading: float) -> float:
    """
    Calculate units consumed between two meter readings.
    Formula: Units (kWh) = Current Reading - Previous Reading
    
    Validation:
      - Readings cannot be negative numbers.
      - Current reading cannot be less than previous reading.
    """
    if previous_reading < 0 or current_reading < 0:
        raise ValueError("Meter readings cannot be negative.")
    if current_reading < previous_reading:
        raise ValueError(f"Current reading ({current_reading}) is less than previous reading ({previous_reading}).")
    
    return round(current_reading - previous_reading, 2)


def calculate_bill(
    units: float,
    tariff_slabs: List[Tuple[float, float, float]] = None,
    fixed_charge: float = None,
    tax_rate: float = None
) -> Dict[str, Any]:
    """
    Compute progressive electricity bill using tiered slab structure.
    
    Engineering Formulas:
      - Energy Charges = Sum(units_in_slab * slab_rate)
      - Subtotal = Energy Charges + Fixed Monthly Charge
      - Tax Amount = Subtotal * Tax Rate
      - Total Bill Amount = Subtotal + Tax Amount
    """
    if units < 0:
        raise ValueError("Units consumed cannot be negative.")
        
    if tariff_slabs is None:
        tariff_slabs = DEFAULT_TARIFF_SLABS
    if fixed_charge is None:
        fixed_charge = DEFAULT_FIXED_CHARGE
    if tax_rate is None:
        tax_rate = DEFAULT_TAX_RATE

    units_remaining = units
    energy_charge_total = 0.0
    slab_breakdown: List[Tuple[str, float, float, float]] = []

    for slab_min, slab_max, rate in tariff_slabs:
        if units_remaining <= 0:
            break
            
        slab_capacity = slab_max - slab_min + (1 if slab_min > 0 else 0)
        
        if units > slab_min:
            units_in_slab = min(units_remaining, slab_capacity)
        else:
            units_in_slab = 0.0
            
        if units_in_slab > 0:
            cost = units_in_slab * rate
            energy_charge_total += cost
            units_remaining -= units_in_slab
            
            slab_label = f"{int(slab_min)}-{int(slab_max) if slab_max != float('inf') else 'Above'}"
            slab_breakdown.append((slab_label, round(units_in_slab, 2), rate, round(cost, 2)))

    subtotal = energy_charge_total + fixed_charge
    tax_amount = subtotal * tax_rate
    total_bill = subtotal + tax_amount

    return {
        "units": round(units, 2),
        "slab_breakdown": slab_breakdown,
        "energy_charges": round(energy_charge_total, 2),
        "fixed_charge": round(fixed_charge, 2),
        "subtotal": round(subtotal, 2),
        "tax_rate_percent": round(tax_rate * 100, 1),
        "tax_amount": round(tax_amount, 2),
        "total_bill": round(total_bill, 2)
    }


def format_bill_summary(bill: Dict[str, Any]) -> str:
    """Format bill dictionary into a clean printable receipt."""
    lines = [
        "--------------------------------------------------",
        "           ELECTRICITY BILL ESTIMATE              ",
        "--------------------------------------------------",
        f" Total Units Consumed : {bill['units']} kWh",
        "--------------------------------------------------",
        " Slab Tier Breakdown:",
    ]
    for slab_label, units, rate, cost in bill["slab_breakdown"]:
        lines.append(f"   * Slab ({slab_label} units) : {units:6.2f} kWh @ {CURRENCY} {rate:4.2f}/unit = {CURRENCY} {cost:7.2f}")
        
    lines.extend([
        "--------------------------------------------------",
        f" Energy Charges       : {CURRENCY} {bill['energy_charges']:.2f}",
        f" Fixed Monthly Charge : {CURRENCY} {bill['fixed_charge']:.2f}",
        f" Subtotal             : {CURRENCY} {bill['subtotal']:.2f}",
        f" Electricity Tax ({bill['tax_rate_percent']}%) : {CURRENCY} {bill['tax_amount']:.2f}",
        "==================================================",
        f" TOTAL AMOUNT PAYABLE : {CURRENCY} {bill['total_bill']:.2f}",
        "=================================================="
    ])
    return "\n".join(lines)


# =============================================================================
# SECTION 3: FILE HANDLING & ERROR LOGGING (Unit 3)
# =============================================================================

def log_error(error_message: str, file_path: str = ERROR_LOG_PATH) -> None:
    """Log errors with precise timestamp to a text log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] ERROR: {error_message}\n"
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"Warning: Failed to write error log: {e}")


def load_readings(file_path: str = READINGS_CSV_PATH) -> List[Dict[str, Any]]:
    """Read meter records from a persistent CSV file into a list of dictionaries."""
    if not os.path.exists(file_path):
        return []

    readings = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                readings.append({
                    "id": int(row["id"]),
                    "date": row["date"],
                    "prev_reading": float(row["prev_reading"]),
                    "curr_reading": float(row["curr_reading"]),
                    "units": float(row["units"]),
                    "bill_amount": float(row["bill_amount"]),
                    "status": row.get("status", "Normal")
                })
    except Exception as e:
        log_error(f"Failed to read CSV '{file_path}': {e}")
        print(f"Error loading readings: {e}")
        return []

    return readings


def save_reading(record: Dict[str, Any], file_path: str = READINGS_CSV_PATH) -> bool:
    """Append a new meter reading dictionary record to CSV file."""
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
        log_error(f"Failed to save record: {e}")
        print(f"Error saving reading: {e}")
        return False


def seed_sample_data(file_path: str = READINGS_CSV_PATH, overwrite: bool = False) -> bool:
    """
    Seed 12 months of realistic household electricity consumption data
    reflecting seasonal variations (higher AC load in summer).
    """
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0 and not overwrite:
        return False

    sample_inputs = [
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
            for item in sample_inputs:
                units = round(item["curr_reading"] - item["prev_reading"], 2)
                bill_info = calculate_bill(units)
                status = "High Usage" if units >= DEFAULT_HIGH_USAGE_THRESHOLD else "Normal"
                writer.writerow({
                    "id": item["id"],
                    "date": item["date"],
                    "prev_reading": item["prev_reading"],
                    "curr_reading": item["curr_reading"],
                    "units": units,
                    "bill_amount": bill_info["total_bill"],
                    "status": status
                })
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
    """Generate and write a comprehensive engineering consumption report to a text file."""
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
            matching = next((r for r in readings if r["date"] == date), None)
            if matching:
                lines.append(f"   [!] Date: {date} | Units: {matching['units']} kWh | Bill: {CURRENCY} {matching['bill_amount']:.2f}")
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
        " * High consumption periods correlate strongly with seasonal cooling/heating loads.",
        " * Adopting BEE 5-Star rated appliances can decrease household energy consumption by 20-30%.",
        " * Balancing high-wattage equipment usage avoids stepping into higher progressive tariff tiers.",
        " * Future Scope: Interfacing IoT CT sensors (e.g. SCT-013) for automatic real-time meter readings.",
        separator
    ])

    report_text = "\n".join(lines)
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, mode="w", encoding="utf-8") as f:
            f.write(report_text)
    except Exception as e:
        log_error(f"Failed to save consumption report: {e}")

    return report_text


# =============================================================================
# SECTION 4: DATA STRUCTURES & ANALYTICS (Unit 3: Lists, Tuples, Dicts, Sets)
# =============================================================================

def compute_statistics(readings: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Tuple[float, float, float]]:
    """
    Process meter readings using Python data structures:
      - LISTS: Numerical series comprehension
      - DICTIONARY: Labeled metrics summary
      - TUPLE: Immutable summary representation
    """
    if not readings:
        empty_stats = {
            "count": 0, "total_units": 0.0, "avg_units": 0.0,
            "min_units": 0.0, "max_units": 0.0, "min_date": "N/A",
            "max_date": "N/A", "total_cost": 0.0, "avg_cost": 0.0
        }
        return empty_stats, (0.0, 0.0, 0.0)

    # 1. Lists for data processing
    units_list: List[float] = [r["units"] for r in readings]
    costs_list: List[float] = [r["bill_amount"] for r in readings]
    dates_list: List[str] = [r["date"] for r in readings]

    total_units = sum(units_list)
    total_cost = sum(costs_list)
    count = len(readings)

    avg_units = round(total_units / count, 2)
    avg_cost = round(total_cost / count, 2)

    min_units = min(units_list)
    max_units = max(units_list)

    min_date = dates_list[units_list.index(min_units)]
    max_date = dates_list[units_list.index(max_units)]

    # 2. Dictionary for labeled summary
    stats_dict: Dict[str, Any] = {
        "count": count,
        "total_units": round(total_units, 2),
        "avg_units": avg_units,
        "min_units": round(min_units, 2),
        "max_units": round(max_units, 2),
        "min_date": min_date,
        "max_date": max_date,
        "total_cost": round(total_cost, 2),
        "avg_cost": avg_cost
    }

    # 3. Tuple for immutable summary
    summary_tuple: Tuple[float, float, float] = (
        round(total_units, 2),
        round(total_cost, 2),
        avg_units
    )

    return stats_dict, summary_tuple


def identify_high_consumption_periods(
    readings: List[Dict[str, Any]],
    threshold: float = DEFAULT_HIGH_USAGE_THRESHOLD
) -> Set[str]:
    """
    Identify periods exceeding the consumption threshold using Python SETS.
    Guarantees unique date membership.
    """
    # 4. Set Comprehension
    high_consumption_dates: Set[str] = {
        r["date"] for r in readings if r["units"] >= threshold
    }
    return high_consumption_dates


def analyze_seasonal_patterns(readings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Demonstrate SET OPERATIONS (Union, Difference, Intersection) for seasonal peak analysis."""
    all_periods: Set[str] = {r["date"] for r in readings}
    high_periods: Set[str] = identify_high_consumption_periods(readings)
    normal_periods: Set[str] = all_periods.difference(high_periods)

    # Summer period set (April, May, June)
    summer_periods: Set[str] = {
        r["date"] for r in readings if any(r["date"].startswith(f"2025-0{m}") for m in ["4", "5", "6"])
    }

    # Set Intersection: High-usage periods occurring during summer
    summer_peaks: Set[str] = high_periods.intersection(summer_periods)

    return {
        "all_periods": all_periods,
        "high_usage_periods": high_periods,
        "normal_usage_periods": normal_periods,
        "summer_periods": summer_periods,
        "summer_high_peaks": summer_peaks
    }


# =============================================================================
# SECTION 5: DATA VISUALIZATION (Unit 4: Matplotlib Line, Bar, Scatter)
# =============================================================================

def plot_consumption_trend(readings: List[Dict[str, Any]], save_path: str = None, show: bool = True) -> str:
    """Generate a Line Chart of consumption trends over time with average benchmark line."""
    if not readings:
        print("No readings available to plot consumption trend.")
        return ""

    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "line_chart_trend.png")

    dates = [r["date"] for r in readings]
    units = [r["units"] for r in readings]
    avg_units = sum(units) / len(units)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, units, marker='o', color='#1f77b4', linewidth=2.5, label='Units Consumed (kWh)')
    ax.axhline(avg_units, color='red', linestyle='--', linewidth=1.8, label=f'Average Usage ({avg_units:.1f} kWh)')

    # Annotate peak usage point
    max_units = max(units)
    max_idx = units.index(max_units)
    ax.annotate(
        f'Peak: {max_units} kWh',
        xy=(dates[max_idx], max_units),
        xytext=(dates[max_idx], max_units + 15),
        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
        fontweight='bold', fontsize=9
    )

    ax.set_title("Household Electricity Consumption Trend Over Time", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("Billing Date / Period", fontsize=11, labelpad=8)
    ax.set_ylabel("Units Consumed (kWh)", fontsize=11, labelpad=8)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper left', frameon=True)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig(save_path, dpi=300)
    print(f"[Chart Saved] Line chart saved to: {save_path}")

    if show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)
    return save_path


def plot_period_comparison(readings: List[Dict[str, Any]], save_path: str = None, show: bool = True) -> str:
    """Generate a dual-axis Bar Chart comparing Units Consumed and Bill Amount across periods."""
    if not readings:
        print("No readings available to plot comparison.")
        return ""

    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "bar_chart_comparison.png")

    import numpy as np
    dates = [r["date"] for r in readings]
    units = [r["units"] for r in readings]
    bills = [r["bill_amount"] for r in readings]

    x = np.arange(len(dates))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    ax1.bar(x - width/2, units, width, label='Units Consumed (kWh)', color='#2ca02c', alpha=0.85)
    ax1.set_xlabel("Billing Period", fontsize=11, labelpad=8)
    ax1.set_ylabel("Electricity Consumed (kWh)", color='#2ca02c', fontsize=11, labelpad=8)
    ax1.tick_params(axis='y', labelcolor='#2ca02c')
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45, ha='right')

    # Secondary Y-axis for Bill Amount
    ax2 = ax1.twinx()
    ax2.bar(x + width/2, bills, width, label='Bill Amount (Rs.)', color='#d62728', alpha=0.85)
    ax2.set_ylabel("Estimated Bill Amount (Rs.)", color='#d62728', fontsize=11, labelpad=8)
    ax2.tick_params(axis='y', labelcolor='#d62728')

    plt.title("Comparative Analysis: Energy Consumption vs Estimated Bill Amount", fontsize=13, fontweight='bold', pad=12)
    ax1.grid(True, linestyle=':', alpha=0.5, axis='y')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    print(f"[Chart Saved] Bar chart saved to: {save_path}")

    if show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)
    return save_path


def plot_cost_scatter(
    readings: List[Dict[str, Any]],
    threshold: float = DEFAULT_HIGH_USAGE_THRESHOLD,
    save_path: str = None,
    show: bool = True
) -> str:
    """Generate a Scatter Plot comparing Units Consumed vs Bill Amount highlighting tariff tiers."""
    if not readings:
        print("No readings available to plot scatter analysis.")
        return ""

    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "scatter_plot_cost_analysis.png")

    normal_units = [r["units"] for r in readings if r["units"] < threshold]
    normal_bills = [r["bill_amount"] for r in readings if r["units"] < threshold]

    high_units = [r["units"] for r in readings if r["units"] >= threshold]
    high_bills = [r["bill_amount"] for r in readings if r["units"] >= threshold]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    if normal_units:
        ax.scatter(normal_units, normal_bills, color='#1f77b4', s=70, alpha=0.8, edgecolors='black', label='Normal Usage (< Threshold)')
    if high_units:
        ax.scatter(high_units, high_bills, color='#ff7f0e', s=90, marker='^', alpha=0.9, edgecolors='darkred', label=f'High Usage (≥ {threshold} kWh)')

    ax.axvline(threshold, color='crimson', linestyle='--', linewidth=1.5, label=f'High Usage Threshold ({threshold} kWh)')

    ax.set_title("Scatter Plot: Units Consumed vs Electricity Bill Amount", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Units Consumed (kWh)", fontsize=11, labelpad=8)
    ax.set_ylabel("Total Bill Amount (Rs.)", fontsize=11, labelpad=8)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='upper left', frameon=True)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    print(f"[Chart Saved] Scatter plot saved to: {save_path}")

    if show:
        try:
            plt.show()
        except Exception:
            pass
    plt.close(fig)
    return save_path


def plot_all_visualizations(readings: List[Dict[str, Any]], show: bool = True) -> List[str]:
    """Generate all 3 visualizations (Line, Bar, Scatter) and save them to reports/charts/."""
    p1 = plot_consumption_trend(readings, show=show)
    p2 = plot_period_comparison(readings, show=show)
    p3 = plot_cost_scatter(readings, show=show)
    return [p1, p2, p3]


# =============================================================================
# SECTION 6: USER INTERFACE & INPUT VALIDATION (Units 1 & 2)
# =============================================================================

def display_header():
    """Print project ASCII banner."""
    print("=" * 66)
    print("      SMART ELECTRICITY USAGE AND BILL ANALYZER")
    print("  Engineering Project | Programming Foundations for Engineers")
    print("=" * 66)


def display_menu():
    """Display interactive CLI menu."""
    print("\n" + "-" * 40)
    print("               MAIN MENU")
    print("-" * 40)
    print(" [1] Add New Electricity Meter Reading")
    print(" [2] View All Recorded Meter Readings")
    print(" [3] Quick Bill Estimator (Custom Units)")
    print(" [4] Generate & View Consumption Report")
    print(" [5] Identify High Energy Consumption Periods")
    print(" [6] Visualize Data (Line, Bar & Scatter Charts)")
    print(" [7] View Current Tariff Structure")
    print(" [8] Reload / Reset Sample Dataset")
    print(" [9] Exit Program")
    print("-" * 40)


def prompt_add_reading():
    """Prompt user to record a reading with rigorous input validation."""
    print("\n--- [1] Add New Meter Reading ---")
    readings = load_readings()

    # 1. Date Validation
    while True:
        date_input = input("Enter billing date (YYYY-MM-DD) or press Enter for today: ").strip()
        if not date_input:
            date_str = datetime.now().strftime("%Y-%m-%d")
            break
        try:
            datetime.strptime(date_input, "%Y-%m-%d")
            date_str = date_input
            break
        except ValueError:
            print(" [!] Error: Invalid date format. Please use YYYY-MM-DD (e.g. 2026-03-31).")
            log_error(f"Invalid date entered: '{date_input}'")

    suggested_prev = readings[-1]["curr_reading"] if readings else 0.0
    if readings:
        print(f" (Last recorded meter reading: {suggested_prev} kWh)")

    # 2. Previous Reading Validation
    while True:
        try:
            prev_input = input(f"Enter previous meter reading (kWh) [{suggested_prev}]: ").strip()
            prev_reading = float(prev_input) if prev_input else suggested_prev
            if prev_reading < 0:
                print(" [!] Reading cannot be negative.")
                continue
            break
        except ValueError:
            print(" [!] Error: Please enter a valid numeric value.")
            log_error("Invalid non-numeric input for previous reading.")

    # 3. Current Reading Validation
    while True:
        try:
            curr_input = input("Enter current meter reading (kWh): ").strip()
            curr_reading = float(curr_input)
            if curr_reading < prev_reading:
                print(f" [!] Error: Current reading ({curr_reading}) cannot be less than previous reading ({prev_reading}).")
                log_error(f"Current reading ({curr_reading}) < Previous reading ({prev_reading})")
                continue
            break
        except ValueError:
            print(" [!] Error: Please enter a valid numeric value.")
            log_error("Invalid non-numeric input for current reading.")

    try:
        units = calculate_units_consumed(prev_reading, curr_reading)
        bill_info = calculate_bill(units)
        status = "High Usage" if units >= DEFAULT_HIGH_USAGE_THRESHOLD else "Normal"
        new_id = len(readings) + 1

        record = {
            "id": new_id,
            "date": date_str,
            "prev_reading": prev_reading,
            "curr_reading": curr_reading,
            "units": units,
            "bill_amount": bill_info["total_bill"],
            "status": status
        }

        if save_reading(record):
            print("\n [+] Reading successfully recorded!")
            print(f"     ID            : {new_id}")
            print(f"     Date          : {date_str}")
            print(f"     Units Consumed: {units:.2f} kWh")
            print(f"     Status        : {status}")
            print(f"     Estimated Bill: {CURRENCY} {bill_info['total_bill']:.2f}")
    except Exception as e:
        log_error(f"Error calculating/saving reading: {e}")
        print(f" [!] System error: {e}")


def display_all_readings():
    """Print all readings formatted in a clean table."""
    print("\n--- [2] Recorded Meter Readings ---")
    readings = load_readings()
    if not readings:
        print(" [!] No records found. Use Option [1] to add readings or Option [8] to load sample data.")
        return

    print("-" * 75)
    print(f"{'ID':<4} {'Date':<12} {'Prev (kWh)':<12} {'Curr (kWh)':<12} {'Units':<10} {'Bill (Rs)':<12} {'Status'}")
    print("-" * 75)
    for r in readings:
        print(f"{r['id']:<4} {r['date']:<12} {r['prev_reading']:<12.1f} {r['curr_reading']:<12.1f} "
              f"{r['units']:<10.1f} {r['bill_amount']:<12.2f} {r['status']}")
    print("-" * 75)
    print(f" Total Records: {len(readings)}")


def prompt_quick_estimator():
    """Quick bill estimator for custom unit inputs."""
    print("\n--- [3] Quick Bill Estimator ---")
    while True:
        try:
            raw = input("Enter units consumed (kWh) [e.g. 150]: ").strip()
            units = float(raw)
            if units < 0:
                print(" [!] Units cannot be negative.")
                continue
            bill = calculate_bill(units)
            print("\n" + format_bill_summary(bill))
            break
        except ValueError:
            print(" [!] Please enter a valid number.")


def handle_generate_report():
    """Generate and display summary report."""
    print("\n--- [4] Generate & View Consumption Report ---")
    readings = load_readings()
    if not readings:
        print(" [!] No records available to generate report. Load data first.")
        return

    stats, summary_tuple = compute_statistics(readings)
    high_usage_set = identify_high_consumption_periods(readings)
    report_text = generate_consumption_report(readings, stats, high_usage_set)
    print("\n" + report_text)
    print(f"\n [+] Full report written to: {REPORT_TXT_PATH}")


def handle_high_consumption_analysis():
    """Identify and display high consumption analysis using sets."""
    print("\n--- [5] High Energy Consumption Analysis ---")
    readings = load_readings()
    if not readings:
        print(" [!] No records found.")
        return

    stats, summary = compute_statistics(readings)
    high_set = identify_high_consumption_periods(readings)
    seasonal = analyze_seasonal_patterns(readings)

    print(f"\n * Engineering High-Usage Threshold : {DEFAULT_HIGH_USAGE_THRESHOLD} kWh")
    print(f" * Average Usage Across All Periods  : {stats['avg_units']} kWh")
    print(f" * Maximum Peak Consumption Recorded : {stats['max_units']} kWh on {stats['max_date']}")
    print("-" * 60)
    print(f" High Consumption Periods Detected (Count: {len(high_set)}):")

    if high_set:
        for date in sorted(high_set):
            rec = next((r for r in readings if r["date"] == date), None)
            if rec:
                excess = rec["units"] - DEFAULT_HIGH_USAGE_THRESHOLD
                print(f"   [!] Date: {date} | Usage: {rec['units']} kWh (+{excess:.1f} kWh over threshold) | Bill: {CURRENCY} {rec['bill_amount']:.2f}")

        print("\n Set Analysis Insights:")
        print(f"   * Total Billing Cycles (Universal Set)    : {len(seasonal['all_periods'])} periods")
        print(f"   * Normal Usage Periods (Set Difference)   : {len(seasonal['normal_usage_periods'])} periods")
        print(f"   * High Usage during Summer (Intersection) : {len(seasonal['summer_high_peaks'])} periods ({', '.join(sorted(seasonal['summer_high_peaks'])) or 'None'})")
    else:
        print("   [+] Excellent! No periods exceeded the high-usage threshold.")


def handle_visualizations():
    """Display sub-menu for Matplotlib charts."""
    print("\n--- [6] Data Visualization (Matplotlib) ---")
    readings = load_readings()
    if not readings:
        print(" [!] No records available for visualization. Load data first.")
        return

    print(" Choose chart to generate:")
    print("  [1] Line Chart   : Electricity Consumption Trend Over Time")
    print("  [2] Bar Chart    : Period-wise Units & Bill Amount Comparison")
    print("  [3] Scatter Plot : Units Consumed vs Bill Amount (Tier Analysis)")
    print("  [4] Generate ALL 3 Charts and Save to Reports Folder")
    print("  [0] Back to Main Menu")

    choice = input("Enter visualization choice (0-4): ").strip()
    if choice == "1":
        plot_consumption_trend(readings, show=True)
    elif choice == "2":
        plot_period_comparison(readings, show=True)
    elif choice == "3":
        plot_cost_scatter(readings, show=True)
    elif choice == "4":
        saved_paths = plot_all_visualizations(readings, show=True)
        print(f"\n [+] All 3 charts successfully generated in: {os.path.dirname(saved_paths[0])}")
    elif choice == "0":
        return
    else:
        print(" [!] Invalid option.")


def display_tariff_structure():
    """Display configured tariff slabs."""
    print("\n--- [7] Current Configurable Tariff Slabs ---")
    print(f"{'Slab #':<8} {'Min Units':<12} {'Max Units':<12} {'Rate per Unit'}")
    print("-" * 52)
    for idx, (s_min, s_max, rate) in enumerate(DEFAULT_TARIFF_SLABS, start=1):
        max_str = "Above" if s_max == float('inf') else f"{int(s_max)}"
        print(f"{idx:<8} {int(s_min):<12} {max_str:<12} {CURRENCY} {rate:.2f}")
    print("-" * 52)
    print(f" Fixed Meter Charge     : {CURRENCY} {DEFAULT_FIXED_CHARGE:.2f}")
    print(f" Electricity Duty / Tax : {DEFAULT_TAX_RATE * 100:.1f}%")
    print(f" High Usage Threshold   : {DEFAULT_HIGH_USAGE_THRESHOLD} kWh")


def handle_reset_data():
    """Reload sample dataset."""
    print("\n--- [8] Reload Sample Dataset ---")
    confirm = input("This will reload 12 months of sample data. Proceed? (y/n): ").strip().lower()
    if confirm in ("y", "yes"):
        seed_sample_data(overwrite=True)
        print(" [+] 12 months of sample electricity readings loaded successfully!")
    else:
        print(" Operation cancelled.")


def main():
    """Main program execution loop."""
    display_header()

    # Pre-seed initial sample data if file is missing or empty
    if not os.path.exists(READINGS_CSV_PATH) or os.path.getsize(READINGS_CSV_PATH) == 0:
        print("\n [Notice] No existing records found. Initializing 12-month sample dataset...")
        seed_sample_data(overwrite=False)
        print(" [+] Sample dataset ready for immediate analysis.")

    while True:
        try:
            display_menu()
            choice = input("Enter your choice (1-9): ").strip()

            if choice == "1":
                prompt_add_reading()
            elif choice == "2":
                display_all_readings()
            elif choice == "3":
                prompt_quick_estimator()
            elif choice == "4":
                handle_generate_report()
            elif choice == "5":
                handle_high_consumption_analysis()
            elif choice == "6":
                handle_visualizations()
            elif choice == "7":
                display_tariff_structure()
            elif choice == "8":
                handle_reset_data()
            elif choice == "9":
                print("\n Thank you for using Smart Electricity Usage and Bill Analyzer. Goodbye!\n")
                sys.exit(0)
            else:
                print(" [!] Invalid option. Please enter a number between 1 and 9.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n Program exiting. Goodbye!")
            sys.exit(0)
        except Exception as e:
            log_error(f"Unexpected crash in main loop: {e}")
            print(f"\n [!] An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
