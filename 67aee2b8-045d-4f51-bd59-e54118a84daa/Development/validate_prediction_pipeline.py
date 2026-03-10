import numpy as np
import pandas as pd
import time

print("=" * 70)
print("PREDICTION PIPELINE VALIDATION")
print("=" * 70)

# ── 1. Confirm key model artefacts are present ──────────────────────────────
print("\n📦 MODEL ARTEFACTS")
print("-" * 50)
print(f"  • gb_classifier  : {type(gb_classifier).__name__}")
print(f"  • scaler_model   : {type(scaler_model).__name__}")
print(f"  • feature_cols   : {len(X_train_filled.columns)} features")
print(f"  • gb_intention_dist: {gb_intention_dist.to_dict()}")

# Capture the ordered feature list from training
api_feature_cols = list(X_train_filled.columns)  # 54 features, exact training order
print(f"\n✓ Feature list locked ({len(api_feature_cols)} features):")
for _i, _f in enumerate(api_feature_cols):
    print(f"    [{_i:02d}] {_f}")

# ── 2. CSV schema sample inputs ──────────────────────────────────────────────
# Raw CSV schema: user_id, timestamp, action, success, session_duration_minutes, feature_tier
# These feature rows represent aggregated behavioral features derived from the CSV,
# exactly matching the 54-feature schema used at training time.
print("\n" + "=" * 70)
print("CSV SCHEMA — SAMPLE INPUTS (aggregated from zerve_hackathon CSV format)")
print("=" * 70)

