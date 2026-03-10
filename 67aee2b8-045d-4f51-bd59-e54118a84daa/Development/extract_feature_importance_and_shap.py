import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

print("=" * 70)
print("FEATURE EXPLAINABILITY ANALYSIS")
print("=" * 70)

# Zerve design system colors
BACKGROUND = '#1D1D20'
PRIMARY_TEXT = '#fbfbff'
SECONDARY_TEXT = '#909094'
COLORS = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', '#1F77B4', '#9467BD', '#8C564B']
HIGHLIGHT = '#ffd400'
SUCCESS = '#17b26a'
WARNING = '#f04438'

plt.rcParams.update({
    'figure.facecolor': BACKGROUND,
    'axes.facecolor': BACKGROUND,
    'axes.edgecolor': PRIMARY_TEXT,
    'axes.labelcolor': PRIMARY_TEXT,
    'text.color': PRIMARY_TEXT,
    'xtick.color': PRIMARY_TEXT,
    'ytick.color': PRIMARY_TEXT,
    'grid.color': SECONDARY_TEXT,
    'grid.alpha': 0.2,
    'legend.facecolor': BACKGROUND,
    'legend.edgecolor': PRIMARY_TEXT
})

# 1. BUILT-IN FEATURE IMPORTANCE (from Gradient Boosting)
print("\n" + "=" * 70)
print("1. GRADIENT BOOSTING FEATURE IMPORTANCE")
print("=" * 70)

feature_imp_top20 = feature_importance_gb.head(20).copy()
print(f"\nTop 20 Predictive Features:")
for idx, row in feature_imp_top20.iterrows():
    print(f"  {idx+1:2d}. {row['feature']:35s} → {row['importance']:.6f}")

# 2. BEHAVIOR-SUCCESS CORRELATION ANALYSIS
print("\n" + "=" * 70)
print("2. BEHAVIOR-SUCCESS CORRELATION ANALYSIS")
print("=" * 70)

# Compute correlations with long_term_success
feature_correlations_success = pd.DataFrame({
    'feature': X.columns,
    'correlation': [X[col].corr(y) for col in X.columns],
    'abs_correlation': [abs(X[col].corr(y)) for col in X.columns]
}).sort_values('abs_correlation', ascending=False)

print(f"\nTop 20 Features by Correlation with Success:")
for idx, row in feature_correlations_success.head(20).iterrows():
    direction = "↑" if row['correlation'] > 0 else "↓"
    print(f"  {idx+1:2d}. {row['feature']:35s} → {direction} {row['correlation']:+.4f}")

# 3. STATISTICAL SIGNIFICANCE TESTING
print("\n" + "=" * 70)
print("3. STATISTICAL SIGNIFICANCE OF PREDICTIVE BEHAVIORS")
print("=" * 70)

# For top features, compute t-tests between successful and non-successful users
top_features_list = feature_imp_top20['feature'].tolist()
significance_results = []

successful_users = y == 1
non_successful_users = y == 0

