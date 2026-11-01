"""
INTEGRATED MONTE CARLO YIELD ANALYZER
-------------------------------------
Module 1: Pandas Data Ingestion & Cleaning
Module 2: NumPy Statistical Analysis
Module 3: Matplotlib Yield Visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Global Design Specifications (converted to kHz for visualization)
LOWER_SPEC_KHZ = 790.0
UPPER_SPEC_KHZ = 820.0

# =============================================================================
# PART 1: PANDAS (Data Ingestion and Cleaning)
# =============================================================================
def get_clean_data(filepath):
    """
    Reads the LTSpice file and returns a clean DataFrame.
    """
    # 1. Read the file (works with tabs and Windows line endings)
    df = pd.read_csv(filepath, sep=r"\s+", engine="python")

    # 2. Tidy the column names
    df.columns = [c.strip().lower() for c in df.columns]

    # 3. Turn text into numbers
    df = df.apply(pd.to_numeric, errors="coerce")

    # 4. Remove empty rows and repeated runs
    df = df.dropna().drop_duplicates(subset="run")

    # 5. Make run numbers whole numbers
    df["run"] = df["run"].round().astype(int)

    # 6. Sort and renumber the rows
    return df.sort_values("run").reset_index(drop=True)


# =============================================================================
# PART 2: NUMPY (Statistics and Yield)
# =============================================================================
def analyze(df, low_khz, high_khz, column="bandwidth"):
    """
    Calculates statistics and yield percentages using NumPy vectorization.
    """
    # Extract Pandas column to NumPy array and convert Hz to kHz
    bw_khz = df[column].to_numpy() / 1e3

    # Statistics (ddof=1 = sample statistics)
    mean = np.mean(bw_khz)
    std = np.std(bw_khz, ddof=1)
    var = np.var(bw_khz, ddof=1)
    lo, hi = np.min(bw_khz), np.max(bw_khz)

    # Yield: Vectorized boolean check
    passed = (bw_khz >= low_khz) & (bw_khz <= high_khz)
    yield_pct = 100 * np.count_nonzero(passed) / len(bw_khz)

    return {
        "values": bw_khz, 
        "mean": mean, 
        "std": std, 
        "variance": var,
        "min": lo, 
        "max": hi, 
        "yield_pct": yield_pct,
        "total_runs": len(bw_khz)
    }


# =============================================================================
# PART 3: MATPLOTLIB (Your Contribution - Visualization & Verdict)
# =============================================================================
def plot_results(stats, test_name, low_spec, high_spec):
    """
    Prints the engineering summary and renders the tolerance histogram.
    """
    # 1. Print Engineering Summary
    print("=" * 60)
    print(f"    MONTE CARLO SUMMARY: {test_name}")
    print("=" * 60)
    print(f"Total Circuit Runs : {stats['total_runs']}")
    print(f"Mean Bandwidth     : {stats['mean']:.2f} kHz")
    print(f"Standard Deviation : {stats['std']:.2f} kHz")
    print(f"Worst-Case Minimum : {stats['min']:.2f} kHz")
    print(f"Worst-Case Maximum : {stats['max']:.2f} kHz")
    print(f"Manufacturing Yield: {stats['yield_pct']:.1f}%")
    
    if stats['yield_pct'] < 90:
        print("Verdict: FAIL - Variance is too high. Tighter components required.")
    else:
        print("Verdict: PASS - Design is robust. Tolerances meet standards.")
    print("-" * 60 + "\n")

    # 2. Render Matplotlib Histogram
    plt.figure(figsize=(9, 5.5))
    plt.hist(
        stats['values'], 
        bins=12, 
        color='skyblue', 
        edgecolor='black', 
        alpha=0.75, 
        label=f'Simulated Runs (N={stats["total_runs"]})'
    )

    # 3. Apply Threshold Overlays
    plt.axvline(stats['mean'], color='green', linestyle='-', linewidth=2, label=f'Mean ({stats["mean"]:.1f} kHz)')
    plt.axvline(low_spec, color='red', linestyle='--', linewidth=2, label=f'Lower Spec ({low_spec} kHz)')
    plt.axvline(high_spec, color='red', linestyle='--', linewidth=2, label=f'Upper Spec ({high_spec} kHz)')

    # 4. Styling and Execution
    plt.title(f'Yield Analysis: {test_name}', fontsize=12, fontweight='bold')
    plt.xlabel('Bandwidth (-3 dB Cutoff) [kHz]', fontsize=11)
    plt.ylabel('Number of Manufactured Boards (Count)', fontsize=11)
    plt.grid(axis='y', linestyle=':', alpha=0.6)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.show()


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    
    try:
        # --- TEST 1: Baseline Analysis (Standard Components) ---
        df_baseline = get_clean_data("circuit.log.txt")
        stats_baseline = analyze(df_baseline, LOWER_SPEC_KHZ, UPPER_SPEC_KHZ)
        plot_results(stats_baseline, "Standard Parts (5% R, 10% C)", LOWER_SPEC_KHZ, UPPER_SPEC_KHZ)

        # --- TEST 2: Precision Analysis (Upgraded Components) ---
        df_precision = get_clean_data("circuitsim2.log.txt")
        stats_precision = analyze(df_precision, LOWER_SPEC_KHZ, UPPER_SPEC_KHZ)
        plot_results(stats_precision, "Precision Parts (1% R, 2% C)", LOWER_SPEC_KHZ, UPPER_SPEC_KHZ)
        
    except FileNotFoundError as e:
        print(f"\nERROR: Could not find data file. Ensure logs are in the same folder as this script.\nDetails: {e}")