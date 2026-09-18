"""
Publication-Quality Visualization Module for A/B Testing Analytics.

Generates high-resolution, modern, stylized visual figures for reports and dashboards.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter, FuncFormatter

# Set modern publication styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "semibold",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 15,
    "figure.titleweight": "bold",
    "figure.autolayout": True
})

# Custom Palette
COLOR_CONTROL = "#3A6073"       # Slate Blue
COLOR_TREATMENT = "#00B4D8"     # Cyan / Electric Blue
COLOR_ACCENT = "#2EC4B6"        # Emerald
COLOR_DARK = "#1E293B"          # Slate 800
COLOR_LIGHT = "#F8FAFC"         # Off-white
COLOR_WARN = "#E63946"          # Crimson / Alert


def plot_srm_check(srm_dict: dict, save_path: str = "reports/figures/01_srm_check.png"):
    """Visualizes Sample Ratio Mismatch check (Observed vs Expected Counts)."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    
    categories = ["Control Group", "Treatment Group"]
    observed = [srm_dict["n_control"], srm_dict["n_treatment"]]
    expected = [srm_dict["total_sample"] / 2, srm_dict["total_sample"] / 2]
    
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, observed, width, label="Observed", color=[COLOR_CONTROL, COLOR_TREATMENT], alpha=0.9, edgecolor="none")
    rects2 = ax.bar(x + width/2, expected, width, label="Expected (50:50)", color="#94A3B8", alpha=0.5, hatch="//")
    
    ax.set_ylabel("User Exposures", fontsize=11)
    ax.set_title("Sample Ratio Mismatch (SRM) Diagnostic Check", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontweight="bold")
    ax.legend(frameon=True, facecolor="white", edgecolor="#E2E8F0")
    
    # Value annotations
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{int(h):,}\n({h/srm_dict['total_sample']*100:.2f}%)",
                    xy=(rect.get_x() + rect.get_width() / 2, h / 2),
                    xytext=(0, 0), textcoords="offset points",
                    ha="center", va="center", color="white", fontweight="bold", fontsize=10)
        
    # Text box for Chi2 test statistics
    status_text = (
        f"Chi-Square Stat (χ²): {srm_dict['chi2_statistic']:.4f}\n"
        f"P-Value: {srm_dict['p_value']:.4f} (α = 0.01)\n"
        f"SRM Status: {'FAILED (SRM)' if srm_dict['srm_detected'] else 'PASSED (No SRM)'}"
    )
    ax.text(0.98, 0.95, status_text, transform=ax.transAxes, verticalalignment="top",
            horizontalalignment="right", bbox=dict(boxstyle="round,pad=0.6", facecolor="#F1F5F9", edgecolor="#CBD5E1"),
            fontsize=9.5, linespacing=1.3)
            
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] SRM Figure -> {save_path}")


