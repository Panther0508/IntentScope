import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

print("=" * 80)
print("SCENARIO SIMULATION ENGINE")
print("=" * 80)

# Zerve design system
DARK_BG = '#1D1D20'
PRIMARY_TEXT = '#fbfbff'
SECONDARY_TEXT = '#909094'
HIGHLIGHT_YELLOW = '#ffd400'
SUCCESS_GREEN = '#17b26a'
WARNING_RED = '#f04438'
ZERVE_COLORS = ['#A1C9F4', '#FFB482', '#8DE5A1', '#FF9F9B', '#D0BBFF', 
                '#1F77B4', '#9467BD', '#8C564B', '#C49C94', '#E377C2']

plt.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor': DARK_BG,
    'axes.edgecolor': PRIMARY_TEXT,
    'axes.labelcolor': PRIMARY_TEXT,
    'text.color': PRIMARY_TEXT,
    'xtick.color': PRIMARY_TEXT,
    'ytick.color': PRIMARY_TEXT,
    'grid.color': SECONDARY_TEXT,
    'legend.facecolor': DARK_BG,
    'legend.edgecolor': PRIMARY_TEXT
})

# Define intervention scenarios based on top features
print("\n📋 DEFINING INTERVENTION SCENARIOS")
print("-" * 80)

scenarios = {
    'Baseline': {
        'description': 'Current state - no interventions',
        'adjustments': {}
    },
    'Increase Engagement': {
        'description': 'Encourage more interactions (+50% total_interactions)',
        'adjustments': {
            'total_interactions': 1.5,
            'interactions_per_day': 1.5,
            'successful_actions': 1.5
        }
    },
    'Boost Success Rate': {
        'description': 'Improve success rate through better UX (+20% overall_success_rate)',
        'adjustments': {
            'overall_success_rate': 1.2,
            'early_success_rate': 1.2,
            'successful_actions': 1.2
        }
    },
    'Advanced Feature Adoption': {
        'description': 'Promote advanced/premium features (+30% pct_advanced_premium)',
        'adjustments': {
            'pct_advanced_premium': 1.3,
            'freq_advanced': 1.3,
            'advanced_user': 1.0  # Binary, so set to 1
        }
    },
    'Workflow Optimization': {
        'description': 'Improve workflow patterns and session duration (+40% avg_session_duration)',
        'adjustments': {
            'avg_session_duration': 1.4,
            'complete_sessions': 1.4,
            'has_analysis_viz_pattern': 1.0
        }
    },
    'Combined Strategy': {
        'description': 'Multi-pronged approach (engagement + success rate + advanced features)',
        'adjustments': {
            'total_interactions': 1.3,
            'overall_success_rate': 1.15,
            'pct_advanced_premium': 1.2,
            'successful_actions': 1.3,
            'avg_session_duration': 1.2
        }
    }
}

for scenario_name, scenario_info in scenarios.items():
    print(f"\n🎯 {scenario_name}")
    print(f"   Description: {scenario_info['description']}")
    if scenario_info['adjustments']:
        print(f"   Adjustments: {', '.join(scenario_info['adjustments'].keys())}")

# Function to apply scenario adjustments
def apply_scenario_adjustments(base_data, adjustments):
    """Apply scenario adjustments to feature data"""
    modified_data = base_data.copy()
    
    for feature, multiplier in adjustments.items():
        if feature in modified_data.columns:
            if feature in ['advanced_user', 'has_analysis_viz_pattern', 'has_login_analysis_pattern',
                          'has_analysis_viz_pattern', 'has_viz_export_pattern', 'has_export_share_pattern']:
                # Binary features - set to 1 if multiplier >= 1.0
                modified_data[feature] = (modified_data[feature] * multiplier).clip(0, 1)
            else:
                # Continuous features - apply multiplier
                modified_data[feature] = modified_data[feature] * multiplier
                
                # Handle percentage features - clip to [0, 1]
                if feature.startswith('pct_') or 'rate' in feature:
                    modified_data[feature] = modified_data[feature].clip(0, 1)
    
    return modified_data

# Run simulations for each scenario
print("\n" + "=" * 80)
print("RUNNING SCENARIO SIMULATIONS")
print("=" * 80)

