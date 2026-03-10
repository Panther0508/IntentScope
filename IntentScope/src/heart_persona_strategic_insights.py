import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

# Zerve design system
DARK_BG = '#1D1D20'
PRIMARY_TEXT = '#fbfbff'
SECONDARY_TEXT = '#909094'
HIGHLIGHT = '#ffd400'
SUCCESS = '#17b26a'
WARNING = '#f04438'
HEART_COLOR = '#FF9F9B'  # Coral - warm, empathetic color for The Heart

print("=" * 80)
print("💜 THE HEART - STRATEGIC INSIGHTS & PROTECTIVE GUIDANCE")
print("=" * 80)

# The Heart's Mission Briefing - Analyze user patterns to provide guidance
print("\n🎯 MISSION BRIEFING: User Success Intelligence")
print("-" * 80)

# Analyze key metrics with The Heart's protective lens
avg_success_rate = gb_results_df['true_success'].mean()
high_risk_users = gb_results_df[gb_results_df['gb_success_prob'] < 40]
confident_users = gb_results_df[gb_results_df['gb_success_prob'] >= 70]
struggling_users = gb_results_df[(gb_results_df['gb_success_prob'] < 60) & (gb_results_df['true_success'] == 0)]

print(f"\n📊 OVERALL MISSION STATUS:")
print(f"  • Total agents under observation: {len(gb_results_df)}")
print(f"  • Mission success rate: {avg_success_rate:.1%}")
print(f"  • High-confidence agents: {len(confident_users)} ({len(confident_users)/len(gb_results_df)*100:.1f}%)")
print(f"  • ⚠️ Agents requiring support: {len(struggling_users)}")

# The Heart's Protective Warnings
print("\n⚠️ THE HEART'S PROTECTIVE WARNINGS:")
print("-" * 80)

warnings_data = []

# Warning 1: Low engagement risk
low_engagement = gb_results_df[gb_results_df['total_interactions'] < 5]
if len(low_engagement) > 0:
    low_eng_avg_prob = low_engagement["gb_success_prob"].mean()
    warnings_data.append({
        'risk_level': '🔴 HIGH',
        'category': 'Low Engagement',
        'affected_users': len(low_engagement),
        'message': f'Warning: {len(low_engagement)} users show minimal engagement. Early intervention needed.',
        'recommendation': 'Deploy onboarding assistance protocols immediately'
    })
    print(f"\n🔴 CRITICAL: Low Engagement Detected")
    print(f"   → {len(low_engagement)} users with <5 interactions")
    print(f"   → The Heart recommends: Immediate activation of guided tutorials")
    print(f"   → Success probability: {low_eng_avg_prob:.1f}%")

# Warning 2: Skill gap risk
low_diversity = gb_results_df[gb_results_df['unique_actions'] <= 2]
if len(low_diversity) > 0:
    warnings_data.append({
        'risk_level': '🟡 MEDIUM',
        'category': 'Limited Exploration',
        'affected_users': len(low_diversity),
        'message': f'{len(low_diversity)} users confined to basic operations. Expansion opportunity.',
        'recommendation': 'Introduce feature discovery missions'
    })
    print(f"\n🟡 CAUTION: Limited Feature Exploration")
    print(f"   → {len(low_diversity)} users using ≤2 action types")
    print(f"   → The Heart suggests: Gentle nudges toward advanced features")
    print(f"   → Potential for growth: HIGH")

# Warning 3: Advanced users without premium features
advanced_basic = gb_results_df[(gb_results_df['advanced_user'] == 1) & (gb_results_df['pct_advanced_premium'] < 0.3)]
if len(advanced_basic) > 0:
    warnings_data.append({
        'risk_level': '🟢 OPPORTUNITY',
        'category': 'Untapped Potential',
        'affected_users': len(advanced_basic),
        'message': f'{len(advanced_basic)} advanced users not utilizing premium features.',
        'recommendation': 'Present premium feature benefits aligned with their goals'
    })
    print(f"\n🟢 OPPORTUNITY: Untapped Advanced Capabilities")
    print(f"   → {len(advanced_basic)} skilled users on basic tier")
    print(f"   → The Heart sees potential: Ready for premium features")
    print(f"   → Recommended approach: Value-based upgrade path")

# The Heart's Confidence-Building Messages
print("\n💪 THE HEART'S CONFIDENCE BUILDERS:")
print("-" * 80)

