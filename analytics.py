"""
Analytics and Data Processing Module
Utilizes Python data structures (lists, tuples, dictionaries, and sets)
to process engineering measurement data, calculate statistics, and identify peak usage.
"""

from typing import List, Tuple, Dict, Set, Any
from config import DEFAULT_HIGH_USAGE_THRESHOLD


def compute_statistics(readings: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Tuple[float, float, float]]:
    """
    Process meter readings using lists and dictionaries to calculate summary statistics.
    
    Parameters:
        readings (list of dict): List of reading records.
        
    Returns:
        tuple: (stats_dictionary, summary_tuple)
            - stats_dictionary: Contains total, average, min, max consumption and cost.
            - summary_tuple: (total_units, total_cost, average_units)
    """
    if not readings:
        empty_stats = {
            "count": 0,
            "total_units": 0.0,
            "avg_units": 0.0,
            "min_units": 0.0,
            "max_units": 0.0,
            "min_date": "N/A",
            "max_date": "N/A",
            "total_cost": 0.0,
            "avg_cost": 0.0
        }
        return empty_stats, (0.0, 0.0, 0.0)

    # 1. Using LISTS for numerical processing
    units_list: List[float] = [record["units"] for record in readings]
    costs_list: List[float] = [record["bill_amount"] for record in readings]
    dates_list: List[str] = [record["date"] for record in readings]

    total_units = sum(units_list)
    total_cost = sum(costs_list)
    count = len(readings)
    
    avg_units = round(total_units / count, 2)
    avg_cost = round(total_cost / count, 2)

    min_units = min(units_list)
    max_units = max(units_list)

    # Identify corresponding dates using list indexing
    min_index = units_list.index(min_units)
    max_index = units_list.index(max_units)
    min_date = dates_list[min_index]
    max_date = dates_list[max_index]

    # 2. Using a DICTIONARY to store labeled engineering metrics
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

    # 3. Using a TUPLE for immutable summary representation
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
    Identify periods where electricity consumption exceeds the engineering threshold.
    Uses Python SETS to guarantee unique date tracking and demonstrate set operations.
    
    Parameters:
        readings (list of dict): List of reading records.
        threshold (float): Threshold in kWh.
        
    Returns:
        set: A set of date strings representing high consumption periods.
    """
    # 4. Using SET COMPREHENSION to collect high-usage dates
    high_consumption_dates: Set[str] = {
        record["date"] for record in readings if record["units"] >= threshold
    }
    return high_consumption_dates


def analyze_seasonal_patterns(readings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Demonstrate SET operations (Union, Intersection, Difference) to compare
    peak summer months vs general billing periods.
    
    Parameters:
        readings (list of dict): List of reading records.
        
    Returns:
        dict: Set analysis results.
    """
    all_billing_periods: Set[str] = {record["date"] for record in readings}
    high_usage_periods: Set[str] = identify_high_consumption_periods(readings)
    normal_usage_periods: Set[str] = all_billing_periods.difference(high_usage_periods)

    # Example: Summer period definition (April, May, June)
    summer_periods: Set[str] = {
        record["date"] for record in readings if any(record["date"].startswith(f"2025-0{m}") for m in ["4", "5", "6"])
    }

    # High usage during summer (Set Intersection)
    summer_high_peaks: Set[str] = high_usage_periods.intersection(summer_periods)

    return {
        "all_periods": all_billing_periods,
        "high_usage_periods": high_usage_periods,
        "normal_usage_periods": normal_usage_periods,
        "summer_periods": summer_periods,
        "summer_high_peaks": summer_high_peaks
    }
