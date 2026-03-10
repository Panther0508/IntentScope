import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import data from upstream blocks
user_metrics_data = user_metrics
user_behavior_data = user_behavior_df

# ========================================
# 1. ACHIEVEMENT BADGES SYSTEM
# ========================================

def calculate_badges(user_data, behavior_data):
    """Award achievement badges based on user engagement and success metrics"""
    badges = {}
    
    for user_id in user_data['user_id'].unique():
        user_badges = []
        user_row = user_data[user_data['user_id'] == user_id].iloc[0]
        user_actions = behavior_data[behavior_data['user_id'] == user_id]
        
        # Badge: First Steps (completed first interaction)
        if len(user_actions) >= 1:
            user_badges.append('First Steps')
        
        # Badge: Active Learner (10+ interactions)
        if user_row['total_interactions'] >= 10:
            user_badges.append('Active Learner')
        
        # Badge: Power User (50+ interactions)
        if user_row['total_interactions'] >= 50:
            user_badges.append('Power User')
        
        # Badge: Success Master (90%+ success rate with 5+ interactions)
        if user_row['success_rate'] >= 0.9 and user_row['total_interactions'] >= 5:
            user_badges.append('Success Master')
        
        # Badge: Explorer (used 5+ different actions)
        if user_row['unique_actions'] >= 5:
            user_badges.append('Explorer')
        
        # Badge: Consistent User (10+ days active)
        if user_row['days_active'] >= 10:
            user_badges.append('Consistent User')
        
        # Badge: Advanced Explorer (used advanced features)
        if user_row['advanced_usage_count'] >= 3:
            user_badges.append('Advanced Explorer')
        
        # Badge: Marathon Runner (total time > 1000 min)
        if user_row['total_session_time'] > 1000:
            user_badges.append('Marathon Runner')
        
        badges[user_id] = user_badges
    
    return badges

user_badges = calculate_badges(user_metrics_data, user_behavior_data)

# ========================================
# 2. PROGRESS TRACKING METRICS
# ========================================