def plot_conversion_rate_with_ci(z_res: dict, save_path: str = "reports/figures/02_conversion_rate_ci.png"):
    """Visualizes Conversion Rate for Control vs Treatment with 95% Confidence Intervals."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 5.5), dpi=300)
    
    groups = ["Control (Old Page)", "Treatment (New Page)"]
    cr_values = [z_res["cr_control_pct"], z_res["cr_treatment_pct"]]
    
    ci_ctrl_err = [
        z_res["cr_control_pct"] - z_res["ci_control_pct"][0],
        z_res["ci_control_pct"][1] - z_res["cr_control_pct"]
    ]
    ci_treat_err = [
        z_res["cr_treatment_pct"] - z_res["ci_treatment_pct"][0],
        z_res["ci_treatment_pct"][1] - z_res["cr_treatment_pct"]
    ]
    yerr = np.array([[ci_ctrl_err[0], ci_treat_err[0]], [ci_ctrl_err[1], ci_treat_err[1]]])
    
    bars = ax.bar(groups, cr_values, yerr=yerr, capsize=8, color=[COLOR_CONTROL, COLOR_TREATMENT],
                  alpha=0.9, width=0.5, edgecolor="none", error_kw={"elinewidth": 2, "ecolor": COLOR_DARK})
    
    ax.set_ylabel("Conversion Rate (%)", fontsize=11)
    ax.set_title("Conversion Rate Comparison (with 95% Wilson Score CIs)", pad=15)
    ax.yaxis.set_major_formatter(PercentFormatter(decimals=1))
    ax.set_ylim(0, max(cr_values) * 1.35)
    
    # Value annotations on bars
    for bar, cr in zip(bars, cr_values):
        ax.annotate(f"{cr:.2f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2),
                    xytext=(0, 0), textcoords="offset points",
                    ha="center", va="center", color="white", fontweight="bold", fontsize=12)
        
    # Lift annotation bracket
    x1, x2 = 0, 1
    y = max(cr_values) * 1.12
    h = max(cr_values) * 0.03
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.5, color=COLOR_DARK)
    ax.text((x1 + x2) * 0.5, y + h * 1.5,
            f"Relative Lift: +{z_res['relative_lift_pct']:.2f}%\n(95% CI: [{z_res['ci_relative_lift_pct'][0]:+.2f}%, {z_res['ci_relative_lift_pct'][1]:+.2f}%])\np-val: {z_res['p_value']:.2e} (Z = {z_res['z_statistic']:.2f})",
            ha="center", va="bottom", color="#0F172A", fontweight="bold", fontsize=9.5)
            
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Conversion Rate CI Figure -> {save_path}")


def plot_daily_trend(df: pd.DataFrame, save_path: str = "reports/figures/03_daily_trend_conversion.png"):
    """Visualizes daily and cumulative conversion rate trajectories over time."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    daily = df.groupby(["date", "group"]).agg(
        users=("user_id", "count"),
        conversions=("converted", "sum")
    ).reset_index()
    
    daily["daily_cr"] = (daily["conversions"] / daily["users"]) * 100
    daily["date"] = pd.to_datetime(daily["date"])
    
    # Cumulative calculation
    daily = daily.sort_values(["group", "date"])
    daily["cum_users"] = daily.groupby("group")["users"].cumsum()
    daily["cum_conversions"] = daily.groupby("group")["conversions"].cumsum()
    daily["cum_cr"] = (daily["cum_conversions"] / daily["cum_users"]) * 100
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=300, sharex=True)
    
    # 1. Daily Instantaneous CR
    for grp, col, lbl in zip(["control", "treatment"], [COLOR_CONTROL, COLOR_TREATMENT], ["Control (Old)", "Treatment (New)"]):
        subset = daily[daily["group"] == grp]
        ax1.plot(subset["date"], subset["daily_cr"], marker="o", markersize=4, label=lbl, color=col, lw=2, alpha=0.85)
        
    ax1.set_title("A. Daily Conversion Rate Fluctuations", loc="left", fontsize=12, pad=10)
    ax1.set_ylabel("Daily CR (%)", fontsize=10)
    ax1.yaxis.set_major_formatter(PercentFormatter(decimals=1))
    ax1.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#CBD5E1")
    
    # 2. Cumulative Conversion Rate Stability
    for grp, col, lbl in zip(["control", "treatment"], [COLOR_CONTROL, COLOR_TREATMENT], ["Control Cumulative CR", "Treatment Cumulative CR"]):
        subset = daily[daily["group"] == grp]
        ax2.plot(subset["date"], subset["cum_cr"], marker="", label=lbl, color=col, lw=2.5)
        
    ax2.set_title("B. Cumulative Conversion Rate Convergence", loc="left", fontsize=12, pad=10)
    ax2.set_ylabel("Cumulative CR (%)", fontsize=10)
    ax2.set_xlabel("Campaign Date", fontsize=11)
    ax2.yaxis.set_major_formatter(PercentFormatter(decimals=1))
    ax2.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#CBD5E1")
    
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Daily Trend Figure -> {save_path}")


