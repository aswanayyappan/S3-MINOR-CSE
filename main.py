"""
Smart Electricity Usage and Bill Analyzer
Main Program & User Interface
PBL Course: Programming Foundations for Engineers (25MNCST309)

Demonstrates:
  - Unit 1: Variables, operators, conditionals, loops, exception handling (try-except)
  - Unit 2: Modular programming, functions, standard libraries
  - Unit 3: Lists, tuples, dictionaries, sets, CSV & text file handling
  - Unit 4: Data visualization (Line, Bar, Scatter) using Matplotlib, Git version control practices
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Ensure terminal stdout/stderr handles UTF-8 gracefully on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import (
    READINGS_CSV_PATH,
    ERROR_LOG_PATH,
    REPORT_TXT_PATH,
    DEFAULT_TARIFF_SLABS,
    DEFAULT_FIXED_CHARGE,
    DEFAULT_TAX_RATE,
    DEFAULT_HIGH_USAGE_THRESHOLD,
    CURRENCY
)
from tariff import calculate_units_consumed, calculate_bill, format_bill_summary
from data_manager import (
    load_readings,
    save_reading,
    seed_sample_data,
    generate_consumption_report,
    log_error
)
from analytics import (
    compute_statistics,
    identify_high_consumption_periods,
    analyze_seasonal_patterns
)
from visualization import (
    plot_consumption_trend,
    plot_period_comparison,
    plot_cost_scatter,
    plot_all_visualizations
)


def display_header():
    """Display program header."""
    print("=" * 66)
    print("      SMART ELECTRICITY USAGE AND BILL ANALYZER")
    print("  Engineering Project | Programming Foundations for Engineers")
    print("=" * 66)


def display_menu():
    """Display the main interactive menu."""
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
    """Prompt user to add a new meter reading with strict validation."""
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
            log_error(f"User entered invalid date format: '{date_input}'")

    # Suggest previous reading if prior records exist
    suggested_prev = 0.0
    if readings:
        suggested_prev = readings[-1]["curr_reading"]
        print(f" (Last recorded meter reading was: {suggested_prev} kWh)")

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
            print(" [!] Error: Please enter a valid numerical value.")
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
            print(" [!] Error: Please enter a valid numerical value.")
            log_error("Invalid non-numeric input for current reading.")

    # Engineering Computation
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

        success = save_reading(record)
        if success:
            print("\n [+] Reading successfully recorded!")
            print(f"     ID            : {new_id}")
            print(f"     Date          : {date_str}")
            print(f"     Units Consumed: {units:.2f} kWh")
            print(f"     Status        : {status}")
            print(f"     Estimated Bill: {CURRENCY} {bill_info['total_bill']:.2f}")
    except Exception as e:
        log_error(f"Error during reading calculation and save: {e}")
        print(f" [!] System error: {e}")


def display_all_readings():
    """Display all meter readings in a clean tabular format."""
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
    """Quick bill calculation for custom units entered by user."""
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
            log_error("Invalid number in Quick Estimator.")


def handle_generate_report():
    """Generate and display the consumption analysis report."""
    print("\n--- [4] Generate & View Consumption Report ---")
    readings = load_readings()
    if not readings:
        print(" [!] No records available to generate report. Please load data first.")
        return

    stats, summary_tuple = compute_statistics(readings)
    high_usage_set = identify_high_consumption_periods(readings)

    report_text = generate_consumption_report(readings, stats, high_usage_set)
    print("\n" + report_text)
    print(f"\n [+] Full report written to: {REPORT_TXT_PATH}")


def handle_high_consumption_analysis():
    """Identify high consumption periods using Python sets and statistics."""
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

        # Set operations output
        print("\n Set Analysis Insights:")
        print(f"   * Total Billing Cycles (Universal Set)    : {len(seasonal['all_periods'])} periods")
        print(f"   * Normal Usage Periods (Set Difference)   : {len(seasonal['normal_usage_periods'])} periods")
        print(f"   * High Usage during Summer (Intersection) : {len(seasonal['summer_high_peaks'])} periods ({', '.join(sorted(seasonal['summer_high_peaks'])) or 'None'})")
    else:
        print("   [+] Excellent! No periods exceeded the high-usage threshold.")


def handle_visualizations():
    """Interactive visualization sub-menu for Matplotlib charts."""
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
    """Display configured tariff slabs and rates."""
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
    """Pre-seed sample data with confirmation."""
    print("\n--- [8] Reload Sample Dataset ---")
    confirm = input("This will overwrite current readings with 12 months of sample data. Proceed? (y/n): ").strip().lower()
    if confirm in ("y", "yes"):
        seed_sample_data(overwrite=True)
        print(" [+] 12 months of realistic household electricity readings loaded successfully!")
    else:
        print(" Operation cancelled.")


def main():
    """Program entry point."""
    display_header()

    # Pre-seed sample dataset if file does not exist yet
    if not os.path.exists(READINGS_CSV_PATH) or os.path.getsize(READINGS_CSV_PATH) == 0:
        print("\n [Notice] No existing readings found. Auto-populating initial sample dataset...")
        seed_sample_data(overwrite=False)
        print(" [+] Initialized with 12 months of sample household consumption records.")

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
            print("\n\n Program exiting...")
            sys.exit(0)
        except Exception as e:
            log_error(f"Unexpected crash in main loop: {e}")
            print(f"\n [!] An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
