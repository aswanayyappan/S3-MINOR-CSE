"""
Data Visualization Module
Generates Line Charts, Bar Charts, and Scatter Plots using Matplotlib
for engineering data presentation and consumption pattern analysis.
"""

import os
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from config import CHARTS_DIR, DEFAULT_HIGH_USAGE_THRESHOLD


def plot_consumption_trend(
    readings: List[Dict[str, Any]],
    save_path: str = None,
    show: bool = True
) -> str:
    """
    Generate a Line Chart showing electricity consumption trend over time.
    Features:
        - Units consumed plotted chronologically.
        - Horizontal benchmark line representing the average consumption.
        - Clear grid, data markers, and labels.
    """
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

    # Annotate peak point
    max_units = max(units)
    max_idx = units.index(max_units)
    ax.annotate(
        f'Peak: {max_units} kWh',
        xy=(dates[max_idx], max_units),
        xytext=(dates[max_idx], max_units + 15),
        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
        fontweight='bold',
        fontsize=9
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


def plot_period_comparison(
    readings: List[Dict[str, Any]],
    save_path: str = None,
    show: bool = True
) -> str:
    """
    Generate a Bar Chart comparing units consumed and electricity bill across periods.
    Uses dual axes (Units on Left Y-axis, Cost on Right Y-axis) or side-by-side bars.
    """
    if not readings:
        print("No readings available to plot period comparison.")
        return ""

    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "bar_chart_comparison.png")

    dates = [r["date"] for r in readings]
    units = [r["units"] for r in readings]
    bills = [r["bill_amount"] for r in readings]

    import numpy as np
    x = np.arange(len(dates))
    width = 0.38

    fig, ax1 = plt.subplots(figsize=(11, 5.5))

    bar1 = ax1.bar(x - width/2, units, width, label='Units Consumed (kWh)', color='#2ca02c', alpha=0.85)
    ax1.set_xlabel("Billing Period", fontsize=11, labelpad=8)
    ax1.set_ylabel("Electricity Consumed (kWh)", color='#2ca02c', fontsize=11, labelpad=8)
    ax1.tick_params(axis='y', labelcolor='#2ca02c')
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=45, ha='right')

    # Secondary Y-axis for Bill Amount
    ax2 = ax1.twinx()
    bar2 = ax2.bar(x + width/2, bills, width, label='Bill Amount (₹)', color='#d62728', alpha=0.85)
    ax2.set_ylabel("Estimated Bill Amount (₹)", color='#d62728', fontsize=11, labelpad=8)
    ax2.tick_params(axis='y', labelcolor='#d62728')

    plt.title("Comparative Analysis: Energy Consumption vs Estimated Bill Amount", fontsize=13, fontweight='bold', pad=12)
    ax1.grid(True, linestyle=':', alpha=0.5, axis='y')

    # Combined legend
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
    """
    Generate a Scatter Plot displaying Units Consumed vs Bill Amount.
    Highlights:
        - Progressive non-linear tariff curve effect.
        - High-consumption points highlighted in contrasting color.
        - Vertical threshold line separating Normal from High usage.
    """
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
    ax.set_ylabel("Total Bill Amount (₹)", fontsize=11, labelpad=8)
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


def plot_all_visualizations(
    readings: List[Dict[str, Any]],
    threshold: float = DEFAULT_HIGH_USAGE_THRESHOLD,
    show: bool = True
) -> List[str]:
    """
    Generate and save all 3 visualizations (Line, Bar, and Scatter).
    Returns list of paths where charts were saved.
    """
    p1 = plot_consumption_trend(readings, show=show)
    p2 = plot_period_comparison(readings, show=show)
    p3 = plot_cost_scatter(readings, threshold=threshold, show=show)
    return [p1, p2, p3]
