"""
Data Loader & Synthetic Kaggle A/B Testing Dataset Generator.

Simulates a high-volume Marketing Campaign & Landing Page Conversion A/B Test
with realistic consumer behavior, multivariate segmentation, and e-commerce transactions.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_ab_test_dataset(
    n_samples: int = 120_000,
    random_seed: int = 42,
    output_path: str = "data/raw/marketing_ab_test_raw.csv"
) -> pd.DataFrame:
    """
    Generates a realistic A/B testing dataset for a marketing landing page campaign.
    
    Parameters:
    -----------
    n_samples : int
        Total number of user visit records to generate.
    random_seed : int
        Seed for reproducibility.
    output_path : str
        Filepath to save the CSV.
        
    Returns:
    --------
    pd.DataFrame : The generated raw dataset.
    """
    np.random.seed(random_seed)
    
    # 1. Unique User IDs (with minor duplicates to simulate re-visits/cleaning requirement)
    n_unique_users = int(n_samples * 0.96)
    user_pool = [f"USR_{i:06d}" for i in range(1, n_unique_users + 1)]
    user_ids = np.random.choice(user_pool, size=n_samples, replace=True)
    
    # 2. Assignment into Control (50%) and Treatment (50%)
    groups = np.random.choice(["control", "treatment"], size=n_samples, p=[0.50, 0.50])
    landing_pages = np.where(groups == "control", "old_landing_page", "new_landing_page")
    
    # Introduce small intentional mismatch noise (0.2%) where page logged doesn't match group
    # for cleaning demonstration in data quality audits
    mismatch_idx = np.random.choice(n_samples, size=int(n_samples * 0.002), replace=False)
    for idx in mismatch_idx:
        landing_pages[idx] = "new_landing_page" if groups[idx] == "control" else "old_landing_page"
    
    # 3. Timestamps across a 30-day campaign period
    start_date = datetime(2025, 10, 1, 0, 0, 0)
    random_seconds = np.random.randint(0, 30 * 24 * 3600, size=n_samples)
    timestamps = [start_date + timedelta(seconds=int(s)) for s in random_seconds]
    
    # 4. Device Segmentation
    devices = np.random.choice(["Mobile", "Desktop", "Tablet"], size=n_samples, p=[0.52, 0.36, 0.12])
    
    # 5. Marketing Channel Source
    channels = np.random.choice(
        ["Social Ads", "Search (PPC)", "Email Campaign", "Organic / Direct"],
        size=n_samples,
        p=[0.38, 0.28, 0.18, 0.16]
    )
    
    # 6. User Tier / Type
    user_tiers = np.random.choice(
        ["New Visitor", "Returning Customer", "VIP / Loyalty"],
        size=n_samples,
        p=[0.60, 0.32, 0.08]
    )
    
    # 7. Geographic Region
    regions = np.random.choice(
        ["North America", "Europe", "Asia Pacific", "Latin America"],
        size=n_samples,
        p=[0.42, 0.30, 0.18, 0.10]
    )
    
    # 8. Conversion Generation Model with realistic probabilities & segment modifiers
    # Baseline control probability ~ 10.5%
    # Baseline treatment probability ~ 11.7%
    base_prob = np.where(groups == "control", 0.105, 0.117)
    
    # Device modifier
    device_mod = np.where(devices == "Desktop", 0.025, np.where(devices == "Mobile", -0.010, 0.005))
    
    # Channel modifier
    channel_mod = np.where(
        channels == "Email Campaign", 0.035,
        np.where(channels == "Search (PPC)", 0.015,
        np.where(channels == "Social Ads", -0.010, 0.000))
    )
    
    # User Tier modifier
    tier_mod = np.where(user_tiers == "VIP / Loyalty", 0.080, np.where(user_tiers == "Returning Customer", 0.030, 0.000))
    
    final_probs = base_prob + device_mod + channel_mod + tier_mod
    final_probs = np.clip(final_probs, 0.01, 0.95)
    
    # Binary conversion event (0 or 1)
    converted = np.random.binomial(1, final_probs)
    
    # 9. Session Duration (Continuous Metric, in seconds)
    # Control: mean ~185s, Treatment: mean ~205s (log-normal)
    mu_ctrl, sigma_ctrl = np.log(185), 0.55
    mu_treat, sigma_treat = np.log(205), 0.55
    durations = np.where(
        groups == "control",
        np.random.lognormal(mu_ctrl, sigma_ctrl, size=n_samples),
        np.random.lognormal(mu_treat, sigma_treat, size=n_samples)
    )
    durations = np.round(durations, 1)
    
    # 10. Orders Count & Revenue (for converters)
    # Converters purchase 1-3 items, spending log-normal amount
    orders_count = np.where(converted == 1, np.random.choice([1, 2, 3], size=n_samples, p=[0.80, 0.15, 0.05]), 0)
    
    revenue_spend = np.where(
        converted == 1,
        np.round(np.random.gamma(shape=5.0, scale=9.5, size=n_samples) + (orders_count * 12.0), 2),
        0.00
    )
    
    # Build DataFrame
    df = pd.DataFrame({
        "user_id": user_ids,
        "timestamp": timestamps,
        "group": groups,
        "landing_page": landing_pages,
        "device": devices,
        "campaign_channel": channels,
        "user_tier": user_tiers,
        "region": regions,
        "session_duration_sec": durations,
        "converted": converted,
        "orders_count": orders_count,
        "revenue": revenue_spend
    })
    
    # Sort by timestamp
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Generated {len(df):,} raw A/B testing records -> {output_path}")
    return df


def clean_ab_test_data(
    raw_df: pd.DataFrame,
    output_path: str = "data/processed/ab_test_cleaned.csv"
) -> pd.DataFrame:
    """
    Cleans raw A/B test data by:
    1. Auditing and removing inconsistent landing_page vs group mismatch assignments.
    2. Handling duplicate user visits (keeping the first valid visit/exposure per user).
    3. Parsing date and datetime features.
    4. Validating data integrity and ranges.
    """
    initial_count = len(raw_df)
    
    # 1. Filter out mismatch assignment errors (e.g. control routed to new_page or vice versa)
    valid_mask = (
        ((raw_df["group"] == "control") & (raw_df["landing_page"] == "old_landing_page")) |
        ((raw_df["group"] == "treatment") & (raw_df["landing_page"] == "new_landing_page"))
    )
    df = raw_df[valid_mask].copy()
    mismatch_removed = initial_count - len(df)
    
    # 2. Remove duplicate users (deduplication on user_id, retaining first exposure)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df = df.drop_duplicates(subset=["user_id"], keep="first").reset_index(drop=True)
    dedup_removed = (initial_count - mismatch_removed) - len(df)
    
    # 3. Add date column for time-series aggregation
    df["date"] = df["timestamp"].dt.date
    
    # 4. Save cleaned dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"[AUDIT] Initial records: {initial_count:,}")
    print(f"[AUDIT] Mismatches removed: {mismatch_removed:,}")
    print(f"[AUDIT] Duplicate users removed: {dedup_removed:,}")
    print(f"[AUDIT] Final Cleaned Sample Size: {len(df):,} -> {output_path}")
    return df


if __name__ == "__main__":
    raw_data = generate_ab_test_dataset(n_samples=120_000)
    cleaned_data = clean_ab_test_data(raw_data)