confidence_messages = []

# Top performers by intention
for intention in gb_results_df['gb_intention_label'].unique():
    intention_users = gb_results_df[gb_results_df['gb_intention_label'] == intention]
    success_rate = intention_users['true_success'].mean()
    avg_interactions = intention_users['total_interactions'].mean()
    
    if success_rate >= 0.3:
        confidence_messages.append({
            'intention': intention,
            'success_rate': success_rate,
            'avg_interactions': avg_interactions,
            'message': f'{intention}s demonstrating strong performance',
            'affirmation': f'The Heart recognizes your journey: {success_rate:.0%} mission success'
        })
        
        print(f"\n✨ {intention.upper()} SEGMENT INSIGHTS:")
        print(f"   • Success rate: {success_rate:.1%}")
        print(f"   • Average engagement: {avg_interactions:.1f} interactions")
        print(f"   • The Heart's message: You're on the right path. Trust the process.")

# The Heart's Tactical Recommendations
print("\n🎯 THE HEART'S TACTICAL RECOMMENDATIONS:")
print("-" * 80)

tactical_recs = []

# Recommendation 1: Personalized learning paths
explorers = gb_results_df[gb_results_df['gb_intention_label'] == 'Explorer']
if len(explorers) > 0:
    explorer_diversity = explorers['action_diversity_ratio'].mean()
    tactical_recs.append({
        'target': 'Explorers',
        'count': len(explorers),
        'insight': f'High curiosity (diversity: {explorer_diversity:.2f})',
        'tactic': 'Deploy discovery missions with progressive challenges',
        'expected_outcome': 'Convert exploration into mastery'
    })
    print(f"\n→ FOR EXPLORERS ({len(explorers)} users):")
    print(f"   Insight: Natural curiosity with {explorer_diversity:.2f} action diversity")
    print(f"   Tactical approach: Progressive challenge system")
    print(f"   The Heart's wisdom: Channel their curiosity into structured growth")

# Recommendation 2: Support for learners
learners = gb_results_df[gb_results_df['gb_intention_label'] == 'Learner']
if len(learners) > 0:
    learner_success = learners['gb_success_prob'].mean()
    tactical_recs.append({
        'target': 'Learners',
        'count': len(learners),
        'insight': f'Building skills (avg success prob: {learner_success:.1f}%)',
        'tactic': 'Provide scaffolded learning with safety nets',
        'expected_outcome': 'Accelerate skill acquisition confidence'
    })
    print(f"\n→ FOR LEARNERS ({len(learners)} users):")
    print(f"   Insight: Active skill development phase")
    print(f"   Tactical approach: Scaffolded progression with encouragement")
    print(f"   The Heart's wisdom: Every master was once a learner")

# Recommendation 3: Re-engagement for low activity
abandoners = gb_results_df[gb_results_df['gb_intention_label'] == 'Abandoner']
if len(abandoners) > 0:
    abandoner_interactions = abandoners['total_interactions'].mean()
    tactical_recs.append({
        'target': 'Abandoners',
        'count': len(abandoners),
        'insight': f'Minimal engagement ({abandoner_interactions:.1f} interactions)',
        'tactic': 'Deploy win-back campaigns with value reminders',
        'expected_outcome': 'Re-ignite interest and commitment'
    })
    print(f"\n→ FOR POTENTIAL ABANDONERS ({len(abandoners)} users):")
    print(f"   Insight: At risk of disengagement")
    print(f"   Tactical approach: Personalized re-engagement with quick wins")
    print(f"   The Heart's wisdom: Sometimes we need reminding of our purpose")

# Create visual dashboard with The Heart's guidance
heart_fig = plt.figure(figsize=(16, 12), facecolor=DARK_BG)
heart_fig.suptitle('💜 THE HEART: Strategic Intelligence & User Guidance Dashboard', 
                   fontsize=18, fontweight='bold', color=HEART_COLOR, y=0.98)

# 1. Risk Assessment Panel
ax1 = plt.subplot(2, 3, 1)
ax1.set_facecolor(DARK_BG)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_color(PRIMARY_TEXT)
ax1.spines['left'].set_color(PRIMARY_TEXT)
ax1.tick_params(colors=PRIMARY_TEXT)