sample_csv_rows = [
    # User 99901: Active power user — should predict success=1, intention=Builder
    {
        "user_id": 99901,
        "total_interactions": 18, "days_active": 12, "interactions_per_day": 1.5,
        "freq_login": 3, "pct_login": 0.167,
        "freq_view_dashboard": 4, "pct_view_dashboard": 0.222,
        "freq_run_analysis": 5, "pct_run_analysis": 0.278,
        "freq_create_visualization": 3, "pct_create_visualization": 0.167,
        "freq_export_data": 2, "pct_export_data": 0.111,
        "freq_share_result": 1, "pct_share_result": 0.056,
        "freq_logout": 0, "pct_logout": 0.0,
        "freq_basic": 4, "freq_advanced": 9, "freq_premium": 5,
        "pct_advanced_premium": 0.778,
        "unique_actions": 6, "action_diversity_ratio": 1.0,
        "most_common_sequence_count": 3, "unique_sequences": 9,
        "has_login_analysis_pattern": 1, "has_analysis_viz_pattern": 1,
        "has_viz_export_pattern": 1, "has_export_share_pattern": 1,
        "complete_sessions": 12,
        "avg_hour_of_day": 10.5, "hour_std": 2.1,
        "pct_business_hours": 0.85, "pct_weekend": 0.10,
        "avg_time_between_interactions_hrs": 14.4,
        "median_time_between_interactions_hrs": 10.0,
        "std_time_between_interactions_hrs": 12.5, "max_gap_days": 2.5,
        "days_since_last_interaction": 1, "days_since_first_interaction": 11,
        "avg_session_duration": 22.0, "total_session_time_hrs": 6.6,
        "median_session_duration": 20.0, "max_session_duration": 45.0,
        "overall_success_rate": 0.89, "successful_actions": 16, "failed_actions": 2,
        "success_rate_run_analysis": 0.90,
        "success_rate_create_visualization": 0.95, "success_rate_export_data": 1.0,
        "tier_progression": 1, "advanced_user": 1,
        "early_success_rate": 0.85, "early_avg_session": 20.0,
    },
    # User 99902: Low-engagement abandoner — should predict success=0, intention=Abandoner
    {
        "user_id": 99902,
        "total_interactions": 2, "days_active": 1, "interactions_per_day": 2.0,
        "freq_login": 1, "pct_login": 0.5,
        "freq_view_dashboard": 1, "pct_view_dashboard": 0.5,
        "freq_run_analysis": 0, "pct_run_analysis": 0.0,
        "freq_create_visualization": 0, "pct_create_visualization": 0.0,
        "freq_export_data": 0, "pct_export_data": 0.0,
        "freq_share_result": 0, "pct_share_result": 0.0,
        "freq_logout": 0, "pct_logout": 0.0,
        "freq_basic": 2, "freq_advanced": 0, "freq_premium": 0,
        "pct_advanced_premium": 0.0,
        "unique_actions": 2, "action_diversity_ratio": 0.33,
        "most_common_sequence_count": 1, "unique_sequences": 1,
        "has_login_analysis_pattern": 0, "has_analysis_viz_pattern": 0,
        "has_viz_export_pattern": 0, "has_export_share_pattern": 0,
        "complete_sessions": 0,
        "avg_hour_of_day": 14.0, "hour_std": 0.0,
        "pct_business_hours": 0.5, "pct_weekend": 0.0,
        "avg_time_between_interactions_hrs": 1.0,
        "median_time_between_interactions_hrs": 1.0,
        "std_time_between_interactions_hrs": 0.0, "max_gap_days": 0.04,
        "days_since_last_interaction": 10, "days_since_first_interaction": 0,
        "avg_session_duration": 3.0, "total_session_time_hrs": 0.1,
        "median_session_duration": 3.0, "max_session_duration": 4.0,
        "overall_success_rate": 0.0, "successful_actions": 0, "failed_actions": 2,
        "success_rate_run_analysis": 0.0,
        "success_rate_create_visualization": 0.0, "success_rate_export_data": 0.0,
        "tier_progression": 0, "advanced_user": 0,
        "early_success_rate": 0.0, "early_avg_session": 3.0,
    },
    # User 99903: Moderate learner — mixed signals, expect Learner
    {
        "user_id": 99903,
        "total_interactions": 7, "days_active": 5, "interactions_per_day": 1.4,
        "freq_login": 2, "pct_login": 0.286,
        "freq_view_dashboard": 2, "pct_view_dashboard": 0.286,
        "freq_run_analysis": 2, "pct_run_analysis": 0.286,
        "freq_create_visualization": 1, "pct_create_visualization": 0.143,
        "freq_export_data": 0, "pct_export_data": 0.0,
        "freq_share_result": 0, "pct_share_result": 0.0,
        "freq_logout": 0, "pct_logout": 0.0,
        "freq_basic": 4, "freq_advanced": 3, "freq_premium": 0,
        "pct_advanced_premium": 0.429,
        "unique_actions": 4, "action_diversity_ratio": 0.67,
        "most_common_sequence_count": 2, "unique_sequences": 4,
        "has_login_analysis_pattern": 1, "has_analysis_viz_pattern": 1,
        "has_viz_export_pattern": 0, "has_export_share_pattern": 0,
        "complete_sessions": 3,
        "avg_hour_of_day": 9.0, "hour_std": 3.5,
        "pct_business_hours": 0.71, "pct_weekend": 0.14,
        "avg_time_between_interactions_hrs": 28.8,
        "median_time_between_interactions_hrs": 24.0,
        "std_time_between_interactions_hrs": 18.0, "max_gap_days": 3.0,
        "days_since_last_interaction": 2, "days_since_first_interaction": 4,
        "avg_session_duration": 14.0, "total_session_time_hrs": 1.6,
        "median_session_duration": 13.0, "max_session_duration": 22.0,
        "overall_success_rate": 0.57, "successful_actions": 4, "failed_actions": 3,
        "success_rate_run_analysis": 0.5,
        "success_rate_create_visualization": 1.0, "success_rate_export_data": 0.0,
        "tier_progression": 0, "advanced_user": 0,
        "early_success_rate": 0.5, "early_avg_session": 14.0,
    },
]

# ── 3. Run predictions end-to-end ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("END-TO-END PREDICTION PIPELINE TEST")
print("=" * 70)

pipeline_validation_results = []

