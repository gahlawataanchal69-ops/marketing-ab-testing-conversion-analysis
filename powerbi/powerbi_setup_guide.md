# 📊 Power BI & Tableau Implementation Guide

## 1. Quick Setup in Power BI Desktop
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV** -> Select `data/processed/ab_test_cleaned.csv` and `data/processed/ab_test_daily_metrics.csv`.
3. In **Power Query Editor**:
   - Ensure `timestamp` is parsed as `DateTime`.
   - Ensure `date` is parsed as `Date`.
   - Ensure `converted` is parsed as `Whole Number (0/1)`.
   - Ensure `revenue` and `session_duration_sec` are parsed as `Decimal Number`.
4. Click **Close & Apply**.
5. Create a new Measures table and paste the DAX formulas from [`powerbi_dax_measures.dax`](./powerbi_dax_measures.dax).

---

## 2. Recommended Report Visual Layout (4-Card Executive View)
- **Top KPI Scorecard Band**:
  - *Card 1*: Total Sample Size ($N = 74,513$) with SRM Status badge (`No SRM Detected, p = 0.51`).
  - *Card 2*: Control vs Treatment Conversion Rate ($13.01\%$ vs $14.45\%$).
  - *Card 3*: Relative Lift ($+11.06\%$ [95% CI: $+7.26\%$ to $+14.86\%$], $Z = 5.71, p < 0.0001$).
  - *Card 4*: Average Revenue Per User (ARPU) Lift ($+9.85\%$, Control: $\$8.18$ vs Treatment: $\$8.99$, $p < 0.0001$).
- **Visual 1 (Top Left - Line Chart)**: Daily Cumulative Conversion Rate over the 30-day experiment showing steady convergence of Treatment over Control.
- **Visual 2 (Top Right - Clustered Bar Chart)**: Conversion Rate by Marketing Channel with error bars (Wilson 95% CIs).
- **Visual 3 (Bottom Left - Matrix / Heatmap)**: Conversion Rate by Device Type (Mobile vs Desktop vs Tablet) demonstrating positive lift across all hardware form factors.
- **Visual 4 (Bottom Right - Gauge / Donut)**: Statistical Power Gauge ($99.99\%$ achieved power) & Risk / Decision Matrix.
- **Slicers (Interactive Filters)**:
  - Date Range slider
  - Device selector (`Mobile`, `Desktop`, `Tablet`)
  - Marketing Channel selector
  - User Tier selector

---

## 3. Tableau Public Publishing Workflow
1. Connect to `data/processed/ab_test_daily_metrics.csv`.
2. Create calculated fields for `Conversion Rate = SUM([Conversions]) / SUM([Visitors])` and `Lift = (ZN([CR Treatment]) - ZN([CR Control])) / ZN([CR Control])`.
3. Build the story dashboard matching the visual wireframe.
4. Publish to **Tableau Public** and embed the public link in your portfolio!
