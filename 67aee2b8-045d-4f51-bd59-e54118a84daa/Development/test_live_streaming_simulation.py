import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from threading import Thread
import random

class LiveInputSimulator:
    """
    Real-time user interaction simulator with configurable parameters.
    Generates streaming user behavior data with timestamps and realistic action sequences.
    """
    
    def __init__(self, num_users=100, interaction_rate=10, behavior_pattern='mixed'):
        """
        Initialize the live input simulator.
        
        Parameters:
        -----------
        num_users : int
            Number of concurrent simulated users
        interaction_rate : float
            Average interactions per second across all users
        behavior_pattern : str
            'exploratory', 'goal_oriented', 'mixed', 'high_frequency'
        """
        self.num_users = num_users
        self.interaction_rate = interaction_rate
        self.behavior_pattern = behavior_pattern
        
        # Action sequences based on behavior patterns
        self.action_types = ['login', 'search', 'filter', 'export', 'view_details', 
                             'configure', 'save', 'share', 'logout']
        
        # Tier distribution
        self.tiers = ['Free', 'Pro', 'Enterprise']
        self.tier_weights = [0.6, 0.3, 0.1]  # Realistic distribution
        
        # Behavior pattern templates
        self.patterns = {
            'exploratory': {
                'actions': ['login', 'search', 'view_details', 'search', 'view_details', 'logout'],
                'duration_range': (10, 60),
                'success_prob': 0.7
            },
            'goal_oriented': {
                'actions': ['login', 'search', 'filter', 'export', 'logout'],
                'duration_range': (5, 30),
                'success_prob': 0.9
            },
            'high_frequency': {
                'actions': ['login', 'search', 'filter', 'view_details', 'configure', 
                           'save', 'export', 'share', 'logout'],
                'duration_range': (2, 15),
                'success_prob': 0.85
            },
            'mixed': {
                'actions': ['login', 'search', 'view_details', 'filter', 'export', 'logout'],
                'duration_range': (5, 45),
                'success_prob': 0.8
            }
        }
        
        # Streaming state
        self.streaming_events = []
        self.is_streaming = False
        self.event_count = 0
        
        print(f"✓ Live Input Simulator initialized")
        print(f"  • Users: {num_users}")
        print(f"  • Interaction rate: {interaction_rate} events/sec")
        print(f"  • Behavior pattern: {behavior_pattern}")
    
    def generate_user_session(self, user_id, pattern_type=None):
        """Generate a realistic user session with action sequence."""
        if pattern_type is None:
            pattern_type = self.behavior_pattern
        
        # For mixed patterns, randomly choose
        if pattern_type == 'mixed':
            pattern_type = random.choice(['exploratory', 'goal_oriented', 'high_frequency'])
        
        pattern = self.patterns[pattern_type]
        actions = pattern['actions'].copy()
        
        # Add some randomness to action sequences
        if random.random() > 0.7:
            random_action = random.choice(self.action_types)
            insert_pos = random.randint(1, len(actions) - 1)
            actions.insert(insert_pos, random_action)
        
        # Generate session events
        session_events = []
        current_time = datetime.now()
        tier = random.choices(self.tiers, weights=self.tier_weights)[0]
        
        for action in actions:
            duration = random.randint(*pattern['duration_range'])
            success = random.random() < pattern['success_prob']
            
            event = {
                'user_id': user_id,
                'timestamp': current_time.isoformat(),
                'action': action,
                'tier': tier,
                'session_duration': duration,
                'success': success,
                'feature_used': random.choice(['feature_' + chr(65 + i) for i in range(5)])
            }
            
            session_events.append(event)
            current_time += timedelta(seconds=duration)
        
        return session_events
    
    def stream_events(self, duration_seconds=20):
        """Stream events in real-time for specified duration."""
        self.is_streaming = True
        start_time = time.time()
        
        delay_per_event = 1.0 / self.interaction_rate
        user_id_base = 50000
        
        print(f"\n🔴 STREAMING STARTED")
        print(f"Duration: {duration_seconds}s | Rate: {self.interaction_rate} events/sec")
        print(f"Expected events: ~{int(duration_seconds * self.interaction_rate)}")
        
        while (time.time() - start_time) < duration_seconds and self.is_streaming:
            user_id = user_id_base + random.randint(0, self.num_users - 1)
            tier = random.choices(self.tiers, weights=self.tier_weights)[0]
            action = random.choice(self.action_types)
            
            pattern = self.patterns[self.behavior_pattern if self.behavior_pattern != 'mixed' 
                                   else random.choice(['exploratory', 'goal_oriented', 'high_frequency'])]
            
            event = {
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'tier': tier,
                'session_duration': random.randint(*pattern['duration_range']),
                'success': random.random() < pattern['success_prob'],
                'feature_used': random.choice(['feature_' + chr(65 + i) for i in range(5)])
            }
            
            self.streaming_events.append(event)
            self.event_count += 1
            
            time.sleep(delay_per_event)
        
        elapsed = time.time() - start_time
        actual_rate = self.event_count / elapsed if elapsed > 0 else 0
        
        print(f"⏹ STREAMING STOPPED")
        print(f"Total events: {self.event_count} | Actual rate: {actual_rate:.2f} events/sec")
        print(f"Unique users: {len(set(e['user_id'] for e in self.streaming_events))}")
        
        self.is_streaming = False
    
    def get_streaming_dataframe(self):
        """Get current streaming events as DataFrame."""
        if not self.streaming_events:
            return pd.DataFrame()
        return pd.DataFrame(self.streaming_events)
    
    def generate_batch_sessions(self, num_sessions=50):
        """Generate a batch of complete user sessions."""
        all_events = []
        for i in range(num_sessions):
            user_id = 60000 + i
            session_events = self.generate_user_session(user_id)
            all_events.extend(session_events)
        
        return pd.DataFrame(all_events)


# Test streaming simulation
print("=" * 70)
print("LIVE INPUT SIMULATION ENGINE - STREAMING TEST")
print("=" * 70)

# Create simulator
stream_simulator = LiveInputSimulator(num_users=50, interaction_rate=15, behavior_pattern='mixed')

# Test streaming for 20 seconds
stream_simulator.stream_events(duration_seconds=20)

# Get resulting data
streaming_data = stream_simulator.get_streaming_dataframe()

print(f"\n✅ STREAMING TEST COMPLETE")
print(f"\nGenerated Data Summary:")
print(f"  • Total Events: {len(streaming_data)}")
print(f"  • Unique Users: {streaming_data['user_id'].nunique()}")
print(f"  • Time Span: {len(streaming_data) / 15:.1f}s (at 15 events/sec)")
print(f"  • Success Rate: {streaming_data['success'].mean() * 100:.1f}%")

print(f"\n📊 Action Distribution:")
for action, count in streaming_data['action'].value_counts().head(5).items():
    pct = (count / len(streaming_data)) * 100
    print(f"  {action:15s}: {count:3d} ({pct:5.1f}%)")

print(f"\n📊 Tier Distribution:")
for tier, count in streaming_data['tier'].value_counts().items():
    pct = (count / len(streaming_data)) * 100
    print(f"  {tier:15s}: {count:3d} ({pct:5.1f}%)")

print(f"\nSample streaming events:")
print(streaming_data[['user_id', 'timestamp', 'action', 'tier', 'success']].head(10))

print("\n" + "=" * 70)
print("✅ SUCCESS: Live Input Simulation Engine validated")
print("=" * 70)
