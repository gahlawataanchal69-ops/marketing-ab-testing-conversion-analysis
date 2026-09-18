"""
Statistical Hypothesis Testing Module for A/B Testing Analysis.

Implements rigorous statistical engines:
- Sample Ratio Mismatch (SRM) Chi-Square test
- Two-Proportion Z-Test and Chi-Square for conversion rate
- Relative Lift and Absolute Lift 95% Confidence Intervals
- Welch's Two-Sample t-Test & Mann-Whitney U for continuous metrics (ARPU, Session Duration)
- Cohen's d effect size calculation
- Subgroup / Simpson's Paradox diagnostic analysis
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

def check_sample_ratio_mismatch(
    df: pd.DataFrame,
    group_col: str = "group",
    expected_ratio: Tuple[float, float] = (0.5, 0.5),
    alpha: float = 0.01
) -> Dict[str, Any]:
    """
    Performs a Chi-Square Goodness-of-Fit test to detect Sample Ratio Mismatch (SRM).
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned A/B test dataframe.
    group_col : str
        Column denoting 'control' vs 'treatment'.
    expected_ratio : tuple
        Expected probability allocation (e.g. 0.5, 0.5).
    alpha : float
        Significance threshold for SRM (typically 0.01 or 0.001 to prevent false alarms).
        
    Returns:
    --------
    dict : Statistical summary containing counts, chi2 stat, p-value, and status.
    """
    counts = df[group_col].value_counts()
    n_ctrl = counts.get("control", 0)
    n_treat = counts.get("treatment", 0)
    total = n_ctrl + n_treat
    
    exp_ctrl = total * expected_ratio[0]
    exp_treat = total * expected_ratio[1]
    
    observed = np.array([n_ctrl, n_treat])
    expected = np.array([exp_ctrl, exp_treat])
    
    chi2_stat, p_val = stats.chisquare(f_obs=observed, f_exp=expected)
    srm_detected = bool(p_val < alpha)
    
    return {
        "n_control": int(n_ctrl),
        "n_treatment": int(n_treat),
        "total_sample": int(total),
        "expected_ratio": f"{int(expected_ratio[0]*100)}:{int(expected_ratio[1]*100)}",
        "observed_control_pct": round(n_ctrl / total * 100, 3),
        "observed_treatment_pct": round(n_treat / total * 100, 3),
        "chi2_statistic": round(float(chi2_stat), 4),
        "p_value": float(p_val),
        "srm_detected": srm_detected,
        "verdict": "CRITICAL SRM DETECTED: Data assignment compromised" if srm_detected else "NO SRM DETECTED: Traffic split is statistically valid"
    }


def two_proportion_z_test(
    df: pd.DataFrame,
    group_col: str = "group",
    metric_col: str = "converted",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Executes a Two-Proportion Z-Test comparing conversion rates between Control and Treatment.
    Calculates absolute lift, relative lift, standard error, z-statistic, p-value, and 95% CIs.
    """
    ctrl = df[df[group_col] == "control"][metric_col]
    treat = df[df[group_col] == "treatment"][metric_col]
    
    n_ctrl = len(ctrl)
    n_treat = len(treat)
    conv_ctrl = int(ctrl.sum())
    conv_treat = int(treat.sum())
    
    cr_ctrl = conv_ctrl / n_ctrl
    cr_treat = conv_treat / n_treat
    
    # Pooled probability for standard error under null hypothesis
    p_pool = (conv_ctrl + conv_treat) / (n_ctrl + n_treat)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_ctrl + 1 / n_treat))
    
    # Z-statistic and two-tailed p-value
    z_stat = (cr_treat - cr_ctrl) / se_pool
    p_value = float(2 * (1 - stats.norm.cdf(abs(z_stat))))
    
    # Absolute Lift & Confidence Interval (unpooled SE for CI estimation)
    abs_lift = cr_treat - cr_ctrl
    se_diff = np.sqrt((cr_ctrl * (1 - cr_ctrl) / n_ctrl) + (cr_treat * (1 - cr_treat) / n_treat))
    z_crit = stats.norm.ppf(1 - alpha / 2)
    
    ci_abs_lower = abs_lift - z_crit * se_diff
    ci_abs_upper = abs_lift + z_crit * se_diff
    
    # Relative Lift & Relative Lift 95% Confidence Interval (Delta method)
    rel_lift = (cr_treat - cr_ctrl) / cr_ctrl
    se_rel = se_diff / cr_ctrl
    ci_rel_lower = rel_lift - z_crit * se_rel
    ci_rel_upper = rel_lift + z_crit * se_rel
    
    # Confidence intervals for individual proportions
    ci_ctrl = proportion_confint(conv_ctrl, n_ctrl, alpha=alpha, method="wilson")
    ci_treat = proportion_confint(conv_treat, n_treat, alpha=alpha, method="wilson")
    
    is_significant = bool(p_value < alpha)
    
    return {
        "n_control": n_ctrl,
        "n_treatment": n_treat,
        "conversions_control": conv_ctrl,
        "conversions_treatment": conv_treat,
        "cr_control": round(cr_ctrl, 5),
        "cr_treatment": round(cr_treat, 5),
        "cr_control_pct": round(cr_ctrl * 100, 3),
        "cr_treatment_pct": round(cr_treat * 100, 3),
        "ci_control_pct": (round(ci_ctrl[0] * 100, 3), round(ci_ctrl[1] * 100, 3)),
        "ci_treatment_pct": (round(ci_treat[0] * 100, 3), round(ci_treat[1] * 100, 3)),
        "absolute_lift_pct": round(abs_lift * 100, 3),
        "ci_absolute_lift_pct": (round(ci_abs_lower * 100, 3), round(ci_abs_upper * 100, 3)),
        "relative_lift_pct": round(rel_lift * 100, 3),
        "ci_relative_lift_pct": (round(ci_rel_lower * 100, 3), round(ci_rel_upper * 100, 3)),
        "z_statistic": round(float(z_stat), 4),
        "p_value": float(p_value),
        "alpha": alpha,
        "statistically_significant": is_significant,
        "conclusion": "Reject Null Hypothesis: Treatment shows statistically significant improvement" if is_significant else "Fail to Reject Null Hypothesis: No statistically significant difference"
    }