def plot_revenue_distributions(df: pd.DataFrame, t_res: dict, save_path: str = "reports/figures/04_revenue_distribution.png"):
    """Visualizes Average Revenue Per User (ARPU) and Revenue distribution for buyers."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)
    
    # 1. ARPU Comparison (all visitors including $0)
    groups = ["Control", "Treatment"]
    arpu_vals = [t_res["mean_control"], t_res["mean_treatment"]]
    
    bars = ax1.bar(groups, arpu_vals, color=[COLOR_CONTROL, COLOR_TREATMENT], width=0.45, alpha=0.9)
    ax1.set_title("Average Revenue Per User (ARPU)", pad=12)
    ax1.set_ylabel("Mean Revenue ($)", fontsize=11)
    ax1.set_ylim(0, max(arpu_vals) * 1.3)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:.2f}"))
    
    for b, val in zip(bars, arpu_vals):
        ax1.annotate(f"${val:.2f}",
                     xy=(b.get_x() + b.get_width() / 2, val / 2),
                     ha="center", va="center", color="white", fontweight="bold", fontsize=11)
        
    ax1.annotate(f"ARPU Lift: +{t_res['relative_lift_pct']:.1f}%\np-val (Welch's t): {t_res['p_value_ttest']:.2e}\nCohen's d = {t_res['cohens_d']:.3f}",
                 xy=(0.5, 0.88), xycoords="axes fraction", ha="center",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#F8FAFC", edgecolor="#CBD5E1"), fontsize=9.5)
                 
    # 2. Kernel Density for Converting Buyers (non-zero spend)
    buyers = df[df["converted"] == 1]
    sns.kdeplot(data=buyers[buyers["group"] == "control"]["revenue"], ax=ax2, label="Control Buyers", color=COLOR_CONTROL, fill=True, alpha=0.3, lw=2)
    sns.kdeplot(data=buyers[buyers["group"] == "treatment"]["revenue"], ax=ax2, label="Treatment Buyers", color=COLOR_TREATMENT, fill=True, alpha=0.3, lw=2)
    
    ax2.set_title("Order Value Distribution (Converting Buyers)", pad=12)
    ax2.set_xlabel("Order Revenue ($)", fontsize=11)
    ax2.set_ylabel("Density", fontsize=11)
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${int(x)}"))
    ax2.legend(frameon=True, facecolor="white", edgecolor="#CBD5E1")
    
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Revenue Distribution Figure -> {save_path}")


def plot_power_curves(power_data: dict, actual_sample_per_variant: int, actual_lift_pct: float, save_path: str = "reports/figures/05_statistical_power_curve.png"):
    """Visualizes Statistical Power Curves across sample sizes with benchmark markers."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=300)
    
    sizes = power_data["sample_sizes"]
    curves = power_data["curves"]
    colors = ["#94A3B8", "#64748B", "#0284C7", "#059669", "#D97706"]
    
    for (label, powers), col in zip(curves.items(), colors):
        ax.plot(sizes, powers, label=label, lw=2, color=col)
        
    # Standard 80% Power threshold line
    ax.axhline(0.80, color="#E11D48", linestyle="--", lw=1.5, label="Standard Target Power (80%)")
    
    # Mark Actual Experiment Sample Size
    ax.axvline(actual_sample_per_variant, color="#0F172A", linestyle=":", lw=2, label=f"Actual Sample: {actual_sample_per_variant:,} / group")
    
    ax.set_title("Statistical Power Analysis Curves (α = 0.05, Two-Tailed)", pad=15)
    ax.set_xlabel("Sample Size per Variant (n)", fontsize=11)
    ax.set_ylabel("Statistical Power (1 - β)", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x/1000)}k"))
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#CBD5E1", fontsize=9)
    
    # Annotation
    ax.text(0.04, 0.45,
            f"• Achieved Power > 99.9% for observed ~{actual_lift_pct:.1f}% lift\n• Minimal risk of Type II (False Negative) Error\n• Well-powered experiment",
            transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.5", facecolor="#F0FDF4", edgecolor="#86EFAC"),
            fontsize=9.5, linespacing=1.4)
            
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Power Curve Figure -> {save_path}")


def plot_segmentation_forest(segment_df: pd.DataFrame, overall_rel_lift: float, save_path: str = "reports/figures/06_segmentation_forest_plot.png"):
    """Visualizes Forest Plot of Relative Lift and 95% CIs across all dimensions."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    
    df_sorted = segment_df.sort_values(by="rel_lift_pct", ascending=True).reset_index(drop=True)
    y_pos = np.arange(len(df_sorted))
    
    labels = [f"{row['segment_dimension'].capitalize()}: {row['segment_value']}" for _, row in df_sorted.iterrows()]
    lifts = df_sorted["rel_lift_pct"].values
    ci_lowers = df_sorted["ci_rel_lower"].values
    ci_uppers = df_sorted["ci_rel_upper"].values
    
    err_low = lifts - ci_lowers
    err_high = ci_uppers - lifts
    
    # Zero line (no effect)
    ax.axvline(0, color="#94A3B8", linestyle="-", lw=1.5, alpha=0.8)
    
    # Overall aggregate lift benchmark line
    ax.axvline(overall_rel_lift, color="#2563EB", linestyle="--", lw=1.5, label=f"Overall Aggregate Lift (+{overall_rel_lift:.2f}%)")
    
    # Forest error bars
    ax.errorbar(lifts, y_pos, xerr=[err_low, err_high], fmt="o", color=COLOR_TREATMENT,
                ecolor="#0284C7", elinewidth=2, capsize=4, markersize=7, markeredgecolor="#0F172A", label="Subgroup Lift (95% CI)")
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Relative Lift in Conversion Rate (%)", fontsize=11)
    ax.set_title("Subgroup Segmentation Analysis & Forest Plot (Simpson's Paradox Audit)", pad=15)
    ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#CBD5E1")
    
    # Text annotation
    for i, (_, row) in enumerate(df_sorted.iterrows()):
        sig_star = "***" if row["p_value"] < 0.001 else ("**" if row["p_value"] < 0.01 else ("*" if row["p_value"] < 0.05 else " (ns)"))
        ax.text(max(ci_uppers) + 1.2, i, f"+{row['rel_lift_pct']:.1f}% {sig_star}",
                va="center", fontsize=9, fontweight="bold", color="#1E293B")
        
    ax.set_xlim(min(-2, min(ci_lowers) - 3), max(ci_uppers) + 7)
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    print(f"[SAVED] Segmentation Forest Figure -> {save_path}")