# Use a sample of users for simulation (first 100 users)
sample_users_scaled = all_features_scaled_gb.head(100).copy()
sample_users_original = X.loc[sample_users_scaled.index].copy()

scenario_results = []

for scenario_name, scenario_info in scenarios.items():
    print(f"\n🔄 Simulating: {scenario_name}")
    
    # Apply adjustments to unscaled data first
    if scenario_info['adjustments']:
        modified_features_unscaled = apply_scenario_adjustments(
            sample_users_original, 
            scenario_info['adjustments']
        )
        # Scale the modified features
        modified_features_scaled = pd.DataFrame(
            scaler_model.transform(modified_features_unscaled),
            columns=modified_features_unscaled.columns,
            index=modified_features_unscaled.index
        ).fillna(0)
    else:
        # Baseline - use original scaled data
        modified_features_scaled = sample_users_scaled.copy()
    
    # Predict success probabilities
    success_probs = gb_classifier.predict_proba(modified_features_scaled)[:, 1]
    predicted_success = (success_probs > 0.5).astype(int)
    
    # Calculate metrics
    avg_success_prob = success_probs.mean()
    predicted_success_rate = predicted_success.mean()
    high_confidence_users = (success_probs > 0.7).sum()
    
    scenario_results.append({
        'scenario': scenario_name,
        'description': scenario_info['description'],
        'avg_success_prob': avg_success_prob,
        'predicted_success_rate': predicted_success_rate,
        'high_confidence_users': high_confidence_users,
        'total_users': len(sample_users_scaled),
        'success_probabilities': success_probs
    })
    
    print(f"   ✓ Avg success probability: {avg_success_prob:.2%}")
    print(f"   ✓ Predicted success rate: {predicted_success_rate:.2%}")
    print(f"   ✓ High-confidence successes (>70%): {high_confidence_users} users")

# Create comparison dataframe
scenario_comparison_df = pd.DataFrame([{
    'Scenario': r['scenario'],
    'Description': r['description'],
    'Avg Success Prob': r['avg_success_prob'],
    'Predicted Success Rate': r['predicted_success_rate'],
    'High-Confidence Users': r['high_confidence_users']
} for r in scenario_results])

print("\n" + "=" * 80)
print("SCENARIO COMPARISON SUMMARY")
print("=" * 80)
print(scenario_comparison_df.to_string(index=False))

# Calculate improvements vs baseline
baseline_prob = scenario_results[0]['avg_success_prob']
print(f"\n📊 IMPROVEMENT VS BASELINE:")
print("-" * 80)
for result in scenario_results[1:]:  # Skip baseline
    improvement = result['avg_success_prob'] - baseline_prob
    improvement_pct = (improvement / baseline_prob) * 100
    print(f"   {result['scenario']:30s}: +{improvement_pct:6.2f}% ({result['avg_success_prob']:.2%})")

# Create visualizations comparing scenarios
print("\n" + "=" * 80)
print("GENERATING COMPARATIVE VISUALIZATIONS")
print("=" * 80)

# Figure 1: Side-by-side success probability comparison
fig_scenario_comparison = plt.figure(figsize=(14, 10))

# Chart 1: Average Success Probability by Scenario
ax1 = plt.subplot(2, 2, 1)
scenario_names = [r['scenario'] for r in scenario_results]
success_probs_avg = [r['avg_success_prob'] * 100 for r in scenario_results]
colors_scenarios = [ZERVE_COLORS[0] if i == 0 else HIGHLIGHT_YELLOW for i in range(len(scenario_names))]

bars1 = ax1.barh(scenario_names, success_probs_avg, color=colors_scenarios, edgecolor=PRIMARY_TEXT, linewidth=1)
ax1.set_xlabel('Average Success Probability (%)', color=PRIMARY_TEXT, fontsize=11)
ax1.set_title('Success Probability by Scenario', color=PRIMARY_TEXT, fontsize=13, fontweight='bold', pad=15)
ax1.set_xlim(0, 100)
ax1.grid(axis='x', alpha=0.3, color=SECONDARY_TEXT)

# Add value labels
for bar_idx, (bar, val) in enumerate(zip(bars1, success_probs_avg)):
    ax1.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val:.1f}%', 
             va='center', color=PRIMARY_TEXT, fontsize=10, fontweight='bold')

