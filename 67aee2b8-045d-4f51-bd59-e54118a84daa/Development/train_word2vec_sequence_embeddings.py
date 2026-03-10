import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

print("=" * 70)
print("SEQUENCE EMBEDDINGS & K-MEANS FOR INTENTION INFERENCE")
print("=" * 70)

# Approach: Create sequence embeddings using TF-IDF on action sequences
# Combined with statistical features for richer representation

# Prepare action sequences (treat as documents for TF-IDF)
action_sequences_str = []
user_ids_seq_list = []

for _embed_uid in df_sorted['user_id'].unique():
    _embed_user_actions = df_sorted[df_sorted['user_id'] == _embed_uid]['action'].tolist()
    # Create sequence string (space-separated)
    action_sequences_str.append(' '.join(_embed_user_actions))
    user_ids_seq_list.append(_embed_uid)

print(f"\n✓ Prepared {len(action_sequences_str)} user action sequences")
print(f"✓ Sample sequence: '{action_sequences_str[0][:80]}...'")

# Create TF-IDF embeddings from action sequences
print("\n" + "=" * 70)
print("CREATING SEQUENCE EMBEDDINGS (TF-IDF)")
print("=" * 70)

# TF-IDF with n-grams to capture action sequences
tfidf_vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
    max_features=50,
    min_df=2
)

sequence_embeddings_tfidf = tfidf_vectorizer.fit_transform(action_sequences_str).toarray()

print(f"\n✓ TF-IDF sequence embeddings shape: {sequence_embeddings_tfidf.shape}")
print(f"✓ Number of features captured: {sequence_embeddings_tfidf.shape[1]}")
print(f"✓ Sample feature names: {tfidf_vectorizer.get_feature_names_out()[:10].tolist()}")

# Add behavioral features for richer embeddings
print("\n" + "=" * 70)
print("ENRICHING WITH BEHAVIORAL FEATURES")
print("=" * 70)

# Get key behavioral features from feature_matrix
behavioral_cols = [
    'total_interactions', 'unique_actions', 'overall_success_rate',
    'pct_advanced_premium', 'interactions_per_day', 'days_active',
    'complete_sessions', 'action_diversity_ratio'
]

user_behavioral_features = feature_matrix[['user_id'] + behavioral_cols].copy()
user_behavioral_features = user_behavioral_features.set_index('user_id').reindex(user_ids_seq_list).reset_index()

# Normalize behavioral features
from sklearn.preprocessing import StandardScaler
scaler_embed = StandardScaler()
behavioral_scaled = scaler_embed.fit_transform(user_behavioral_features[behavioral_cols])

# Combine sequence embeddings with behavioral features
combined_embeddings = np.hstack([sequence_embeddings_tfidf, behavioral_scaled])

print(f"\n✓ Combined embeddings shape: {combined_embeddings.shape}")
print(f"  • Sequence features: {sequence_embeddings_tfidf.shape[1]}")
print(f"  • Behavioral features: {behavioral_scaled.shape[1]}")

# Apply KMeans clustering to identify intention categories
print("\n" + "=" * 70)
print("K-MEANS CLUSTERING FOR INTENTION CATEGORIES")
print("=" * 70)

# Test different numbers of clusters (4 for Builder/Explorer/Learner/Abandoner)
n_clusters_intent = 4

print(f"\n✓ Applying K-Means with {n_clusters_intent} clusters...")

kmeans_intent = KMeans(n_clusters=n_clusters_intent, random_state=42, n_init=20, max_iter=500)
cluster_labels_intent = kmeans_intent.fit_predict(combined_embeddings)

# Calculate cluster quality metrics
silhouette_intent = silhouette_score(combined_embeddings, cluster_labels_intent)
davies_bouldin_intent = davies_bouldin_score(combined_embeddings, cluster_labels_intent)
calinski_harabasz_intent = calinski_harabasz_score(combined_embeddings, cluster_labels_intent)

print(f"\n✓ Clustering Quality Metrics (k={n_clusters_intent}):")
print(f"  • Silhouette Score: {silhouette_intent:.4f} (higher is better, range [-1, 1])")
print(f"  • Davies-Bouldin Index: {davies_bouldin_intent:.4f} (lower is better)")
print(f"  • Calinski-Harabasz Score: {calinski_harabasz_intent:.2f} (higher is better)")

