# Automated-Monte-Carlo-Yield-Analyzer
# Integrated Monte Carlo Yield Analyzer

This Python tool automates the processing of LTSpice simulation logs to perform statistical yield analysis and visualize Monte Carlo circuit tolerance data.

## Features
* **Data Ingestion & Cleaning:** Uses Pandas to read LTSpice files, standardize column names, handle text-to-number conversions, and remove duplicate runs.
* **Statistical Analysis:** Uses NumPy to calculate mean, standard deviation, variance, minimum, maximum, and manufacturing yield based on 790.0 kHz to 820.0 kHz bandwidth specifications.
* **Yield Visualization:** Uses Matplotlib to render a 12-bin tolerance histogram overlayed with the simulated mean and upper/lower specification thresholds.
* **Automated Engineering Verdicts:** Outputs an engineering summary to the terminal and assigns a PASS/FAIL verdict, requiring at least a 90% yield for a robust design.

## Prerequisites
```bash
pip install pandas numpy matplotlib
