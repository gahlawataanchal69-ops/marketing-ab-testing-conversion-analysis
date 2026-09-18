"""
Power Analysis and Sample Size Estimation Module.

Provides:
- Minimum Sample Size calculation per variant for two-proportion A/B tests.
- Minimum Detectable Effect (MDE) calculations.
- Post-hoc achieved statistical power calculation.
- Power curve generation across variable sample sizes and effect sizes.
"""

from typing import Dict, Any, List
import numpy as np
from scipy import stats
import statsmodels.stats.api as sms

def calculate_required_sample_size(
    baseline_cr: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
    ratio: float = 1.0
) -> Dict[str, Any]:
    """
    Calculates the required sample size per variant for a two-proportion test.
    
    Parameters:
    -----------
    baseline_cr : float
        Current control group baseline conversion rate (e.g. 0.10 for 10%).
    mde_relative : float
        Minimum Detectable Effect as a relative change (e.g. 0.05 for +5% lift).
    alpha : float
        Significance level (Type I error rate, default 0.05).
    power : float
        Statistical power (1 - Type II error rate, default 0.80).
    ratio : float
        Ratio of treatment to control sample sizes (default 1.0 for 50/50 split).
        
    Returns:
    --------
    dict : Detailed sizing breakdown.
    """
    p1 = baseline_cr
    p2 = baseline_cr * (1 + mde_relative)
    
    # Standard formula using normal approximation
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    
    p_avg = (p1 + p2) / 2
    
    # Sizing per variant
    num = (z_alpha * np.sqrt(2 * p_avg * (1 - p_avg)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    den = (p2 - p1) ** 2
    n_per_variant = int(np.ceil(num / den))
    total_n = int(n_per_variant * 2)
    
    # Also verify with statsmodels effect size (Cohen's h)
    effect_size = sms.proportion_effectsize(p1, p2)
    sm_n = sms.NormalIndPower().solve_power(
        effect_size=abs(effect_size),
        power=power,
        alpha=alpha,
        ratio=ratio,
        alternative="two-sided"
    )
    
    return {
        "baseline_conversion_rate": baseline_cr,
        "treatment_target_cr": round(p2, 5),
        "mde_relative_pct": round(mde_relative * 100, 2),
        "mde_absolute_pct": round((p2 - p1) * 100, 3),
        "significance_level_alpha": alpha,
        "statistical_power_target": power,
        "cohens_h_effect_size": round(float(effect_size), 5),
        "required_n_per_variant": n_per_variant,
        "required_total_sample_size": total_n,
        "statsmodels_n_per_variant": int(np.ceil(sm_n))
    }


def calculate_achieved_power(
    n_ctrl: int,
    n_treat: int,
    cr_ctrl: float,
    cr_treat: float,
    alpha: float = 0.05
) -> float:
    """
    Calculates post-hoc achieved statistical power given observed sample sizes and proportions.
    """
    effect_size = sms.proportion_effectsize(cr_ctrl, cr_treat)
    ratio = n_treat / n_ctrl
    power = sms.NormalIndPower().power(
        effect_size=abs(effect_size),
        nobs1=n_ctrl,
        alpha=alpha,
        ratio=ratio,
        alternative="two-sided"
    )
    return float(power)


def generate_power_curve_data(
    baseline_cr: float = 0.105,
    relative_lifts: List[float] = [0.03, 0.05, 0.08, 0.10, 0.15],
    sample_sizes: np.ndarray = None,
    alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Generates data matrix for plotting statistical power vs sample size across multiple lifts.
    """
    if sample_sizes is None:
        sample_sizes = np.linspace(2_000, 100_000, 50, dtype=int)
        
    power_curves = {}
    for lift in relative_lifts:
        p2 = baseline_cr * (1 + lift)
        effect_size = sms.proportion_effectsize(baseline_cr, p2)
        powers = [
            sms.NormalIndPower().power(
                effect_size=abs(effect_size),
                nobs1=n,
                alpha=alpha,
                ratio=1.0,
                alternative="two-sided"
            )
            for n in sample_sizes
        ]
        power_curves[f"{int(lift*100)}% Relative Lift"] = powers
        
    return {
        "sample_sizes": sample_sizes.tolist(),
        "curves": power_curves
    }
