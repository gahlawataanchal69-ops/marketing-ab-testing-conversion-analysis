# 📖 Data Dictionary — A/B Testing Telemetry & Summary Datasets

## 1. Primary Table: `ab_test_cleaned.csv`
Granularity: **One row per unique user exposure** (74,513 rows).

| Column Name | Data Type | Description | Example Values |
|:---|:---|:---|:---|
| `user_id` | Text (String) | Unique alphanumeric user identifier | `USR_000142`, `USR_049102` |
| `timestamp` | Datetime | Exact UTC timestamp of landing page session | `2025-10-04 14:22:10` |
| `group` | Text (Categorical) | Assigned variant group (`control` vs `treatment`) | `control`, `treatment` |
| `landing_page` | Text (Categorical) | Landing page variant served | `old_landing_page`, `new_landing_page` |
| `device` | Text (Categorical) | Client device used during the visit | `Mobile`, `Desktop`, `Tablet` |
| `campaign_channel` | Text (Categorical) | Inbound marketing acquisition channel | `Social Ads`, `Search (PPC)`, `Email Campaign`, `Organic / Direct` |
| `user_tier` | Text (Categorical) | Customer relationship status | `New Visitor`, `Returning Customer`, `VIP / Loyalty` |
| `region` | Text (Categorical) | User geographic market | `North America`, `Europe`, `Asia Pacific`, `Latin America` |
| `session_duration_sec` | Decimal (Float) | Total time spent on landing page / site (seconds) | `142.5`, `310.2` |
| `converted` | Integer (Binary 0/1) | Primary conversion outcome (1 = converted/signed up, 0 = bounced) | `0`, `1` |
| `orders_count` | Integer | Total orders placed in session (0 for non-converters) | `0`, `1`, `2`, `3` |
| `revenue` | Decimal (Currency) | Total monetary spend generated during session ($) | `0.00`, `64.50`, `112.20` |
| `date` | Date | Partition date of the session | `2025-10-04` |

---

## 2. Pre-Aggregated Table: `ab_test_daily_metrics.csv`
Granularity: **Daily metrics grouped by variant and segment dimensions**.

| Column Name | Data Type | Description |
|:---|:---|:---|
| `date` | Date | Experiment calendar date |
| `group` | Text | `control` or `treatment` |
| `device` | Text | Device category |
| `campaign_channel` | Text | Inbound marketing channel |
| `region` | Text | Geographic market |
| `user_tier` | Text | Customer cohort status |
| `visitors` | Integer | Total unique user count |
| `conversions` | Integer | Total converted users |
| `total_orders` | Integer | Total orders count |
| `total_revenue` | Decimal | Gross revenue ($) |
| `avg_session_duration` | Decimal | Mean session duration (sec) |

---

## 3. Subgroup Summary Table: `ab_test_segment_summary.csv`
Contains calculated metrics and two-proportion z-test statistics across all segment values.

| Field | Description |
|:---|:---|
| `segment_dimension` | Dimension name (`device`, `campaign_channel`, `region`, `user_tier`) |
| `segment_value` | Specific category value |
| `n_control` / `n_treatment` | Sample size in control / treatment |
| `cr_control_pct` / `cr_treatment_pct` | Conversion rates (%) |
| `abs_lift_pct` / `rel_lift_pct` | Absolute & relative conversion lifts (%) |
| `ci_rel_lower` / `ci_rel_upper` | 95% Confidence Interval for relative lift |
| `z_statistic` / `p_value` | Two-proportion Z-test statistics |
| `is_significant` | Boolean flag indicating $p < 0.05$ |