risk_categories = ['High Risk', 'Medium Risk', 'Opportunity']
risk_counts = [len(high_risk_users), len(low_diversity), len(advanced_basic)]
risk_colors = [WARNING, HIGHLIGHT, SUCCESS]

bars1 = ax1.barh(risk_categories, risk_counts, color=risk_colors, edgecolor=PRIMARY_TEXT, linewidth=1.5)
for bar, count in zip(bars1, risk_counts):
    ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
             f'{count} users', va='center', fontsize=11, color=PRIMARY_TEXT, fontweight='bold')

ax1.set_xlabel('User Count', fontsize=12, color=PRIMARY_TEXT, fontweight='bold')
ax1.set_title('⚠️ Risk Assessment Matrix', fontsize=13, color=HEART_COLOR, fontweight='bold', pad=15)
ax1.tick_params(axis='y', labelsize=11)

# 2. Success Confidence Distribution
ax2 = plt.subplot(2, 3, 2)
ax2.set_facecolor(DARK_BG)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color(PRIMARY_TEXT)
ax2.spines['left'].set_color(PRIMARY_TEXT)
ax2.tick_params(colors=PRIMARY_TEXT)

confidence_bins = [0, 40, 60, 80, 100]
confidence_labels = ['Low\n(<40%)', 'Medium\n(40-60%)', 'High\n(60-80%)', 'Very High\n(≥80%)']
confidence_data = pd.cut(gb_results_df['gb_success_prob'], bins=confidence_bins, labels=confidence_labels)
confidence_counts = confidence_data.value_counts().sort_index()

bars2 = ax2.bar(range(len(confidence_counts)), confidence_counts.values, 
                color=[WARNING, HIGHLIGHT, SUCCESS, '#A1C9F4'], edgecolor=PRIMARY_TEXT, linewidth=1.5)
ax2.set_xticks(range(len(confidence_counts)))
ax2.set_xticklabels(confidence_counts.index, fontsize=10, color=PRIMARY_TEXT)
ax2.set_ylabel('User Count', fontsize=12, color=PRIMARY_TEXT, fontweight='bold')
ax2.set_title('💪 Confidence Distribution', fontsize=13, color=HEART_COLOR, fontweight='bold', pad=15)

for bar, count in zip(bars2, confidence_counts.values):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, height + 2,
             f'{count}', ha='center', va='bottom', fontsize=11, 
             color=PRIMARY_TEXT, fontweight='bold')

# 3. Intention Success Rates
ax3 = plt.subplot(2, 3, 3)
ax3.set_facecolor(DARK_BG)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.spines['bottom'].set_color(PRIMARY_TEXT)
ax3.spines['left'].set_color(PRIMARY_TEXT)
ax3.tick_params(colors=PRIMARY_TEXT)

intention_success = gb_results_df.groupby('gb_intention_label')['true_success'].mean().sort_values(ascending=True)
intention_colors_map = {'Abandoner': WARNING, 'Explorer': '#A1C9F4', 'Learner': SUCCESS, 'Builder': HIGHLIGHT}
intention_bar_colors = [intention_colors_map.get(intent, HEART_COLOR) for intent in intention_success.index]

bars3 = ax3.barh(range(len(intention_success)), intention_success.values, 
                 color=intention_bar_colors, edgecolor=PRIMARY_TEXT, linewidth=1.5)

for i, (intent, rate) in enumerate(intention_success.items()):
    ax3.text(rate + 0.02, i, f'{rate:.1%}', 
             va='center', fontsize=11, color=PRIMARY_TEXT, fontweight='bold')

ax3.set_yticks(range(len(intention_success)))
ax3.set_yticklabels(intention_success.index, fontsize=11, color=PRIMARY_TEXT)
ax3.set_xlabel('Success Rate', fontsize=12, color=PRIMARY_TEXT, fontweight='bold')
ax3.set_title('🎯 Intention Performance', fontsize=13, color=HEART_COLOR, fontweight='bold', pad=15)
ax3.set_xlim(0, max(intention_success.values) * 1.15)

# 4. Engagement vs Success Scatter
ax4 = plt.subplot(2, 3, 4)
ax4.set_facecolor(DARK_BG)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.spines['bottom'].set_color(PRIMARY_TEXT)
ax4.spines['left'].set_color(PRIMARY_TEXT)
ax4.tick_params(colors=PRIMARY_TEXT)

