import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from threading import Thread, Lock
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
        self.lock = Lock()
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
            # Insert random actions
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
    
    def stream_events(self, duration_seconds=60):
        """
        Stream events in real-time for specified duration.
        
        Parameters:
        -----------
        duration_seconds : int
            How long to stream events (seconds)
        """
        self.is_streaming = True
        start_time = time.time()
        
        # Calculate delay between events to match interaction rate
        delay_per_event = 1.0 / self.interaction_rate
        
        user_id_base = 50000  # Start from higher ID to distinguish from training data
        
        print(f"\n🔴 STREAMING STARTED")
        print(f"Duration: {duration_seconds}s | Rate: {self.interaction_rate} events/sec")
        print(f"Expected events: ~{int(duration_seconds * self.interaction_rate)}")
        print("-" * 60)
        
        while (time.time() - start_time) < duration_seconds and self.is_streaming:
            # Generate event for random user
            user_id = user_id_base + random.randint(0, self.num_users - 1)
            
            # Generate single event (not full session to simulate real-time)
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
            
            with self.lock:
                self.streaming_events.append(event)
                self.event_count += 1
            
            # Rate limiting
            time.sleep(delay_per_event)
        
        elapsed = time.time() - start_time
        actual_rate = self.event_count / elapsed if elapsed > 0 else 0
        
        print("-" * 60)
        print(f"⏹ STREAMING STOPPED")
        print(f"Total events generated: {self.event_count}")
        print(f"Actual rate: {actual_rate:.2f} events/sec")
        print(f"Unique users: {len(set(e['user_id'] for e in self.streaming_events))}")
        
        self.is_streaming = False
    
    def get_streaming_dataframe(self):
        """Get current streaming events as DataFrame."""
        with self.lock:
            if not self.streaming_events:
                return pd.DataFrame()
            return pd.DataFrame(self.streaming_events)
    
    def clear_buffer(self):
        """Clear streaming event buffer."""
        with self.lock:
            self.streaming_events = []
            self.event_count = 0
        print("✓ Event buffer cleared")
    
    def generate_batch_sessions(self, num_sessions=50):
        """Generate a batch of complete user sessions (for testing)."""
        all_events = []
        for i in range(num_sessions):
            user_id = 60000 + i
            session_events = self.generate_user_session(user_id)
            all_events.extend(session_events)
        
        return pd.DataFrame(all_events)


# Test the simulator with different configurations
print("=" * 70)
print("LIVE INPUT SIMULATION ENGINE")
print("=" * 70)

# Test 1: Default configuration
print("\n[Test 1] Default Configuration (Mixed Behavior)")
simulator_default = LiveInputSimulator(num_users=50, interaction_rate=10, 
                                       behavior_pattern='mixed')

# Generate batch sessions for demonstration
batch_data = simulator_default.generate_batch_sessions(num_sessions=10)
print(f"\n✓ Generated {len(batch_data)} events from 10 complete sessions")
print(f"\nSample events:")
print(batch_data[['user_id', 'action', 'tier', 'session_duration', 'success']].head(10))

# Test 2: High-frequency pattern
print("\n\n[Test 2] High-Frequency Behavior Pattern")
simulator_highfreq = LiveInputSimulator(num_users=30, interaction_rate=20, 
                                       behavior_pattern='high_frequency')
batch_highfreq = simulator_highfreq.generate_batch_sessions(num_sessions=5)
print(f"✓ Generated {len(batch_highfreq)} events (high-frequency pattern)")

# Test 3: Goal-oriented pattern
print("\n[Test 3] Goal-Oriented Behavior Pattern")
simulator_goal = LiveInputSimulator(num_users=25, interaction_rate=5, 
                                   behavior_pattern='goal_oriented')
batch_goal = simulator_goal.generate_batch_sessions(num_sessions=5)
print(f"✓ Generated {len(batch_goal)} events (goal-oriented pattern)")

# Analyze generated data
print("\n" + "=" * 70)
print("DATA QUALITY ANALYSIS")
print("=" * 70)

print(f"\n📊 Action Distribution (Default Pattern):")
action_dist = batch_data['action'].value_counts()
for action, count in action_dist.items():
    pct = (count / len(batch_data)) * 100
    print(f"  {action:15s}: {count:3d} ({pct:5.1f}%)")

print(f"\n📊 Tier Distribution:")
tier_dist = batch_data['tier'].value_counts()
for tier, count in tier_dist.items():
    pct = (count / len(batch_data)) * 100
    print(f"  {tier:15s}: {count:3d} ({pct:5.1f}%)")

print(f"\n📊 Success Rate: {batch_data['success'].mean() * 100:.1f}%")
print(f"📊 Avg Session Duration: {batch_data['session_duration'].mean():.1f}s")
print(f"📊 Total Unique Users: {batch_data['user_id'].nunique()}")

# Create reusable simulators for streaming tests
simulator_streaming = LiveInputSimulator(num_users=100, interaction_rate=15, 
                                        behavior_pattern='mixed')

print("\n" + "=" * 70)
print("✅ Live Input Simulation Engine Ready")
print("=" * 70)
print("\nAvailable simulators:")
print("  • simulator_default: Mixed behavior, 50 users, 10 events/sec")
print("  • simulator_highfreq: High-frequency, 30 users, 20 events/sec")
print("  • simulator_goal: Goal-oriented, 25 users, 5 events/sec")
print("  • simulator_streaming: Mixed behavior, 100 users, 15 events/sec (for streaming)")
print("\nUsage:")
print("  # Generate batch sessions")
print("  data = simulator_default.generate_batch_sessions(num_sessions=100)")
print("\n  # Stream events in real-time")
print("  simulator_streaming.stream_events(duration_seconds=30)")
print("  df = simulator_streaming.get_streaming_dataframe()")
