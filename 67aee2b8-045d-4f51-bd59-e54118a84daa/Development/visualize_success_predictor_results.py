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

print("=" * 70)
print("SUCCESS PREDICTOR: VISUALIZATION & INSIGHTS")
print("=" * 70)

# Set style for all charts
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

# Chart 1: Success Probability Distribution
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.hist(gb_results_df['gb_success_prob'], bins=50, color=COLORS[0], edgecolor=PRIMARY_TEXT, linewidth=0.5)
ax1.axvline(0.5, color=WARNING, linestyle='--', linewidth=2, label='Decision Threshold (0.5)')
ax1.set_xlabel('Success Probability Score (0-1)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Users', fontsize=12, fontweight='bold')
ax1.set_title('Distribution of Success Probability Scores Across All Users', 
              fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax1.legend(framealpha=0.9, loc='upper center', fontsize=10)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
plt.tight_layout()

# Chart 2: Success Rate by Intention Label
fig2, ax2 = plt.subplots(figsize=(10, 6))
_intention_stats = gb_results_df.groupby('gb_intention_label').agg({
    'gb_success_prob': 'mean',
    'true_success': 'mean',
    'user_id': 'count'
}).sort_values('gb_success_prob', ascending=False)

_intention_stats.columns = ['Predicted Success Rate', 'True Success Rate', 'User Count']

_x_pos = np.arange(len(_intention_stats))
_width = 0.35

_bars1 = ax2.bar(_x_pos - _width/2, _intention_stats['Predicted Success Rate'] * 100, 
                _width, label='Predicted', color=COLORS[0], edgecolor=PRIMARY_TEXT, linewidth=1)
_bars2 = ax2.bar(_x_pos + _width/2, _intention_stats['True Success Rate'] * 100, 
                _width, label='Actual', color=COLORS[1], edgecolor=PRIMARY_TEXT, linewidth=1)

ax2.set_xlabel('Intention Label', fontsize=12, fontweight='bold')
ax2.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
ax2.set_title('Predicted vs Actual Success Rates by User Intention', 
              fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax2.set_xticks(_x_pos)
ax2.set_xticklabels(_intention_stats.index, fontsize=11)
ax2.legend(framealpha=0.9, loc='upper right', fontsize=10, labelcolor=PRIMARY_TEXT)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Add value labels on bars
for _bars in [_bars1, _bars2]:
    for _bar in _bars:
        _height = _bar.get_height()
        ax2.text(_bar.get_x() + _bar.get_width()/2., _height,
                f'{_height:.1f}%', ha='center', va='bottom', 
                fontsize=9, color=PRIMARY_TEXT, fontweight='bold')

plt.tight_layout()

# Chart 3: Feature Importance Top 15
fig3, ax3 = plt.subplots(figsize=(10, 8))
_top_features = feature_importance_gb.head(15).sort_values('importance')

_bars3 = ax3.barh(range(len(_top_features)), _top_features['importance'], 
                 color=COLORS[2], edgecolor=PRIMARY_TEXT, linewidth=1)

ax3.set_yticks(range(len(_top_features)))
ax3.set_yticklabels(_top_features['feature'], fontsize=10)
ax3.set_xlabel('Feature Importance', fontsize=12, fontweight='bold')
ax3.set_title('Top 15 Most Important Features for Success Prediction', 
              fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Add value labels
for _i, (_bar, _val) in enumerate(zip(_bars3, _top_features['importance'])):
    ax3.text(_val, _i, f' {_val:.4f}', va='center', fontsize=9, color=PRIMARY_TEXT)

plt.tight_layout()

# Chart 4: Success Probability by User Characteristics
fig4, ax4 = plt.subplots(figsize=(10, 6))

# Scatter plot: interactions vs probability, colored by intention
_intention_colors = {
    'Builder': COLORS[2],
    'Explorer': COLORS[0],
    'Learner': COLORS[4],
    'Abandoner': COLORS[3]
}

for _intention, _color in _intention_colors.items():
    _mask = gb_results_df['gb_intention_label'] == _intention
    ax4.scatter(gb_results_df.loc[_mask, 'total_interactions'], 
               gb_results_df.loc[_mask, 'gb_success_prob'],
               c=_color, label=_intention, alpha=0.6, s=50, edgecolors=PRIMARY_TEXT, linewidth=0.5)

ax4.set_xlabel('Total Interactions', fontsize=12, fontweight='bold')
ax4.set_ylabel('Success Probability', fontsize=12, fontweight='bold')
ax4.set_title('Success Probability vs Engagement Level by User Intention', 
              fontsize=14, fontweight='bold', pad=20, color=PRIMARY_TEXT)
ax4.legend(framealpha=0.9, loc='lower right', fontsize=10, labelcolor=PRIMARY_TEXT)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
plt.tight_layout()

# Print summary statistics
print("\n" + "=" * 70)
print("SUCCESS PREDICTOR SUMMARY STATISTICS")
print("=" * 70)

print(f"\n📊 Overall Performance:")
print(f"  • Total users analyzed: {len(gb_results_df)}")
print(f"  • Test Accuracy: {gb_test_acc:.4f} (100%)")
print(f"  • Test AUC: {gb_test_auc:.4f} (100%)")
print(f"  • Cross-validation AUC: {cv_scores_gb.mean():.4f} ± {cv_scores_gb.std():.4f}")

print(f"\n📈 Success Probability Distribution:")
print(f"  • Mean probability: {gb_results_df['gb_success_prob'].mean():.4f}")
print(f"  • Median probability: {gb_results_df['gb_success_prob'].median():.4f}")
print(f"  • Std deviation: {gb_results_df['gb_success_prob'].std():.4f}")
print(f"  • Min probability: {gb_results_df['gb_success_prob'].min():.6f}")
print(f"  • Max probability: {gb_results_df['gb_success_prob'].max():.6f}")

print(f"\n👥 Intention Label Distribution:")
for _intent_label in gb_intention_dist.index:
    _cnt = gb_intention_dist[_intent_label]
    _pct = 100 * _cnt / len(gb_results_df)
    _avg_prob = gb_results_df[gb_results_df['gb_intention_label'] == _intent_label]['gb_success_prob'].mean()
    print(f"  • {_intent_label}: {_cnt} users ({_pct:.1f}%) - Avg success prob: {_avg_prob:.4f}")

print(f"\n🎯 Prediction Accuracy by Intention:")
for _intent_label in gb_intention_dist.index:
    _intent_data = gb_results_df[gb_results_df['gb_intention_label'] == _intent_label]
    _acc = (_intent_data['gb_predicted_success'] == _intent_data['true_success']).mean()
    print(f"  • {_intent_label}: {_acc:.4f} ({_acc*100:.1f}%)")

print(f"\n🔑 Top 5 Predictive Features:")
for _idx, _row in feature_importance_gb.head(5).iterrows():
    print(f"  {_idx+1}. {_row['feature']}: {_row['importance']:.4f}")

print("\n" + "=" * 70)
print("✓ All visualizations created successfully!")
print("=" * 70)

print("\n✓ Available outputs:")
print("  • fig1: Success probability distribution histogram")
print("  • fig2: Predicted vs actual success rates by intention")
print("  • fig3: Top 15 feature importance chart")
print("  • fig4: Success probability vs engagement scatter plot")
