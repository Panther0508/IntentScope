import numpy as np
import pandas as pd
import time
from datetime import datetime
import random

print("=" * 70)
print("LIVE STREAMING EVENT SIMULATION WITH REAL-TIME PREDICTIONS")
print("=" * 70)

# Simulation parameters
simulation_duration_seconds = 30  # 30 seconds of streaming
events_per_second = 10  # Target throughput
num_users = 50

# Action types (matching training data)
action_types = ['login', 'view_dashboard', 'run_analysis', 'create_visualization', 
                'export_data', 'share_result', 'logout']
tiers = ['basic', 'advanced', 'premium']
tier_weights = [0.6, 0.3, 0.1]

print(f"\n⚙️ Simulation Configuration:")
print(f"  • Duration: {simulation_duration_seconds}s")
print(f"  • Target rate: {events_per_second} events/sec")
print(f"  • Expected total events: ~{simulation_duration_seconds * events_per_second}")
print(f"  • Simulated users: {num_users}")
print(f"  • Action types: {len(action_types)}")

# Clear buffer to start fresh
event_buffer.clear_all()

print("\n" + "=" * 70)
print("🔴 STREAMING SIMULATION STARTED")
print("=" * 70)

start_time = time.time()
event_count = 0
user_id_base = 70000  # New user IDs for simulation

# Track predictions
prediction_stream = []

# Simulate streaming events
delay_per_event = 1.0 / events_per_second

while (time.time() - start_time) < simulation_duration_seconds:
    # Generate simulated event
    user_id = user_id_base + random.randint(0, num_users - 1)
    action = random.choice(action_types)
    tier = random.choices(tiers, weights=tier_weights)[0]
    session_duration = random.randint(5, 120)  # seconds
    success = random.random() < 0.85  # 85% success rate
    feature_used = f"feature_{random.choice(['A', 'B', 'C', 'D', 'E'])}"
    
    # Process event through prediction engine
    prediction = prediction_engine.process_event(
        user_id=user_id,
        action=action,
        tier=tier,
        session_duration=session_duration,
        success=success,
        feature_used=feature_used
    )
    
    prediction_stream.append(prediction)
    event_count += 1
    
    # Display progress every 50 events
    if event_count % 50 == 0:
        elapsed = time.time() - start_time
        current_rate = event_count / elapsed
        print(f"  ⚡ Processed {event_count} events | Rate: {current_rate:.1f} events/sec | "
              f"Latest: User {user_id} → {prediction['intention_label']} "
              f"({prediction['success_probability']:.1f}% success)")
    
    # Rate limiting
    time.sleep(delay_per_event)

# Simulation complete
elapsed_time = time.time() - start_time
actual_rate = event_count / elapsed_time

print("\n" + "=" * 70)
print("⏹ STREAMING SIMULATION COMPLETED")
print("=" * 70)

print(f"\n📊 Simulation Results:")
print(f"  • Total events processed: {event_count}")
print(f"  • Actual duration: {elapsed_time:.2f}s")
print(f"  • Actual event rate: {actual_rate:.2f} events/sec")
print(f"  • Unique users: {len(set(p['user_id'] for p in prediction_stream))}")

# Get performance statistics
perf_stats = prediction_engine.get_performance_stats()

print(f"\n⚡ Prediction Engine Performance:")
print(f"  • Total predictions: {perf_stats['total_predictions']}")
print(f"  • Average latency: {perf_stats['avg_latency_ms']:.2f}ms per prediction")
print(f"  • Total prediction time: {perf_stats['total_time_seconds']:.2f}s")
print(f"  • Throughput capacity: {perf_stats['throughput_per_second']:.2f} predictions/sec")

# Analyze predictions
predictions_df = pd.DataFrame(prediction_stream)

print(f"\n🎯 Prediction Results Analysis:")
print(f"\n  Intention Distribution:")
for intention, count in predictions_df['intention_label'].value_counts().items():
    pct = (count / len(predictions_df)) * 100
    avg_prob = predictions_df[predictions_df['intention_label'] == intention]['success_probability'].mean()
    print(f"    • {intention}: {count} predictions ({pct:.1f}%) - "
          f"Avg success prob: {avg_prob:.1f}%")

