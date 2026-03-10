import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

print("=" * 70)
print("EXPLAINABILITY VISUALIZATION & INSIGHTS")
print("=" * 70)

# Chart 1: Top 15 Features by Composite Impact
fig_impact, ax_impact = plt.subplots(figsize=(12, 8))
top15_impact = impact_scores.head(15).sort_values('composite_impact')

bars_impact = ax_impact.barh(range(len(top15_impact)), top15_impact['composite_impact'], 
                              color=COLORS[0], edgecolor=PRIMARY_TEXT, linewidth=1)

ax_impact.set_yticks(range(len(top15_impact)))
ax_impact.set_yticklabels(top15_impact['feature'], fontsize=11)
ax_impact.set_xlabel('Composite Impact Score', fontsize=13, fontweight='bold')
ax_impact.set_title('Top 15 Behavioral Features Driving Long-Term Success\n(Composite: 70% Model Importance + 30% Correlation)', 
                    fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax_impact.spines['top'].set_visible(False)
ax_impact.spines['right'].set_visible(False)

# Add value labels
for i, (bar, val) in enumerate(zip(bars_impact, top15_impact['composite_impact'])):
    ax_impact.text(val, i, f' {val:.4f}', va='center', fontsize=10, color=PRIMARY_TEXT, fontweight='bold')

plt.tight_layout()

# Chart 2: Feature Importance vs Correlation Scatter
fig_scatter, ax_scatter = plt.subplots(figsize=(12, 8))

top20_scatter = impact_scores.head(20)
scatter = ax_scatter.scatter(top20_scatter['gb_importance'], 
                             top20_scatter['abs_correlation'],
                             s=top20_scatter['composite_impact'] * 500,
                             c=range(len(top20_scatter)),
                             cmap='viridis',
                             alpha=0.7,
                             edgecolors=PRIMARY_TEXT,
                             linewidth=1.5)

# Add labels for top 10 features
for idx, row in top20_scatter.head(10).iterrows():
    ax_scatter.annotate(row['feature'][:20], 
                       (row['gb_importance'], row['abs_correlation']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, color=PRIMARY_TEXT,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=BACKGROUND, 
                                edgecolor=PRIMARY_TEXT, alpha=0.8))

ax_scatter.set_xlabel('Gradient Boosting Feature Importance', fontsize=13, fontweight='bold')
ax_scatter.set_ylabel('Absolute Correlation with Success', fontsize=13, fontweight='bold')
ax_scatter.set_title('Feature Impact: Model Importance vs Correlation\n(Bubble size = Composite Impact)', 
                     fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax_scatter.spines['top'].set_visible(False)
ax_scatter.spines['right'].set_visible(False)
ax_scatter.grid(True, alpha=0.3)

plt.tight_layout()

# Chart 3: Behavioral Category Impact Comparison
fig_cat, ax_cat = plt.subplots(figsize=(12, 7))

# Calculate average impact by behavioral category
behavioral_categories = {
    'Success Metrics': [f for f in impact_scores['feature'] if 'success' in f.lower()],
    'Frequency Behaviors': [f for f in impact_scores['feature'] if 'freq_' in f],
    'Percentage Behaviors': [f for f in impact_scores['feature'] if 'pct_' in f],
    'Sequential Patterns': [f for f in impact_scores['feature'] if 'pattern' in f or 'sequence' in f],
    'Engagement Metrics': [f for f in impact_scores['feature'] if 'interactions' in f or 'diversity' in f or 'actions' in f.split('_')[-1]],
    'Timing Features': [f for f in impact_scores['feature'] if 'time' in f or 'hour' in f or 'days' in f or 'session' in f]
}

category_impacts = []
for cat, features_list in behavioral_categories.items():
    if features_list:
        cat_data = impact_scores[impact_scores['feature'].isin(features_list)]
        avg_impact = cat_data['composite_impact'].mean()
        max_impact = cat_data['composite_impact'].max()
        count = len(cat_data)
        category_impacts.append({
            'category': cat,
            'avg_impact': avg_impact,
            'max_impact': max_impact,
            'feature_count': count
        })

category_df = pd.DataFrame(category_impacts).sort_values('avg_impact', ascending=True)

y_positions = np.arange(len(category_df))
bars_cat = ax_cat.barh(y_positions, category_df['avg_impact'], 
                       color=COLORS[2], edgecolor=PRIMARY_TEXT, linewidth=1.5, alpha=0.8)

ax_cat.set_yticks(y_positions)
ax_cat.set_yticklabels(category_df['category'], fontsize=11)
ax_cat.set_xlabel('Average Composite Impact', fontsize=13, fontweight='bold')
ax_cat.set_title('Average Impact by Behavioral Category', 
                 fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax_cat.spines['top'].set_visible(False)
ax_cat.spines['right'].set_visible(False)

# Add value labels with feature count
for i, (bar, row) in enumerate(zip(bars_cat, category_df.itertuples())):
    ax_cat.text(row.avg_impact, i, 
               f' {row.avg_impact:.4f} ({row.feature_count} features)', 
               va='center', fontsize=10, color=PRIMARY_TEXT, fontweight='bold')

plt.tight_layout()

# Chart 4: Statistical Significance by Effect Size
fig_stats, ax_stats = plt.subplots(figsize=(12, 8))

# Plot Cohen's d for top 15 features
sig_sorted = significance_df.head(15).sort_values('cohens_d')

colors_sig = [SUCCESS if row['significant'] else WARNING for _, row in sig_sorted.iterrows()]
bars_stats = ax_stats.barh(range(len(sig_sorted)), sig_sorted['cohens_d'], 
                           color=colors_sig, edgecolor=PRIMARY_TEXT, linewidth=1)

ax_stats.set_yticks(range(len(sig_sorted)))
ax_stats.set_yticklabels(sig_sorted['feature'], fontsize=11)
ax_stats.set_xlabel("Cohen's d (Effect Size)", fontsize=13, fontweight='bold')
ax_stats.set_title('Statistical Effect Sizes: Successful vs Non-Successful Users\n(Green = Significant p<0.05, Red = Not Significant)', 
                   fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax_stats.spines['top'].set_visible(False)
ax_stats.spines['right'].set_visible(False)
ax_stats.axvline(0.2, color=SECONDARY_TEXT, linestyle='--', linewidth=1, alpha=0.5, label='Small Effect')
ax_stats.axvline(0.5, color=SECONDARY_TEXT, linestyle='--', linewidth=1, alpha=0.7, label='Medium Effect')
ax_stats.axvline(0.8, color=SECONDARY_TEXT, linestyle='--', linewidth=1, alpha=0.9, label='Large Effect')

# Add value labels
for i, (bar, val) in enumerate(zip(bars_stats, sig_sorted['cohens_d'])):
    ax_stats.text(val, i, f' {val:.3f}', va='center', fontsize=9, color=PRIMARY_TEXT)

ax_stats.legend(framealpha=0.9, loc='lower right', fontsize=10, labelcolor=PRIMARY_TEXT)
plt.tight_layout()

print("\n✓ Created 4 explainability visualizations:")
print("  • fig_impact: Top 15 features by composite impact")
print("  • fig_scatter: Feature importance vs correlation scatter")
print("  • fig_cat: Behavioral category impact comparison")
print("  • fig_stats: Statistical effect sizes by feature")

print(f"\n📊 Summary Statistics:")
print(f"  • Total features with composite impact > 0.5: {len(impact_scores[impact_scores['composite_impact'] > 0.5])}")
print(f"  • Features with large effect size (d > 0.8): {len(significance_df[significance_df['cohens_d'] > 0.8])}")
print(f"  • Average correlation of top 10 features: {impact_scores.head(10)['abs_correlation'].mean():.4f}")