def calculate_progress_metrics(user_data):
    """Calculate comprehensive progress tracking metrics"""
    progress_metrics = []
    
    for _, user_row in user_data.iterrows():
        user_id = user_row['user_id']
        
        # Calculate progress levels (0-100%)
        interaction_progress = min(user_row['total_interactions'] / 100, 1.0) * 100
        success_progress = user_row['success_rate'] * 100
        feature_exploration_progress = min(user_row['unique_actions'] / 7, 1.0) * 100
        consistency_progress = min(user_row['days_active'] / 30, 1.0) * 100
        
        # Overall progress score (weighted average)
        overall_progress = (
            interaction_progress * 0.3 +
            success_progress * 0.3 +
            feature_exploration_progress * 0.2 +
            consistency_progress * 0.2
        )
        
        progress_metrics.append({
            'user_id': user_id,
            'interaction_progress': round(interaction_progress, 2),
            'success_progress': round(success_progress, 2),
            'feature_exploration_progress': round(feature_exploration_progress, 2),
            'consistency_progress': round(consistency_progress, 2),
            'overall_progress': round(overall_progress, 2),
            'level': int(overall_progress // 10) + 1  # Levels 1-11
        })
    
    return pd.DataFrame(progress_metrics)

progress_tracking_df = calculate_progress_metrics(user_metrics_data)

# ========================================
# 3. STREAK COUNTERS
# ========================================

def calculate_streaks(behavior_data):
    """Calculate engagement streaks for each user"""
    streaks = {}
    
    for user_id in behavior_data['user_id'].unique():
        user_actions = behavior_data[behavior_data['user_id'] == user_id].sort_values('timestamp')
        
        if len(user_actions) == 0:
            streaks[user_id] = {'current_streak': 0, 'longest_streak': 0, 'total_days_active': 0}
            continue
        
        # Convert timestamps to dates
        dates = pd.to_datetime(user_actions['timestamp']).dt.date
        unique_dates = sorted(dates.unique())
        
        if len(unique_dates) == 0:
            streaks[user_id] = {'current_streak': 0, 'longest_streak': 0, 'total_days_active': 0}
            continue
        
        # Calculate streaks
        longest_streak = 1
        temp_streak = 1
        
        for i in range(1, len(unique_dates)):
            prev_date = unique_dates[i-1]
            curr_date = unique_dates[i]
            diff = (curr_date - prev_date).days
            
            if diff == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
        
        # Current streak (check if last date is recent)
        last_date = unique_dates[-1]
        today = datetime.now().date()
        days_since_last = (today - last_date).days
        
        if days_since_last <= 1:
            current_streak = temp_streak
        else:
            current_streak = 0
        
        streaks[user_id] = {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_days_active': len(unique_dates)
        }
    
    return streaks

user_streaks = calculate_streaks(user_behavior_data)

# ========================================
# 4. LEADERBOARDS
# ========================================

def generate_leaderboards(user_data, badges_dict, streaks_dict):
    """Generate comprehensive leaderboards"""
    leaderboard_data = []
    
    for _, user_row in user_data.iterrows():
        user_id = user_row['user_id']
        
        leaderboard_data.append({
            'user_id': user_id,
            'total_interactions': user_row['total_interactions'],
            'success_rate': user_row['success_rate'],
            'unique_actions': user_row['unique_actions'],
            'badge_count': len(badges_dict.get(user_id, [])),
            'longest_streak': streaks_dict.get(user_id, {}).get('longest_streak', 0),
            'total_session_time': user_row['total_session_time']
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_data)
    
    # Generate multiple leaderboards
    leaderboards = {
        'top_interactions': leaderboard_df.nlargest(10, 'total_interactions')[['user_id', 'total_interactions']],
        'top_success_rate': leaderboard_df.nlargest(10, 'success_rate')[['user_id', 'success_rate']],
        'top_explorers': leaderboard_df.nlargest(10, 'unique_actions')[['user_id', 'unique_actions']],
        'top_badge_collectors': leaderboard_df.nlargest(10, 'badge_count')[['user_id', 'badge_count']],
        'top_streaks': leaderboard_df.nlargest(10, 'longest_streak')[['user_id', 'longest_streak']],
        'top_time_spent': leaderboard_df.nlargest(10, 'total_session_time')[['user_id', 'total_session_time']]
    }
    
    return leaderboards, leaderboard_df

leaderboards, leaderboard_full_df = generate_leaderboards(user_metrics_data, user_badges, user_streaks)

# ========================================
# 5. MILESTONE REWARDS
# ========================================

def calculate_milestones(user_data, badges_dict, streaks_dict):
    """Calculate milestone achievements and rewards"""
    milestones = {}
    milestone_definitions = {
        'bronze_tier': {'interactions': 10, 'success_rate': 0.5, 'reward_points': 100},
        'silver_tier': {'interactions': 25, 'success_rate': 0.7, 'reward_points': 250},
        'gold_tier': {'interactions': 50, 'success_rate': 0.85, 'reward_points': 500},
        'platinum_tier': {'interactions': 100, 'success_rate': 0.9, 'reward_points': 1000},
        'streak_warrior': {'streak': 7, 'reward_points': 200},
        'streak_champion': {'streak': 30, 'reward_points': 500},
        'badge_collector': {'badges': 5, 'reward_points': 300},
        'completionist': {'badges': 8, 'reward_points': 1000}
    }
    
    for _, user_row in user_data.iterrows():
        user_id = user_row['user_id']
        user_milestones = []
        total_reward_points = 0
        
        # Tier milestones
        if user_row['total_interactions'] >= 100 and user_row['success_rate'] >= 0.9:
            user_milestones.append('platinum_tier')
            total_reward_points += milestone_definitions['platinum_tier']['reward_points']
        elif user_row['total_interactions'] >= 50 and user_row['success_rate'] >= 0.85:
            user_milestones.append('gold_tier')
            total_reward_points += milestone_definitions['gold_tier']['reward_points']
        elif user_row['total_interactions'] >= 25 and user_row['success_rate'] >= 0.7:
            user_milestones.append('silver_tier')
            total_reward_points += milestone_definitions['silver_tier']['reward_points']
        elif user_row['total_interactions'] >= 10 and user_row['success_rate'] >= 0.5:
            user_milestones.append('bronze_tier')
            total_reward_points += milestone_definitions['bronze_tier']['reward_points']
        
        # Streak milestones
        longest_streak = streaks_dict.get(user_id, {}).get('longest_streak', 0)
        if longest_streak >= 30:
            user_milestones.append('streak_champion')
            total_reward_points += milestone_definitions['streak_champion']['reward_points']
        elif longest_streak >= 7:
            user_milestones.append('streak_warrior')
            total_reward_points += milestone_definitions['streak_warrior']['reward_points']
        
        # Badge milestones
        badge_count = len(badges_dict.get(user_id, []))
        if badge_count >= 8:
            user_milestones.append('completionist')
            total_reward_points += milestone_definitions['completionist']['reward_points']
        elif badge_count >= 5:
            user_milestones.append('badge_collector')
            total_reward_points += milestone_definitions['badge_collector']['reward_points']
        
        milestones[user_id] = {
            'achieved_milestones': user_milestones,
            'total_reward_points': total_reward_points
        }
    
    return milestones, milestone_definitions

user_milestones, milestone_rewards = calculate_milestones(user_metrics_data, user_badges, user_streaks)

# ========================================
# 6. COMPREHENSIVE GAMIFICATION SCORES
# ========================================

def calculate_gamification_scores(user_data, badges_dict, streaks_dict, milestones_dict, progress_df):
    """Calculate comprehensive gamification scores for all users"""
    gamification_scores = []
    
    for _, user_row in user_data.iterrows():
        user_id = user_row['user_id']
        
        # Component scores
        interaction_score = min(user_row['total_interactions'] * 10, 1000)
        success_score = user_row['success_rate'] * 500
        badge_score = len(badges_dict.get(user_id, [])) * 100
        streak_score = streaks_dict.get(user_id, {}).get('longest_streak', 0) * 50
        milestone_score = milestones_dict.get(user_id, {}).get('total_reward_points', 0)
        progress = progress_df[progress_df['user_id'] == user_id]['overall_progress'].values[0]
        progress_score = progress * 5
        
        # Calculate total gamification score
        total_score = (
            interaction_score +
            success_score +
            badge_score +
            streak_score +
            milestone_score +
            progress_score
        )
        
        gamification_scores.append({
            'user_id': user_id,
            'total_score': round(total_score, 2),
            'interaction_score': round(interaction_score, 2),
            'success_score': round(success_score, 2),
            'badge_score': round(badge_score, 2),
            'streak_score': round(streak_score, 2),
            'milestone_score': round(milestone_score, 2),
            'progress_score': round(progress_score, 2),
            'badges_earned': len(badges_dict.get(user_id, [])),
            'current_streak': streaks_dict.get(user_id, {}).get('current_streak', 0),
            'level': progress_df[progress_df['user_id'] == user_id]['level'].values[0]
        })
    
    return pd.DataFrame(gamification_scores).sort_values('total_score', ascending=False)

gamification_scores_df = calculate_gamification_scores(
    user_metrics_data, 
    user_badges, 
    user_streaks, 
    user_milestones,
    progress_tracking_df
)

# ========================================
# 7. RANKINGS
# ========================================

# Add overall rank to gamification scores
gamification_scores_df['rank'] = range(1, len(gamification_scores_df) + 1)

# Calculate percentile ranks
gamification_scores_df['percentile'] = (
    (len(gamification_scores_df) - gamification_scores_df['rank'] + 1) / 
    len(gamification_scores_df) * 100
).round(2)

# ========================================
# RESULTS SUMMARY
# ========================================

print("=" * 80)
print("GAMIFICATION SYSTEM - COMPREHENSIVE RESULTS")
print("=" * 80)

print(f"\n📊 TOTAL USERS PROCESSED: {len(gamification_scores_df)}")

print("\n🏆 TOP 10 OVERALL RANKINGS:")
print("-" * 80)
top_10_users = gamification_scores_df.head(10)
for idx, row in top_10_users.iterrows():
    # Convert float level to integer before formatting
    level_int = int(row['level'])
    print(f"Rank #{int(row['rank']):3d} | User {int(row['user_id']):5d} | Score: {row['total_score']:8.2f} | Level {level_int:2d} | {int(row['badges_earned'])} Badges | {int(row['current_streak'])}-day streak")

print("\n🎖️  ACHIEVEMENT BADGES DISTRIBUTION:")
print("-" * 80)
all_badge_types = set()
for badges_list in user_badges.values():
    all_badge_types.update(badges_list)

badge_counts = {badge_type: sum(1 for badges in user_badges.values() if badge_type in badges) 
                for badge_type in sorted(all_badge_types)}

for badge_name, count in badge_counts.items():
    pct = (count / len(user_badges)) * 100
    print(f"  {badge_name:20s}: {count:4d} users ({pct:5.1f}%)")

print(f"\n  Total Unique Badges: {len(all_badge_types)}")
print(f"  Avg Badges per User: {sum(len(b) for b in user_badges.values()) / len(user_badges):.2f}")

print("\n📈 PROGRESS TRACKING SUMMARY:")
print("-" * 80)
print(f"  Avg Overall Progress: {progress_tracking_df['overall_progress'].mean():.2f}%")
print(f"  Avg Level: {progress_tracking_df['level'].mean():.2f}")
print(f"  Users at Max Level (11): {len(progress_tracking_df[progress_tracking_df['level'] == 11])}")

level_dist = progress_tracking_df['level'].value_counts().sort_index()
print("\n  Level Distribution:")
for level, count in level_dist.items():
    print(f"    Level {int(level):2d}: {count:3d} users")

print("\n🔥 STREAK STATISTICS:")
print("-" * 80)
all_streaks = [s['longest_streak'] for s in user_streaks.values()]
current_streaks = [s['current_streak'] for s in user_streaks.values()]
print(f"  Avg Longest Streak: {np.mean(all_streaks):.2f} days")
print(f"  Max Longest Streak: {np.max(all_streaks)} days")
print(f"  Users with Active Streaks: {sum(1 for s in current_streaks if s > 0)}")

print("\n🏅 MILESTONE ACHIEVEMENTS:")
print("-" * 80)
all_milestone_types = set()
for milestone_data in user_milestones.values():
    all_milestone_types.update(milestone_data['achieved_milestones'])

milestone_counts = {m: sum(1 for md in user_milestones.values() if m in md['achieved_milestones']) 
                    for m in sorted(all_milestone_types)}

for milestone_name, count in milestone_counts.items():
    points = milestone_rewards[milestone_name]['reward_points']
    pct = (count / len(user_milestones)) * 100
    print(f"  {milestone_name:20s}: {count:4d} users ({pct:5.1f}%) | {points} pts")

total_rewards = sum(md['total_reward_points'] for md in user_milestones.values())
print(f"\n  Total Reward Points Distributed: {total_rewards:,}")
print(f"  Avg Reward Points per User: {total_rewards / len(user_milestones):.2f}")

print("\n📋 LEADERBOARD HIGHLIGHTS:")
print("-" * 80)

for board_name, board_df in leaderboards.items():
    print(f"\n  {board_name.upper().replace('_', ' ')}:")
    top_3 = board_df.head(3)
    for idx, (_, row) in enumerate(top_3.iterrows(), 1):
        col_name = board_df.columns[1]
        print(f"    #{idx}. User {int(row['user_id']):5d} - {row[col_name]}")

print("\n💯 GAMIFICATION SCORE STATISTICS:")
print("-" * 80)
print(f"  Avg Total Score: {gamification_scores_df['total_score'].mean():.2f}")
print(f"  Median Total Score: {gamification_scores_df['total_score'].median():.2f}")
print(f"  Max Total Score: {gamification_scores_df['total_score'].max():.2f}")
print(f"  Min Total Score: {gamification_scores_df['total_score'].min():.2f}")

print("\n  Score Component Averages:")
for col in ['interaction_score', 'success_score', 'badge_score', 'streak_score', 'milestone_score', 'progress_score']:
    print(f"    {col.replace('_', ' ').title():20s}: {gamification_scores_df[col].mean():8.2f}")

print("\n" + "=" * 80)
print("✅ GAMIFICATION SYSTEM COMPLETE - All metrics calculated successfully!")
print("=" * 80)

# Export key dataframes for downstream use
gamification_summary = {
    'badges': user_badges,
    'progress': progress_tracking_df,
    'streaks': user_streaks,
    'leaderboards': leaderboards,
    'milestones': user_milestones,
    'scores': gamification_scores_df,
    'milestone_definitions': milestone_rewards
}
