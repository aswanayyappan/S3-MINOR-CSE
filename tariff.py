"""
Tariff and Bill Calculation Engine
Performs engineering computations for electricity charges based on tiered/slab tariff structures.
Demonstrates functions, parameters, return values, loops, and conditional statements.
"""

from typing import List, Tuple, Dict, Any
from config import DEFAULT_TARIFF_SLABS, DEFAULT_FIXED_CHARGE, DEFAULT_TAX_RATE, CURRENCY


def calculate_units_consumed(previous_reading: float, current_reading: float) -> float:
    """
    Calculate units consumed between two meter readings.
    
    Formula: Units = Current Reading - Previous Reading
    
    Parameters:
        previous_reading (float): Meter reading at start of billing cycle.
        current_reading (float): Meter reading at end of billing cycle.
        
    Returns:
        float: Total units consumed (kWh).
        
    Raises:
        ValueError: If current_reading is less than previous_reading or inputs are negative.
    """
    if previous_reading < 0 or current_reading < 0:
        raise ValueError("Meter readings cannot be negative numbers.")
    if current_reading < previous_reading:
        raise ValueError("Current reading cannot be lower than previous reading.")
    
    units = round(current_reading - previous_reading, 2)
    return units


def calculate_bill(
    units: float,
    tariff_slabs: List[Tuple[float, float, float]] = None,
    fixed_charge: float = None,
    tax_rate: float = None
) -> Dict[str, Any]:
    """
    Compute electricity bill based on progressive slab/tiered tariff structure.
    
    Engineering Calculation:
        - Energy Charges = Sum(units_in_slab * slab_rate)
        - Subtotal = Energy Charges + Fixed Monthly Charge
        - Tax Amount = Subtotal * Tax Rate
        - Total Bill = Subtotal + Tax Amount
        
    Parameters:
        units (float): Total units consumed (kWh).
        tariff_slabs (list of tuples): Configurable slabs [(min, max, rate), ...].
        fixed_charge (float): Fixed meter/maintenance charges.
        tax_rate (float): Regulatory electricity tax percentage (e.g. 0.05 for 5%).
        
    Returns:
        dict: Detailed breakdown containing slab wise charges, taxes, and total payable.
    """
    if units < 0:
        raise ValueError("Units consumed cannot be negative.")
        
    # Use defaults from config if not explicitly provided
    if tariff_slabs is None:
        tariff_slabs = DEFAULT_TARIFF_SLABS
    if fixed_charge is None:
        fixed_charge = DEFAULT_FIXED_CHARGE
    if tax_rate is None:
        tax_rate = DEFAULT_TAX_RATE

    units_remaining = units
    energy_charge_total = 0.0
    slab_breakdown = []  # List of tuples: (slab_label, units_billed, rate, cost)

    # Progressive slab calculation using loops and conditional logic
    for slab_min, slab_max, rate in tariff_slabs:
        if units_remaining <= 0:
            break
            
        slab_capacity = slab_max - slab_min + (1 if slab_min > 0 else 0)
        
        # Determine how many units fall into this specific tier
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

    # Organized in a structured dictionary for data handling
    bill_details = {
        "units": round(units, 2),
        "slab_breakdown": slab_breakdown,
        "energy_charges": round(energy_charge_total, 2),
        "fixed_charge": round(fixed_charge, 2),
        "subtotal": round(subtotal, 2),
        "tax_rate_percent": round(tax_rate * 100, 1),
        "tax_amount": round(tax_amount, 2),
        "total_bill": round(total_bill, 2)
    }

    return bill_details


def format_bill_summary(bill: Dict[str, Any]) -> str:
    """
    Format a dictionary of bill details into a clean, readable text receipt.
    
    Parameters:
        bill (dict): Bill dictionary produced by calculate_bill().
        
    Returns:
        str: Multi-line formatted receipt.
    """
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