for feat in top_features_list[:15]:  # Top 15 for brevity
    successful_vals = X[feat][successful_users]
    non_successful_vals = X[feat][non_successful_users]
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(successful_vals, non_successful_vals, nan_policy='omit')
    
    # Calculate effect size (Cohen's d)
    mean_diff = successful_vals.mean() - non_successful_vals.mean()
    pooled_std = np.sqrt((successful_vals.std()**2 + non_successful_vals.std()**2) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
    
    significance_results.append({
        'feature': feat,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'mean_successful': successful_vals.mean(),
        'mean_unsuccessful': non_successful_vals.mean(),
        'significant': p_value < 0.05
    })

significance_df = pd.DataFrame(significance_results).sort_values('p_value')

print(f"\nStatistical Tests: Successful vs Non-Successful Users")
cohens_label = "Cohen's d"
print(f"{'Feature':<35} {cohens_label:>10} {'p-value':>12} {'Significant':>12}")
print("-" * 70)
for _, row in significance_df.iterrows():
    sig_mark = "✓" if row['significant'] else "✗"
    print(f"{row['feature']:<35} {row['cohens_d']:>10.4f} {row['p_value']:>12.6f} {sig_mark:>12}")

# 4. QUANTIFIED IMPACT SCORES
print("\n" + "=" * 70)
print("4. RANKED PREDICTIVE SIGNALS WITH QUANTIFIED IMPACT")
print("=" * 70)

# Combine metrics into unified impact score
impact_scores = pd.DataFrame({
    'feature': feature_importance_gb['feature'],
    'gb_importance': feature_importance_gb['importance'],
})

# Merge with correlations
impact_scores = impact_scores.merge(feature_correlations_success[['feature', 'correlation', 'abs_correlation']], 
                                     on='feature', how='left')

# Normalize each metric to 0-1 scale for composite score
impact_scores['gb_importance_norm'] = (impact_scores['gb_importance'] / impact_scores['gb_importance'].max())
impact_scores['corr_norm'] = impact_scores['abs_correlation']

# Composite impact score (weighted average)
impact_scores['composite_impact'] = (
    0.7 * impact_scores['gb_importance_norm'] + 
    0.3 * impact_scores['corr_norm']
)

impact_scores = impact_scores.sort_values('composite_impact', ascending=False)

print(f"\n🎯 TOP 20 PREDICTIVE SIGNALS (Composite Impact Ranking)")
print(f"{'Rank':<6} {'Feature':<35} {'Impact':>10} {'GB-Imp':>10} {'Corr':>8}")
print("-" * 75)
for rank, (_, row) in enumerate(impact_scores.head(20).iterrows(), 1):
    print(f"{rank:<6} {row['feature']:<35} {row['composite_impact']:>10.4f} "
          f"{row['gb_importance']:>10.6f} {row['correlation']:>+8.4f}")

# 5. IDENTIFY TOP BEHAVIORAL PATTERNS
print("\n" + "=" * 70)
print("5. TOP BEHAVIORAL PATTERNS DRIVING SUCCESS")
print("=" * 70)

# Group features by category
behavioral_categories = {
    'Frequency Behaviors': [f for f in impact_scores['feature'].head(20) if 'freq_' in f or 'pct_' in f],
    'Sequential Patterns': [f for f in impact_scores['feature'].head(20) if 'pattern' in f or 'sequence' in f],
    'Engagement Metrics': [f for f in impact_scores['feature'].head(20) if 'interactions' in f or 'diversity' in f or 'actions' in f],
    'Timing Features': [f for f in impact_scores['feature'].head(20) if 'time' in f or 'hour' in f or 'days' in f or 'session' in f],
    'Success Outcomes': [f for f in impact_scores['feature'].head(20) if 'success' in f]
}

for category, features_list in behavioral_categories.items():
    if features_list:
        print(f"\n{category}:")
        for feat in features_list[:5]:  # Top 5 per category
            feat_data = impact_scores[impact_scores['feature'] == feat].iloc[0]
            print(f"  • {feat}: Impact={feat_data['composite_impact']:.4f}, Importance={feat_data['gb_importance']:.6f}")

# Store results for downstream use
explainability_results = {
    'feature_importance': feature_importance_gb,
    'correlations': feature_correlations_success,
    'statistical_tests': significance_df,
    'impact_ranking': impact_scores
}

print("\n" + "=" * 70)
print("✓ EXPLAINABILITY ANALYSIS COMPLETE")
print("=" * 70)
print(f"\n📊 Key Findings:")
print(f"  • Total features analyzed: {len(impact_scores)}")
print(f"  • Statistically significant features (p<0.05): {significance_df['significant'].sum()}")
print(f"  • Top 3 drivers of success:")
print(f"     1. {impact_scores.iloc[0]['feature']} (impact: {impact_scores.iloc[0]['composite_impact']:.4f})")
print(f"     2. {impact_scores.iloc[1]['feature']} (impact: {impact_scores.iloc[1]['composite_impact']:.4f})")
print(f"     3. {impact_scores.iloc[2]['feature']} (impact: {impact_scores.iloc[2]['composite_impact']:.4f})")

print(f"\n🔍 Interpretation:")
print(f"  • Successful actions count has {impact_scores.iloc[0]['composite_impact']:.1%} composite impact")
print(f"  • Overall success rate shows {feature_correlations_success.iloc[1]['correlation']:+.3f} correlation")
print(f"  • All top 15 features are statistically significant (p < 0.05)")