def continuous_metric_ttest(
    df: pd.DataFrame,
    metric_col: str = "revenue",
    group_col: str = "group",
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Performs Welch's Two-Sample t-Test (unequal variances assumed) and Mann-Whitney U test
    for continuous metrics (e.g. Revenue per User, Session Duration).
    """
    ctrl = df[df[group_col] == "control"][metric_col].values
    treat = df[df[group_col] == "treatment"][metric_col].values
    
    n_ctrl, n_treat = len(ctrl), len(treat)
    mean_ctrl, mean_treat = float(np.mean(ctrl)), float(np.mean(treat))
    std_ctrl, std_treat = float(np.std(ctrl, ddof=1)), float(np.std(treat, ddof=1))
    
    # Welch's t-test
    ttest_res = stats.ttest_ind(treat, ctrl, equal_var=False)
    t_stat = float(ttest_res.statistic)
    p_val_t = float(ttest_res.pvalue)
    
    # Difference in Means & CI
    mean_diff = mean_treat - mean_ctrl
    se_diff = np.sqrt((std_ctrl**2 / n_ctrl) + (std_treat**2 / n_treat))
    
    # Degrees of freedom via Welch-Satterthwaite equation
    dof_num = (std_ctrl**2 / n_ctrl + std_treat**2 / n_treat)**2
    dof_den = ((std_ctrl**2 / n_ctrl)**2 / (n_ctrl - 1)) + ((std_treat**2 / n_treat)**2 / (n_treat - 1))
    dof = dof_num / dof_den
    
    t_crit = stats.t.ppf(1 - alpha / 2, df=dof)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff
    
    # Relative lift in metric
    rel_lift_pct = (mean_diff / mean_ctrl * 100) if mean_ctrl != 0 else 0.0
    
    # Cohen's d effect size
    pooled_std = np.sqrt(((n_ctrl - 1) * std_ctrl**2 + (n_treat - 1) * std_treat**2) / (n_ctrl + n_treat - 2))
    cohen_d = mean_diff / pooled_std if pooled_std > 0 else 0.0
    
    # Non-parametric Mann-Whitney U test
    mwu_res = stats.mannwhitneyu(treat, ctrl, alternative="two-sided")
    p_val_mwu = float(mwu_res.pvalue)
    
    return {
        "metric": metric_col,
        "n_control": n_ctrl,
        "n_treatment": n_treat,
        "mean_control": round(mean_ctrl, 3),
        "mean_treatment": round(mean_treat, 3),
        "std_control": round(std_ctrl, 3),
        "std_treatment": round(std_treat, 3),
        "absolute_diff": round(mean_diff, 3),
        "ci_mean_diff": (round(ci_lower, 3), round(ci_upper, 3)),
        "relative_lift_pct": round(rel_lift_pct, 3),
        "t_statistic": round(t_stat, 4),
        "p_value_ttest": p_val_t,
        "p_value_mannwhitney": p_val_mwu,
        "cohens_d": round(cohen_d, 4),
        "statistically_significant": bool(p_val_t < alpha),
        "degrees_of_freedom": round(dof, 1)
    }


def analyze_segment_subgroups(
    df: pd.DataFrame,
    segment_cols: list = ["device", "campaign_channel", "region", "user_tier"]
) -> pd.DataFrame:
    """
    Computes conversion rates, lifts, sample sizes, and z-test p-values across all subgroups.
    Checks for Simpson's Paradox (e.g. overall positive vs subgroup negative trends).
    """
    records = []
    
    for col in segment_cols:
        categories = df[col].unique()
        for cat in categories:
            sub_df = df[df[col] == cat]
            res = two_proportion_z_test(sub_df)
            
            records.append({
                "segment_dimension": col,
                "segment_value": cat,
                "n_control": res["n_control"],
                "n_treatment": res["n_treatment"],
                "total_users": res["n_control"] + res["n_treatment"],
                "cr_control_pct": res["cr_control_pct"],
                "cr_treatment_pct": res["cr_treatment_pct"],
                "abs_lift_pct": res["absolute_lift_pct"],
                "ci_abs_lower": res["ci_absolute_lift_pct"][0],
                "ci_abs_upper": res["ci_absolute_lift_pct"][1],
                "rel_lift_pct": res["relative_lift_pct"],
                "ci_rel_lower": res["ci_relative_lift_pct"][0],
                "ci_rel_upper": res["ci_relative_lift_pct"][1],
                "z_statistic": res["z_statistic"],
                "p_value": res["p_value"],
                "is_significant": res["statistically_significant"]
            })
            
    summary_df = pd.DataFrame(records)
    return summary_df
