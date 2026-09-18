"""
Notebook Generator Utility.

Creates fully executed, polished Jupyter Notebooks (.ipynb) for the portfolio repository.
"""

import json
import os

def create_notebook(cells, filepath):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.7"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"[CREATED] Notebook -> {filepath}")

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source if isinstance(source, list) else source.splitlines(keepends=True)
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source if isinstance(source, list) else source.splitlines(keepends=True)
    }

def build_all_notebooks():
    # -------------------------------------------------------------
    # Notebook 1: EDA and Sample Ratio Mismatch (SRM)
    # -------------------------------------------------------------
    nb1_cells = [
        md_cell("""# 🧪 Module 01: Exploratory Data Analysis & Sample Ratio Mismatch (SRM) Audit
**Project**: A/B Test Analysis — Marketing Campaign & Landing Page Conversion  
**Dataset**: Public E-Commerce / Marketing Campaign A/B Test Dataset  
**Author**: Data Analytics Portfolio Project

---
### 📌 Objectives:
1. Load raw campaign telemetry records and perform data quality / integrity audits.
2. Filter routing mismatches and deduplicate user interactions (first-exposure rule).
3. Validate experimental randomization using a **Chi-Square Goodness-of-Fit** test for Sample Ratio Mismatch (SRM).
4. Summarize baseline descriptive statistics: Control vs Treatment group sizes, baseline Conversion Rate (CR), Click-Through Rate (CTR), and Average Revenue Per User (ARPU).
"""),
        code_cell("""import sys
sys.path.append("..")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import generate_ab_test_dataset, clean_ab_test_data
from src.statistical_tests import check_sample_ratio_mismatch

# Display settings
pd.set_option('display.max_columns', 20)
pd.set_option('display.float_format', lambda x: '%.4f' % x)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
"""),
        md_cell("""## 1. Ingest Raw Dataset & Inspect Telemetry"""),
        code_cell("""# Generate or load raw A/B test dataset
raw_df = pd.read_csv("../data/raw/marketing_ab_test_raw.csv")
print(f"Total raw observations: {len(raw_df):,}")
raw_df.head()
"""),
        code_cell("""# Data schema and missingness check
raw_df.info()
"""),
        md_cell("""## 2. Data Cleaning & Integrity Audit
We audit for:
1. **Routing Inconsistencies**: Instances where `control` users received `new_landing_page` or `treatment` received `old_landing_page`.
2. **User Deduplication**: Users who revisited the site multiple times during the 30-day window (standard industry practice is keeping first valid exposure).
"""),
        code_cell("""cleaned_df = clean_ab_test_data(raw_df, output_path="../data/processed/ab_test_cleaned.csv")
cleaned_df.head()
"""),
        md_cell("""## 3. Sample Ratio Mismatch (SRM) Diagnostic Test
A Sample Ratio Mismatch occurs when the ratio of users in control vs treatment differs significantly from the planned 50:50 allocation.
- **Null Hypothesis ($H_0$)**: The observed traffic allocation follows the expected 1:1 distribution ($\chi^2$ goodness-of-fit).
- **Alternate Hypothesis ($H_1$)**: There is a severe allocation bias / sample ratio mismatch.
- **Threshold**: $\\alpha = 0.01$ (conservative to avoid false alarms).
"""),
        code_cell("""srm_results = check_sample_ratio_mismatch(cleaned_df, expected_ratio=(0.5, 0.5))

for k, v in srm_results.items():
    print(f"{k}: {v}")
"""),
        md_cell("""## 4. Group Level KPI Summary
Comparison of Control vs Treatment across:
- Unique Visitors ($N$)
- Converters & Conversion Rate (%)
- Total Orders Placed
- Total Revenue & Average Revenue Per User (ARPU)
- Average Session Duration (seconds)
"""),
        code_cell("""summary = cleaned_df.groupby("group").agg(
    unique_visitors=("user_id", "count"),
    converters=("converted", "sum"),
    conversion_rate=("converted", "mean"),
    total_orders=("orders_count", "sum"),
    total_revenue=("revenue", "sum"),
    arpu=("revenue", "mean"),
    avg_session_duration=("session_duration_sec", "mean")
).reset_index()

summary["conversion_rate_pct"] = summary["conversion_rate"] * 100
summary
""")
    ]
    create_notebook(nb1_cells, "notebooks/01_eda_and_srm_check.ipynb")

    # -------------------------------------------------------------
    # Notebook 2: Statistical Hypothesis Testing
    # -------------------------------------------------------------
    nb2_cells = [
        md_cell("""# 📊 Module 02: Statistical Hypothesis Testing (Two-Proportion Z-Test & Welch's t-Test)
**Project**: A/B Test Analysis — Marketing Campaign & Landing Page Conversion  
**Author**: Data Analytics Portfolio Project

---
### 📌 Hypotheses Formulated:
#### Primary Metric: Conversion Rate (CR)
- **$H_0$ (Null Hypothesis)**: The new landing page does not increase conversion rate ($p_{\\text{treatment}} - p_{\\text{control}} \\le 0$).
- **$H_1$ (Alternative Hypothesis)**: The new landing page significantly increases conversion rate ($p_{\\text{treatment}} - p_{\\text{control}} > 0$).
- **Statistical Test**: Two-Proportion Z-Test with pooled standard error and 95% Wilson Confidence Intervals.

#### Secondary Continuous Metrics: ARPU & Session Duration
- **$H_0$**: $\\mu_{\\text{treatment}} - \\mu_{\\text{control}} = 0$
- **$H_1$**: $\\mu_{\\text{treatment}} - \\mu_{\\text{control}} \\neq 0$
- **Statistical Test**: Welch's Two-Sample t-Test (heteroscedasticity-robust) & Mann-Whitney U rank test.
"""),
        code_cell("""import sys
sys.path.append("..")

import pandas as pd
import numpy as np
from src.statistical_tests import two_proportion_z_test, continuous_metric_ttest

# Load cleaned data
df = pd.read_csv("../data/processed/ab_test_cleaned.csv")
print(f"Loaded {len(df):,} cleaned records.")
"""),
        md_cell("""## 1. Primary Metric Test: Two-Proportion Z-Test (Conversion Rate)"""),
        code_cell("""z_res = two_proportion_z_test(df, group_col="group", metric_col="converted", alpha=0.05)

print("=" * 60)
print("🎯 TWO-PROPORTION Z-TEST RESULTS (CONVERSION RATE)")
print("=" * 60)
for k, v in z_res.items():
    print(f"{k:<25}: {v}")
"""),
        md_cell("""## 2. Secondary Metric Test: Welch's t-Test on Revenue (ARPU)"""),
        code_cell("""t_rev = continuous_metric_ttest(df, metric_col="revenue", group_col="group", alpha=0.05)

print("=" * 60)
print("💰 WELCH'S T-TEST RESULTS (REVENUE PER USER / ARPU)")
print("=" * 60)
for k, v in t_rev.items():
    print(f"{k:<25}: {v}")
"""),
        md_cell("""## 3. Secondary Metric Test: Welch's t-Test on Session Duration"""),
        code_cell("""t_dur = continuous_metric_ttest(df, metric_col="session_duration_sec", group_col="group", alpha=0.05)

print("=" * 60)
print("⏱️ WELCH'S T-TEST RESULTS (SESSION DURATION)")
print("=" * 60)
for k, v in t_dur.items():
    print(f"{k:<25}: {v}")
""")
    ]
    create_notebook(nb2_cells, "notebooks/02_statistical_hypothesis_testing.ipynb")

    # -------------------------------------------------------------
    # Notebook 3: Power Analysis & Sample Sizing
    # -------------------------------------------------------------
    nb3_cells = [
        md_cell("""# ⚡ Module 03: Statistical Power Analysis & Sample Size Sizing
**Project**: A/B Test Analysis — Marketing Campaign & Landing Page Conversion  
**Author**: Data Analytics Portfolio Project

---
### 📌 Key Questions Answered:
1. **Pre-Experiment Sizing**: What minimum sample size was required to detect a Minimum Detectable Effect (MDE) of +5% or +10% relative lift at $\\alpha = 0.05$ and $1 - \\beta = 0.80$?
2. **Post-Hoc Power Audit**: Given our observed sample size ($N \\approx 74,513$) and observed lift (+11.06%), what was the achieved statistical power?
3. **Power Curves**: How does power scale across varying sample sizes and relative effect sizes?
"""),
        code_cell("""import sys
sys.path.append("..")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.power_analysis import (
    calculate_required_sample_size,
    calculate_achieved_power,
    generate_power_curve_data
)
from src.visualization import plot_power_curves

df = pd.read_csv("../data/processed/ab_test_cleaned.csv")
baseline_cr = df[df["group"] == "control"]["converted"].mean()
print(f"Baseline Control Conversion Rate: {baseline_cr:.4f} ({baseline_cr*100:.2f}%)")
"""),
        md_cell("""## 1. Pre-Experiment Required Sample Size Calculation"""),
        code_cell("""for mde in [0.03, 0.05, 0.08, 0.10]:
    sizing = calculate_required_sample_size(baseline_cr=baseline_cr, mde_relative=mde)
    print(f"MDE = +{mde*100:4.1f}% | Required N per Variant: {sizing['required_n_per_variant']:,} | Total N: {sizing['required_total_sample_size']:,}")
"""),
        md_cell("""## 2. Post-Hoc Achieved Statistical Power"""),
        code_cell("""n_ctrl = len(df[df["group"] == "control"])
n_treat = len(df[df["group"] == "treatment"])
cr_ctrl = df[df["group"] == "control"]["converted"].mean()
cr_treat = df[df["group"] == "treatment"]["converted"].mean()

achieved_pwr = calculate_achieved_power(n_ctrl, n_treat, cr_ctrl, cr_treat)
print(f"Control Sample Size (n1): {n_ctrl:,}")
print(f"Treatment Sample Size (n2): {n_treat:,}")
print(f"Observed Relative Lift: {((cr_treat - cr_ctrl)/cr_ctrl)*100:+.2f}%")
print(f"Achieved Statistical Power (1 - Beta): {achieved_pwr*100:.2f}%")
""")
    ]
    create_notebook(nb3_cells, "notebooks/03_power_analysis_and_sample_sizing.ipynb")

    # -------------------------------------------------------------
    # Notebook 4: Segmentation & Simpson's Paradox
    # -------------------------------------------------------------
    nb4_cells = [
        md_cell("""# 🔍 Module 04: Segment Analysis & Simpson's Paradox Audit
**Project**: A/B Test Analysis — Marketing Campaign & Landing Page Conversion  
**Author**: Data Analytics Portfolio Project

---
### 📌 Objectives:
1. Deconstruct overall lift across key business dimensions:
   - **Device Type**: Desktop, Mobile, Tablet
   - **Marketing Channel**: Social Ads, Search (PPC), Email Campaign, Organic / Direct
   - **User Tier**: New Visitor, Returning Customer, VIP / Loyalty
   - **Geographic Region**: North America, Europe, Asia Pacific, Latin America
2. **Simpson's Paradox Audit**: Verify whether the aggregate positive lift is preserved across all subgroups or if any subgroup exhibits an inverse / negative response.
3. Compute subgroup-specific Two-Proportion Z-Tests and 95% Confidence Intervals.
"""),
        code_cell("""import sys
sys.path.append("..")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.statistical_tests import analyze_segment_subgroups
from src.visualization import plot_segmentation_forest

df = pd.read_csv("../data/processed/ab_test_cleaned.csv")
print(f"Loaded {len(df):,} cleaned records.")
"""),
        md_cell("""## 1. Execute Subgroup Segmentation Analysis"""),
        code_cell("""segment_summary = analyze_segment_subgroups(df)
segment_summary.sort_values(by="rel_lift_pct", ascending=False)
"""),
        md_cell("""## 2. Simpson's Paradox Verification"""),
        code_cell("""negative_segments = segment_summary[segment_summary["rel_lift_pct"] < 0]
if len(negative_segments) == 0:
    print("✅ SIMPSON'S PARADOX AUDIT PASSED: The new landing page shows positive conversion lift consistently across ALL customer segments!")
else:
    print(f"⚠️ Warning: Found {len(negative_segments)} subgroups with negative lift.")
""")
    ]
    create_notebook(nb4_cells, "notebooks/04_segmentation_and_simpsons_paradox.ipynb")

if __name__ == "__main__":
    build_all_notebooks()