# Chart 2: Improvement vs Baseline
ax2 = plt.subplot(2, 2, 2)
improvement_pcts = [0] + [(r['avg_success_prob'] - baseline_prob) / baseline_prob * 100 
                          for r in scenario_results[1:]]
colors_improvement = [SECONDARY_TEXT if v == 0 else (SUCCESS_GREEN if v > 0 else WARNING_RED) 
                      for v in improvement_pcts]

bars2 = ax2.barh(scenario_names, improvement_pcts, color=colors_improvement, edgecolor=PRIMARY_TEXT, linewidth=1)
ax2.set_xlabel('Improvement vs Baseline (%)', color=PRIMARY_TEXT, fontsize=11)
ax2.set_title('Relative Improvement vs Baseline', color=PRIMARY_TEXT, fontsize=13, fontweight='bold', pad=15)
ax2.axvline(x=0, color=PRIMARY_TEXT, linestyle='-', linewidth=1)
ax2.grid(axis='x', alpha=0.3, color=SECONDARY_TEXT)

for bar, val in zip(bars2, improvement_pcts):
    if val != 0:
        ax2.text(val + (1 if val > 0 else -1), bar.get_y() + bar.get_height()/2, 
                f'+{val:.1f}%' if val > 0 else f'{val:.1f}%',
                va='center', ha='left' if val > 0 else 'right', 
                color=PRIMARY_TEXT, fontsize=10, fontweight='bold')

# Chart 3: Success Probability Distribution
ax3 = plt.subplot(2, 2, 3)
for idx, result in enumerate(scenario_results):
    probs = result['success_probabilities'] * 100
    ax3.hist(probs, bins=20, alpha=0.6, label=result['scenario'], 
             color=ZERVE_COLORS[idx % len(ZERVE_COLORS)], edgecolor=PRIMARY_TEXT, linewidth=0.5)

ax3.set_xlabel('Success Probability (%)', color=PRIMARY_TEXT, fontsize=11)
ax3.set_ylabel('Number of Users', color=PRIMARY_TEXT, fontsize=11)
ax3.set_title('Success Probability Distributions', color=PRIMARY_TEXT, fontsize=13, fontweight='bold', pad=15)
ax3.legend(facecolor=DARK_BG, edgecolor=PRIMARY_TEXT, fontsize=9, loc='upper left')
ax3.grid(alpha=0.3, color=SECONDARY_TEXT)

# Chart 4: High-Confidence Users Comparison
ax4 = plt.subplot(2, 2, 4)
high_conf_counts = [r['high_confidence_users'] for r in scenario_results]
bars4 = ax4.barh(scenario_names, high_conf_counts, color=SUCCESS_GREEN, 
                edgecolor=PRIMARY_TEXT, linewidth=1, alpha=0.8)
ax4.set_xlabel('Number of Users with >70% Success Probability', color=PRIMARY_TEXT, fontsize=11)
ax4.set_title('High-Confidence Success Users', color=PRIMARY_TEXT, fontsize=13, fontweight='bold', pad=15)
ax4.grid(axis='x', alpha=0.3, color=SECONDARY_TEXT)

for bar, val in zip(bars4, high_conf_counts):
    ax4.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val}', 
             va='center', color=PRIMARY_TEXT, fontsize=10, fontweight='bold')

plt.suptitle('Scenario Simulation: Predicted Impact on User Success', 
             color=PRIMARY_TEXT, fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.98])

print("\n✓ Scenario comparison visualizations created")

print("\n" + "=" * 80)
print("✓ SCENARIO SIMULATION COMPLETE")
print("=" * 80)
print(f"✓ Simulated {len(scenarios)} intervention scenarios")
print(f"✓ Sample size: {len(sample_users_scaled)} users")
print(f"✓ Best scenario: {scenario_comparison_df.loc[scenario_comparison_df['Avg Success Prob'].idxmax(), 'Scenario']}")
print(f"✓ Maximum predicted success rate: {scenario_comparison_df['Avg Success Prob'].max():.2%}")
print(f"✓ Maximum improvement: +{max(improvement_pcts):.1f}% vs baseline")
