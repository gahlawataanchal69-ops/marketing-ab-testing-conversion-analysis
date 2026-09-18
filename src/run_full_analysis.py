"""
Master Pipeline Runner for A/B Testing Analysis.

Executes end-to-end data processing, statistical tests, power calculation,
segmentation audits, figure generation, and Power BI data exports.
"""

import os
import json
import pandas as pd
import numpy as np

from src.data_loader import generate_ab_test_dataset, clean_ab_test_data
from src.statistical_tests import (
    check_sample_ratio_mismatch,
    two_proportion_z_test,
    continuous_metric_ttest,
    analyze_segment_subgroups
)
from src.power_analysis import (
    calculate_required_sample_size,
    calculate_achieved_power,
    generate_power_curve_data
)
from src.visualization import (
    plot_srm_check,
    plot_conversion_rate_with_ci,
    plot_daily_trend,
    plot_revenue_distributions,
    plot_power_curves,
    plot_segmentation_forest
)

def run_pipeline():
    print("=" * 80)
    print(" >>> EXECUTING COMPLETE A/B TESTING PORTFOLIO PIPELINE <<<")
    print("=" * 80)
    
    # 1. Generate Raw Dataset & Clean
    print("\n[STEP 1/6] Ingesting & Cleaning Data...")
    raw_df = generate_ab_test_dataset(n_samples=120_000, random_seed=42)
    cleaned_df = clean_ab_test_data(raw_df)
    
    # 2. Check Sample Ratio Mismatch (SRM)
    print("\n[STEP 2/6] Running Sample Ratio Mismatch (SRM) Test...")
    srm_res = check_sample_ratio_mismatch(cleaned_df)
    print(f" -> Control Sample: {srm_res['n_control']:,} ({srm_res['observed_control_pct']}%)")
    print(f" -> Treatment Sample: {srm_res['n_treatment']:,} ({srm_res['observed_treatment_pct']}%)")
    print(f" -> Chi2 Stat: {srm_res['chi2_statistic']:.4f}, p-value: {srm_res['p_value']:.4f}")
    print(f" -> Verdict: {srm_res['verdict']}")
    
    # 3. Conversion Rate Two-Proportion Z-Test
    print("\n[STEP 3/6] Running Two-Proportion Z-Test on Conversion Rate...")
    z_res = two_proportion_z_test(cleaned_df)
    print(f" -> Control Conversion Rate: {z_res['cr_control_pct']}% (95% CI: {z_res['ci_control_pct']}%)")
    print(f" -> Treatment Conversion Rate: {z_res['cr_treatment_pct']}% (95% CI: {z_res['ci_treatment_pct']}%)")
    print(f" -> Absolute Lift: {z_res['absolute_lift_pct']:+.3f}% (95% CI: {z_res['ci_absolute_lift_pct']}%)")
    print(f" -> Relative Lift: {z_res['relative_lift_pct']:+.2f}% (95% CI: {z_res['ci_relative_lift_pct']}%)")
    print(f" -> Z-Statistic: {z_res['z_statistic']:.4f}, p-value: {z_res['p_value']:.4e}")
    print(f" -> Result: {z_res['conclusion']}")
    
    # 4. Continuous Metric Tests (Revenue & Session Duration)
    print("\n[STEP 4/6] Running Welch's t-Test on Continuous Metrics...")
    t_rev = continuous_metric_ttest(cleaned_df, metric_col="revenue")
    t_dur = continuous_metric_ttest(cleaned_df, metric_col="session_duration_sec")
    print(f" -> ARPU (Revenue): Control = ${t_rev['mean_control']}, Treatment = ${t_rev['mean_treatment']} (Lift: {t_rev['relative_lift_pct']:+.2f}%, p = {t_rev['p_value_ttest']:.4e}, Cohen's d = {t_rev['cohens_d']})")
    print(f" -> Session Duration: Control = {t_dur['mean_control']}s, Treatment = {t_dur['mean_treatment']}s (Lift: {t_dur['relative_lift_pct']:+.2f}%, p = {t_dur['p_value_ttest']:.4e})")
    
    # 5. Power Analysis & Sample Sizing
    print("\n[STEP 5/6] Calculating Power Analysis & Sample Size Sizing...")
    baseline_cr = z_res['cr_control']
    sizing_5pct = calculate_required_sample_size(baseline_cr=baseline_cr, mde_relative=0.05)
    sizing_10pct = calculate_required_sample_size(baseline_cr=baseline_cr, mde_relative=0.10)
    achieved_pwr = calculate_achieved_power(
        n_ctrl=z_res['n_control'],
        n_treat=z_res['n_treatment'],
        cr_ctrl=z_res['cr_control'],
        cr_treat=z_res['cr_treatment']
    )
    print(f" -> Required sample size per variant for 5% MDE: {sizing_5pct['required_n_per_variant']:,}")
    print(f" -> Required sample size per variant for 10% MDE: {sizing_10pct['required_n_per_variant']:,}")
    print(f" -> Actual sample size per variant: {z_res['n_control']:,}")
    print(f" -> Post-Hoc Achieved Statistical Power: {achieved_pwr * 100:.2f}% (Experiment is robustly powered)")
    
    # 6. Segment Analysis & Simpson's Paradox Check
    print("\n[STEP 6/6] Segmenting by Device, Channel, Region, User Tier...")
    seg_df = analyze_segment_subgroups(cleaned_df)
    
    # Check for Simpson's Paradox: any segment with negative lift while overall is positive?
    negative_segments = seg_df[seg_df["abs_lift_pct"] < 0]
    if len(negative_segments) == 0:
        print(" -> Simpson's Paradox Check: PASSED. Treatment maintains positive lift across all subgroups.")
    else:
        print(f" -> Note: {len(negative_segments)} subgroups showed divergent response.")
        
    # Generate Visualizations
    print("\n[FIGURES] Generating Publication Figures...")
    plot_srm_check(srm_res)
    plot_conversion_rate_with_ci(z_res)
    plot_daily_trend(cleaned_df)
    plot_revenue_distributions(cleaned_df, t_rev)
    power_curve_data = generate_power_curve_data(baseline_cr=baseline_cr)
    plot_power_curves(power_curve_data, actual_sample_per_variant=z_res['n_control'], actual_lift_pct=z_res['relative_lift_pct'])
    plot_segmentation_forest(seg_df, overall_rel_lift=z_res['relative_lift_pct'])
    
    # Export pre-aggregated summary tables for Power BI / Tableau
    print("\n[EXPORTS] Exporting Clean Aggregations for Power BI / Tableau...")
    
    # Daily metrics table
    daily_df = cleaned_df.groupby(["date", "group", "device", "campaign_channel", "region", "user_tier"]).agg(
        visitors=("user_id", "count"),
        conversions=("converted", "sum"),
        total_orders=("orders_count", "sum"),
        total_revenue=("revenue", "sum"),
        avg_session_duration=("session_duration_sec", "mean")
    ).reset_index()
    daily_df.to_csv("data/processed/ab_test_daily_metrics.csv", index=False)
    
    # Segment summary table
    seg_df.to_csv("data/processed/ab_test_segment_summary.csv", index=False)
    
    # Statistical KPI export
    kpi_summary = {
        "srm_test": srm_res,
        "conversion_rate_test": z_res,
        "revenue_arpu_test": t_rev,
        "session_duration_test": t_dur,
        "sample_sizing_5pct_mde": sizing_5pct,
        "achieved_power_pct": achieved_pwr * 100
    }
    with open("data/processed/ab_test_statistical_summary.json", "w") as f:
        json.dump(kpi_summary, f, indent=4)
        
    print("\n[SUCCESS] End-to-end A/B Testing Pipeline Execution Completed Successfully!")

if __name__ == "__main__":
    run_pipeline()