for _sample in sample_csv_rows:
    _uid = _sample["user_id"]
    
    # Step 1: Build feature DataFrame with exact 54-col training order
    _features_df = pd.DataFrame([{col: _sample.get(col, 0) for col in api_feature_cols}])
    
    # Step 2: Scale via fitted scaler_model (StandardScaler)
    _t0 = time.time()
    _features_scaled = scaler_model.transform(_features_df)
    
    # Step 3: GradientBoostingClassifier predict_proba
    _success_prob = gb_classifier.predict_proba(_features_scaled)[0, 1]
    _predicted_success = int(_success_prob > 0.5)
    _latency_ms = (time.time() - _t0) * 1000
    
    # Step 4: Intention label via trained assign_gb_intention_label function
    _row_for_label = pd.Series({
        "gb_predicted_success": _predicted_success,
        "total_interactions": _sample["total_interactions"],
        "unique_actions": _sample["unique_actions"],
        "advanced_user": _sample["advanced_user"],
    })
    _intention = assign_gb_intention_label(_row_for_label)
    
    _result = {
        "user_id": _uid,
        "success_probability_pct": round(_success_prob * 100, 2),
        "predicted_success": _predicted_success,
        "intention_label": _intention,
        "inference_latency_ms": round(_latency_ms, 3),
        "features_used": len(api_feature_cols),
    }
    pipeline_validation_results.append(_result)
    
    print(f"\n👤 User {_uid}")
    print(f"   interactions={_sample['total_interactions']}  advanced_user={_sample['advanced_user']}  unique_actions={_sample['unique_actions']}")
    print(f"   Success Prob     : {_result['success_probability_pct']}%")
    print(f"   Predicted Success: {'✅ Yes' if _predicted_success else '❌ No'}")
    print(f"   Intention Label  : {_intention}")
    print(f"   Inference Latency: {_result['inference_latency_ms']} ms")

# ── 4. Pipeline summary table ─────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PIPELINE VALIDATION SUMMARY TABLE")
print("=" * 70)
pipeline_validation_df = pd.DataFrame(pipeline_validation_results)
print(pipeline_validation_df.to_string(index=False))

# ── 5. Model performance recap ────────────────────────────────────────────────
print("\n" + "=" * 70)
print("MODEL PERFORMANCE RECAP (from training block)")
print("=" * 70)
print(f"  • Model     : GradientBoostingClassifier (n_estimators=200, max_depth=5)")
print(f"  • Scaler    : StandardScaler (fit on {X_train_filled.shape[0]} training samples)")
print(f"  • Features  : {len(api_feature_cols)} behavioral features")
print(f"  • Test Acc  : {gb_test_acc:.4f}")
print(f"  • Test AUC  : {gb_test_auc:.4f}")
print(f"  • Test F1   : {gb_test_f1:.4f}")
print(f"  • Intentions: {gb_intention_dist.index.tolist()}")

# ── 6. Checklist ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("✅ SUCCESS CRITERIA CHECKLIST")
print("=" * 70)

_checks = {
    "gb_classifier present and functional":  hasattr(gb_classifier, 'predict_proba'),
    "scaler_model present and functional":   hasattr(scaler_model, 'transform'),
    "feature list has exactly 54 columns":   len(api_feature_cols) == 54,
    "3 sample users predicted successfully": len(pipeline_validation_results) == 3,
    "all results include success_probability_pct": all("success_probability_pct" in r for r in pipeline_validation_results),
    "all results include intention_label":   all("intention_label" in r for r in pipeline_validation_results),
    "all inference latencies < 500ms":       all(r["inference_latency_ms"] < 500 for r in pipeline_validation_results),
    "power user (99901) predicted success=1": pipeline_validation_results[0]["predicted_success"] == 1,
    "abandoner (99902) predicted success=0":  pipeline_validation_results[1]["predicted_success"] == 0,
    "intentions are valid category strings":  all(r["intention_label"] in ("Builder","Explorer","Learner","Abandoner") for r in pipeline_validation_results),
}

_all_passed = True
for _check, _passed in _checks.items():
    print(f"  {'✅' if _passed else '❌'} {_check}")
    if not _passed:
        _all_passed = False

print("\n" + ("🎉 ALL CHECKS PASSED — prediction pipeline fully confirmed!" if _all_passed else "⚠️  Some checks failed — review above"))
print("=" * 70)