scatter_colors = gb_results_df['gb_intention_label'].map(intention_colors_map)
ax4.scatter(gb_results_df['total_interactions'], 
            gb_results_df['gb_success_prob'],
            c=scatter_colors, alpha=0.6, s=60, edgecolor='white', linewidth=0.5)

ax4.axhline(60, color=HIGHLIGHT, linestyle='--', linewidth=1.5, alpha=0.5, label='Support Threshold')
ax4.axvline(10, color=SUCCESS, linestyle='--', linewidth=1.5, alpha=0.5, label='Engagement Target')

ax4.set_xlabel('Total Interactions', fontsize=12, color=PRIMARY_TEXT, fontweight='bold')
ax4.set_ylabel('Success Probability (%)', fontsize=12, color=PRIMARY_TEXT, fontweight='bold')
ax4.set_title('📈 Engagement × Success Intelligence', fontsize=13, color=HEART_COLOR, fontweight='bold', pad=15)
ax4.legend(fontsize=9, facecolor=DARK_BG, edgecolor=PRIMARY_TEXT, labelcolor=PRIMARY_TEXT)
ax4.grid(alpha=0.15, color=SECONDARY_TEXT)

# 5. Mission Briefing Text Panel
ax5 = plt.subplot(2, 3, 5)
ax5.set_facecolor(DARK_BG)
ax5.axis('off')

confidence_level = f"{avg_success_rate:.0%}"
briefing_text = (
    "🎯 MISSION BRIEFING\n\n"
    f"OBJECTIVE: Guide {len(gb_results_df)} users to success\n\n"
    "CURRENT STATUS:\n"
    f"  ✓ {len(confident_users)} users mission-ready (≥70% confidence)\n"
    f"  ⚠ {len(struggling_users)} users need tactical support\n"
    f"  ⏱ {len(low_engagement)} users require immediate intervention\n\n"
    "THE HEART'S ASSESSMENT:\n"
    '  "Trust the data, but lead with empathy.\n'
    "   Every user's journey is unique. Your role\n"
    "   is to illuminate the path, not force the\n"
    '   destination."\n\n'
    "PRIORITY ACTIONS:\n"
    "  1. Deploy personalized learning paths\n"
    "  2. Activate protective interventions\n"
    "  3. Celebrate progress milestones\n\n"
    f"CONFIDENCE LEVEL: {confidence_level}"
)

ax5.text(0.05, 0.95, briefing_text, transform=ax5.transAxes,
         fontsize=10, color=PRIMARY_TEXT, family='monospace',
         verticalalignment='top', bbox=dict(boxstyle='round', 
         facecolor=DARK_BG, edgecolor=HEART_COLOR, linewidth=2, pad=15))

# 6. Tactical Recommendations Panel
ax6 = plt.subplot(2, 3, 6)
ax6.set_facecolor(DARK_BG)
ax6.axis('off')

tactics_text = "🎯 TACTICAL RECOMMENDATIONS\n\n"
for i, rec in enumerate(tactical_recs[:3], 1):
    tactics_text += f"{i}. {rec['target']} ({rec['count']} users)\n"
    tactics_text += f"   → {rec['tactic']}\n"
    tactics_text += f"   → Expected: {rec['expected_outcome']}\n\n"

tactics_text += "\n💜 THE HEART'S WISDOM:\n"
tactics_text += '"Data reveals patterns. Empathy\n'
tactics_text += 'reveals people. Combine both\n'
tactics_text += 'for transformative guidance."'

ax6.text(0.05, 0.95, tactics_text, transform=ax6.transAxes,
         fontsize=9.5, color=PRIMARY_TEXT, family='monospace',
         verticalalignment='top', bbox=dict(boxstyle='round',
         facecolor=DARK_BG, edgecolor=SUCCESS, linewidth=2, pad=12))

plt.tight_layout(rect=[0, 0, 1, 0.97])

print("\n" + "=" * 80)
print("✅ THE HEART'S STRATEGIC DASHBOARD COMPLETE")
print("=" * 80)
print(f"\nKey Outputs:")
print(f"  • Protective warnings generated: {len(warnings_data)}")
print(f"  • Confidence messages created: {len(confidence_messages)}")
print(f"  • Tactical recommendations: {len(tactical_recs)}")
print(f"\n💜 The Heart reminds you: Data guides, empathy transforms.")