print(f"\n  Success Probability Statistics:")
print(f"    • Mean: {predictions_df['success_probability'].mean():.1f}%")
print(f"    • Median: {predictions_df['success_probability'].median():.1f}%")
print(f"    • Min: {predictions_df['success_probability'].min():.1f}%")
print(f"    • Max: {predictions_df['success_probability'].max():.1f}%")
print(f"    • Std: {predictions_df['success_probability'].std():.1f}%")

print(f"\n  Confidence Score Statistics:")
print(f"    • Mean confidence: {predictions_df['confidence_score'].mean():.1f}%")
print(f"    • Median confidence: {predictions_df['confidence_score'].median():.1f}%")
print(f"    • Min confidence: {predictions_df['confidence_score'].min():.1f}%")
print(f"    • Max confidence: {predictions_df['confidence_score'].max():.1f}%")

print(f"\n  Latency Performance:")
print(f"    • Mean total latency: {predictions_df['total_latency_ms'].mean():.2f}ms")
print(f"    • Median total latency: {predictions_df['total_latency_ms'].median():.2f}ms")
print(f"    • P95 latency: {predictions_df['total_latency_ms'].quantile(0.95):.2f}ms")
print(f"    • P99 latency: {predictions_df['total_latency_ms'].quantile(0.99):.2f}ms")
print(f"    • Max latency: {predictions_df['total_latency_ms'].max():.2f}ms")

print(f"\n  Feature Extraction Performance:")
print(f"    • Mean extraction time: {predictions_df['feature_extraction_time_ms'].mean():.2f}ms")
print(f"    • Median extraction time: {predictions_df['feature_extraction_time_ms'].median():.2f}ms")
print(f"    • Max extraction time: {predictions_df['feature_extraction_time_ms'].max():.2f}ms")

# Sample predictions
print(f"\n📋 Sample Predictions (First 10):")
sample_cols = ['user_id', 'action', 'intention_label', 'success_probability', 'confidence_score', 'total_latency_ms']
print(predictions_df[sample_cols].head(10).to_string(index=False))

print(f"\n📋 Sample Predictions (Last 10):")
print(predictions_df[sample_cols].tail(10).to_string(index=False))

# Success criteria validation
print("\n" + "=" * 70)
print("✅ SUCCESS CRITERIA VALIDATION")
print("=" * 70)

criteria = []

# 1. Block outputs live prediction stream
criteria.append(("Live prediction stream output", len(prediction_stream) > 0))

# 2. Intention classifications present
unique_intentions = predictions_df['intention_label'].nunique()
criteria.append(("Intention classifications present", unique_intentions >= 2))

# 3. Success probabilities calculated
has_success_probs = predictions_df['success_probability'].notna().all()
criteria.append(("Success probabilities calculated", has_success_probs))

# 4. Confidence scores included
has_confidence = predictions_df['confidence_score'].notna().all()
criteria.append(("Confidence scores included", has_confidence))

# 5. Real-time processing (<100ms target)
meets_latency = predictions_df['total_latency_ms'].median() < 100
criteria.append((f"Real-time latency target (<100ms median)", meets_latency))

# 6. Processed simulated interactions
processed_events = len(prediction_stream) >= simulation_duration_seconds * events_per_second * 0.9
criteria.append(("Processed expected event volume", processed_events))

# 7. Multiple users tracked
multiple_users = len(set(p['user_id'] for p in prediction_stream)) > 10
criteria.append(("Multiple users tracked", multiple_users))

print(f"\n✓ Validation Results:")
for criterion, met in criteria:
    status = "✅ PASS" if met else "❌ FAIL"
    print(f"  {status} - {criterion}")

all_criteria_met = all(met for _, met in criteria)

print("\n" + "=" * 70)
if all_criteria_met:
    print("🎉 ALL SUCCESS CRITERIA MET!")
else:
    print("⚠️ SOME CRITERIA NOT MET - Review above")
print("=" * 70)

print(f"\n✓ Available outputs:")
print(f"  • predictions_df: DataFrame with {len(predictions_df)} predictions")
print(f"  • perf_stats: Performance statistics dictionary")
print(f"  • prediction_stream: List of prediction dictionaries")
print(f"  • event_buffer: Updated buffer with {event_buffer.total_events_received} events")