# Cluster size distribution
cluster_counts_intent = pd.Series(cluster_labels_intent).value_counts().sort_index()
print(f"\n✓ Cluster Distribution:")
for _embed_cid, _embed_ccount in cluster_counts_intent.items():
    _embed_cpct = 100 * _embed_ccount / len(cluster_labels_intent)
    print(f"  • Cluster {_embed_cid}: {_embed_ccount} users ({_embed_cpct:.1f}%)")

# Create results dataframe with cluster assignments
_results_intent_df = pd.DataFrame({
    'user_id': user_ids_seq_list,
    'intention_cluster': cluster_labels_intent
})

# Merge with user_metrics to get behavioral statistics per cluster
results_intent_df = _results_intent_df.merge(user_metrics, on='user_id', how='left')

print("\n" + "=" * 70)
print("CLUSTER CHARACTERIZATION & INTENTION LABELS")
print("=" * 70)

# Analyze each cluster's behavior to assign intention labels
intention_labels_map = {}

for _embed_cluster_id in range(n_clusters_intent):
    _embed_cluster_users = results_intent_df[results_intent_df['intention_cluster'] == _embed_cluster_id]
    
    print(f"\n📊 CLUSTER {_embed_cluster_id} (n={len(_embed_cluster_users)}):")
    print(f"  • Avg interactions: {_embed_cluster_users['total_interactions'].mean():.1f}")
    print(f"  • Avg days active: {_embed_cluster_users['days_active'].mean():.1f}")
    print(f"  • Avg success rate: {_embed_cluster_users['success_rate'].mean():.2f}")
    print(f"  • Avg unique actions: {_embed_cluster_users['unique_actions'].mean():.1f}")
    print(f"  • Advanced usage: {_embed_cluster_users['advanced_usage_count'].mean():.1f}")
    print(f"  • Long-term success rate: {_embed_cluster_users['long_term_success'].mean():.2%}")
    print(f"  • Returned after first day: {_embed_cluster_users['returned_after_first_day'].mean():.2%}")
    
    # Determine intention label based on characteristics
    _embed_avg_interactions = _embed_cluster_users['total_interactions'].mean()
    _embed_avg_unique_actions = _embed_cluster_users['unique_actions'].mean()
    _embed_avg_advanced = _embed_cluster_users['advanced_usage_count'].mean()
    _embed_long_term_success = _embed_cluster_users['long_term_success'].mean()
    _embed_returned_rate = _embed_cluster_users['returned_after_first_day'].mean()
    
    # Label assignment logic
    if _embed_avg_interactions <= 4 and _embed_long_term_success < 0.2:
        _embed_intention_label = "Abandoner"
    elif _embed_avg_advanced >= 1.5 and _embed_avg_unique_actions >= 5.5:
        _embed_intention_label = "Builder"
    elif _embed_avg_unique_actions >= 5 and _embed_long_term_success >= 0.3:
        _embed_intention_label = "Explorer"
    else:
        _embed_intention_label = "Learner"
    
    intention_labels_map[_embed_cluster_id] = _embed_intention_label
    print(f"  → Intention Label: {_embed_intention_label}")

# Add intention labels to results
results_intent_df['intention_label'] = results_intent_df['intention_cluster'].map(intention_labels_map)

print("\n" + "=" * 70)
print("INTENTION DISTRIBUTION ANALYSIS")
print("=" * 70)

intention_distribution = results_intent_df['intention_label'].value_counts()
print("\n✓ User Intention Distribution:")
for _embed_intent_name, _embed_intent_count in intention_distribution.items():
    _embed_intent_pct = 100 * _embed_intent_count / len(results_intent_df)
    print(f"  • {_embed_intent_name}: {_embed_intent_count} users ({_embed_intent_pct:.1f}%)")

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print(f"\n✓ Model Type: Sequence Embeddings (TF-IDF) + Behavioral Features + K-Means")
print(f"✓ Total users clustered: {len(results_intent_df)}")
print(f"✓ Number of clusters: {n_clusters_intent}")
print(f"✓ Silhouette Score: {silhouette_intent:.4f}")
print(f"✓ Davies-Bouldin Index: {davies_bouldin_intent:.4f}")
print(f"✓ Calinski-Harabasz Score: {calinski_harabasz_intent:.2f}")
print(f"✓ Intention categories: {list(intention_labels_map.values())}")

print("\n✓ Available Variables:")
print("  • combined_embeddings: Sequence + behavioral embeddings")
print("  • kmeans_intent: Fitted K-Means model")
print("  • results_intent_df: DataFrame with user_id, cluster, intention label, metrics")
print("  • intention_labels_map: Cluster to intention mapping")
print("  • tfidf_vectorizer: Fitted TF-IDF vectorizer")
