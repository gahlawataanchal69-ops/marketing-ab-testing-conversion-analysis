# 🎯 A/B Test Analysis: Marketing Campaign & Landing Page Conversion Optimization

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Statsmodels](https://img.shields.io/badge/Statsmodels-0.14+-005571)](https://www.statsmodels.org/)
[![PowerBI](https://img.shields.io/badge/Power_BI-Interactive_Dashboard-F2C811?logo=powerbi&logoColor=black)](./powerbi/)
[![Status](https://img.shields.io/badge/Experiment_Status-SHIP_VARIANT_B-22C55E)](#-ship--no-ship-recommendation)

---

## 📌 1. Project Overview & Business Problem

An e-commerce company launched an A/B test on their primary paid marketing acquisition landing page to evaluate whether a redesigned user experience (Variant B / Treatment) with streamlined navigation, social proof badges, and enhanced value proposition improves visitor conversion rate and average revenue per user over the incumbent baseline (Variant A / Control).

### 🎯 Key Business Questions
1. **Conversion Lift**: Does the new landing page statistically significantly increase visitor-to-customer conversion rate ($CR$)?
2. **Revenue Impact**: Does the new design increase Average Revenue Per User ($ARPU$) without degrading average order value?
3. **Validity & Power**: Was the test adequately powered, and is there any evidence of Sample Ratio Mismatch ($SRM$)?
4. **Subgroup Consistency**: Is the lift consistent across devices (Mobile vs. Desktop), marketing channels, and user tiers, or is there evidence of **Simpson's Paradox**?
5. **Decision**: Based on statistical and practical significance, should we **Ship (100% rollout)** or **No-Ship**?

---

## 🔬 2. Hypotheses Formulation & Statistical Methodology

### A. Primary Metric: Conversion Rate ($CR$)
- **Null Hypothesis ($H_0$)**: The new landing page does not increase conversion rate ($p_{\text{treatment}} \le p_{\text{control}}$).
- **Alternative Hypothesis ($H_1$)**: The new landing page significantly increases conversion rate ($p_{\text{treatment}} > p_{\text{control}}$).
- **Statistical Test**: **Two-Proportion Z-Test** (pooled variance) with **95% Wilson Score Confidence Intervals**.
- **Significance Level**: $\alpha = 0.05$ (two-tailed).

### B. Secondary Continuous Metrics: ARPU ($Revenue / Visitor$) & Session Duration
- **Null Hypothesis ($H_0$)**: $\mu_{\text{treatment}} = \mu_{\text{control}}$
- **Alternative Hypothesis ($H_1$)**: $\mu_{\text{treatment}} \neq \mu_{\text{control}}$
- **Statistical Test**: **Welch's Two-Sample t-Test** (robust to unequal variances) & **Mann-Whitney U** rank-sum test.

### C. Experimental Guardrail: Sample Ratio Mismatch ($SRM$)
- **Test**: **Chi-Square Goodness-of-Fit ($\chi^2$)** test comparing observed vs. expected 50:50 traffic allocation at $\alpha = 0.01$.

---

## 📊 3. Key Statistical Findings & Test Results

| Experiment Metric | Control (Old Page) | Treatment (New Page) | Absolute Lift | Relative Lift | 95% Confidence Interval | Test Statistic | P-Value | Statistical Verdict |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Sample Size ($N$)** | 37,166 (49.88%) | 37,347 (50.12%) | +181 | — | — | $\chi^2 = 0.4397$ | $p = 0.5073$ | **Passed (No SRM)** |
| **Conversion Rate (CR)** | **13.01%** | **14.45%** | **+1.44%** | **+11.06%** | **[+7.26%, +14.86%]** | $Z = 5.7069$ | **$1.15 \times 10^{-8}$** | **Statistically Significant ($p < 0.001$)** |
| **ARPU (Revenue/User)** | **$8.18** | **$8.99** | **+$0.81** | **+9.85%** | **[+$0.47, +$1.14]** | $t = 4.7758$ | **$1.79 \times 10^{-6}$** | **Statistically Significant ($p < 0.001$)** |
| **Session Duration** | 214.8 sec | 239.6 sec | +24.9 sec | +11.58% | [+23.0s, +26.8s] | $t = 25.40$ | $p < 10^{-100}$ | **Statistically Significant ($p < 0.001$)** |

---

## ⚡ 4. Statistical Power & Sample Size Analysis

- **Pre-Experiment Sizing (MDE = 5% Relative Lift)**: Required $n = 42,876$ users/variant ($\alpha = 0.05, 1 - \beta = 0.80$).
- **Pre-Experiment Sizing (MDE = 10% Relative Lift)**: Required $n = 10,939$ users/variant.
- **Actual Experiment Sample Size**: **$37,166$ users in Control** and **$37,347$ users in Treatment** (Total: **$74,513$ users**).
- **Post-Hoc Achieved Statistical Power**: **$99.99\%$** for the observed $+11.06\%$ conversion lift.
- **Conclusion**: The test was robustly powered, with virtually zero risk of Type II (false negative) error.

```
Statistical Power vs Sample Size Curves:
-----------------------------------------------------------------------------------
Lift       | N=5,000 | N=10,000 | N=20,000 | N=37,166 (Actual) | Target (80%)
-----------------------------------------------------------------------------------
3% Lift    |  7.2%   |   9.8%   |  15.1%   |     24.2%         | Underpowered
5% Lift    | 12.4%   |  20.1%   |  35.2%   |     73.1%         | Adequate
10% Lift   | 32.5%   |  57.8%   |  86.4%   |     99.4%         | Highly Powered
11% (Obs)  | 38.1%   |  65.2%   |  92.1%   |     99.99%        | EXTREMELY ROBUST
-----------------------------------------------------------------------------------
```

---

## 🔍 5. Segmentation & Simpson's Paradox Audit

To ensure the aggregate conversion lift wasn't an artifact of composition bias (**Simpson's Paradox**), we sliced performance across four key dimensions:

1. **Device Form Factor**:
   - **Desktop**: $+11.04\%$ Lift ($17.1\%$ vs $15.4\%$, $p < 0.001$)
   - **Mobile**: $+10.92\%$ Lift ($13.2\%$ vs $11.9\%$, $p < 0.001$)
   - **Tablet**: $+11.19\%$ Lift ($14.9\%$ vs $13.4\%$, $p < 0.001$)
2. **Marketing Channels**: Positive lift across all acquisition streams: Email ($+11.0\%$), Search PPC ($+11.3\%$), Direct ($+11.5\%$), Social Ads ($+10.8\%$).
3. **User Tiers**: Highest lift observed in **VIP / Loyalty** customers ($+13.8\%$) and **New Visitors** ($+10.9\%$).
4. **Simpson's Paradox Conclusion**: **PASSED**. The treatment effect direction is positive and consistent across all sub-populations.

---

## 📈 6. Key Visualizations

| Diagnostic / Figure | Description |
|:---|:---|
| **[01_srm_check.png](reports/figures/01_srm_check.png)** | Sample Ratio Mismatch check ($49.88\%$ vs $50.12\%$, $\chi^2 = 0.44, p = 0.51$). |
| **[02_conversion_rate_ci.png](reports/figures/02_conversion_rate_ci.png)** | Conversion Rate bar chart with 95% Wilson Score confidence intervals. |
| **[03_daily_trend_conversion.png](reports/figures/03_daily_trend_conversion.png)** | Daily instantaneous and cumulative conversion rate convergence over 30 days. |
| **[04_revenue_distribution.png](reports/figures/04_revenue_distribution.png)** | ARPU comparison and log-transformed order spend distributions. |
| **[05_statistical_power_curve.png](reports/figures/05_statistical_power_curve.png)** | Power vs. sample size sizing curves across variable MDEs. |
| **[06_segmentation_forest_plot.png](reports/figures/06_segmentation_forest_plot.png)** | Forest plot with 95% CIs across all dimensions confirming no Simpson's Paradox. |

---

## 💼 7. Practical Significance & Business Impact (ROI)

Statistical significance alone is insufficient to justify deployment costs. We conducted a practical financial ROI assessment:

- **Baseline Monthly Traffic**: ~150,000 unique landing page visitors.
- **Incremental Conversions**: $+1.44\%$ absolute lift $\rightarrow$ **$+2,160$ additional monthly customers**.
- **Incremental Revenue**: $+9.85\%$ ARPU lift ($\approx +\$0.81$ per visitor) $\rightarrow$ **$+\$121,500$ incremental gross revenue per month**.
- **Annualized Projected Value**: **$\approx \mathbf{\$1.458\text{ Million ARR}}$**.
- **Implementation & Infrastructure Cost**: $<\$25,000$ one-time engineering & QA cost.
- **Payback Period**: Less than **7 business days**.

---

## 🚀 8. Ship / No-Ship Recommendation

### 🟢 FINAL DECISION: SHIP TO 100% TRAFFIC (FULL ROLLOUT)

#### Justification:
1. **Statistical Certainty**: The conversion lift is decisive ($p = 1.15 \times 10^{-8}$) with zero SRM anomaly.
2. **Economic Viability**: The $+9.85\%$ lift in ARPU proves users are not merely converting on discounted items, but generating substantial incremental gross merchandise value ($+\$1.458\text{M}$ ARR).
3. **Uniform User Experience**: No device or regional cohort experienced conversion degradation.
4. **Engagement Uplift**: Session duration increased by $+11.58\%$, reflecting higher browsing engagement and lower friction.

---

## 💻 9. Interactive Power BI / Tableau Dashboard

- **Standalone Interactive Dashboard**: Open [`powerbi/dashboard_mockup.html`](./powerbi/dashboard_mockup.html) in any browser to explore the live interactive dashboard with Chart.js and KPI scorecards.
- **Power BI Setup & DAX Library**: Follow the step-by-step setup guide in [`powerbi/powerbi_setup_guide.md`](./powerbi/powerbi_setup_guide.md) with production DAX formulas in [`powerbi/powerbi_dax_measures.dax`](./powerbi/powerbi_dax_measures.dax).

---

## 📂 10. Repository Structure

```
market project/
│
├── README.md                               <- Executive project summary & statistical report
├── requirements.txt                        <- Python environment dependencies
├── .gitignore                              <- Git ignore configuration
│
├── data/
│   ├── raw/
│   │   └── marketing_ab_test_raw.csv       <- Raw telemetry events (120,000 rows)
│   └── processed/
│       ├── ab_test_cleaned.csv             <- Deduplicated, validated dataset (74,513 rows)
│       ├── ab_test_daily_metrics.csv       <- Pre-aggregated daily dimensional metrics
│       ├── ab_test_segment_summary.csv     <- Subgroup z-test statistics & lift CIs
│       └── ab_test_statistical_summary.json<- Machine-readable test outputs & KPIs
│
├── notebooks/
│   ├── 01_eda_and_srm_check.ipynb          <- Data cleaning & SRM Chi-Square audit
│   ├── 02_statistical_hypothesis_testing.ipynb <- Two-proportion Z-Test & Welch's t-test
│   ├── 03_power_analysis_and_sample_sizing.ipynb <- Sample sizing & power curves
│   └── 04_segmentation_and_simpsons_paradox.ipynb <- Subgroup analysis & Simpson's Paradox
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py                      <- Dataset generation & data cleaning logic
│   ├── statistical_tests.py                <- Core statistical hypothesis testing engine
│   ├── power_analysis.py                   <- Sizing, MDE, and post-hoc power calculators
│   ├── visualization.py                    <- High-resolution figure rendering module
│   ├── notebook_generator.py               <- Jupyter notebook compilation script
│   └── run_full_analysis.py                <- Master pipeline runner
│
├── powerbi/
│   ├── dashboard_mockup.html               <- Interactive web dashboard for portfolio demo
│   ├── powerbi_dax_measures.dax            <- Production-grade DAX measures library
│   ├── powerbi_data_dictionary.md          <- Table schema & field definitions
│   └── powerbi_setup_guide.md              <- Power BI / Tableau connection guide
│
└── reports/
    ├── executive_summary_report.md         <- Detailed stakeholder decision memo
    └── figures/
        ├── 01_srm_check.png                <- SRM Chi-square allocation plot
        ├── 02_conversion_rate_ci.png       <- Conversion rate bar chart with 95% CIs
        ├── 03_daily_trend_conversion.png   <- Daily & cumulative conversion trajectories
        ├── 04_revenue_distribution.png     <- ARPU & order spend density
        ├── 05_statistical_power_curve.png  <- Power curves across sample sizes & lifts
        └── 06_segmentation_forest_plot.png <- Subgroup relative lift forest plot
```

---

## ⚡ How to Reproduce

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd "market project"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute the complete analysis pipeline**:
   ```bash
   python -m src.run_full_analysis
   ```

4. **Launch Jupyter Notebooks**:
   ```bash
   jupyter notebook notebooks/
   ```
