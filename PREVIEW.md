# IntentScope Project Preview

## Virtual Environment Created ✅

A Python virtual environment has been created at: `venv/`

## Updated Requirements - AI Dependencies Optimized

The requirements.txt has been updated with proper AI/ML dependencies:
- **TensorFlow CPU** (tensorflow-cpu) - Optimized for CPU-based deep learning
- **Keras** - Neural network API
- **Scikit-learn** - Machine learning
- **XGBoost & LightGBM** - Gradient boosting
- **Redis & Websockets** - Real-time streaming support

## New AI Features Added

### 1. LSTM Intention Classifier ([`IntentScope/src/lstm_intention_classifier.py`](IntentScope/src/lstm_intention_classifier.py))
- **Bidirectional LSTM** architecture for sequence-based intention prediction
- BatchNormalization and Dropout for regularization
- Early stopping and learning rate reduction callbacks
- Multi-class classification (4 intention classes)
- Feature importance via permutation

### 2. Advanced AI Analytics ([`IntentScope/src/advanced_ai_analytics.py`](IntentScope/src/advanced_ai_analytics.py))
- **AnomalyDetector**: Isolation Forest-based anomaly detection
- **ChurnPredictor**: Random Forest churn prediction with risk segmentation
- **UserSegmenter**: K-Means/DBSCAN clustering for user segmentation
- **ABTestEngine**: A/B testing framework with statistical significance

## Project Structure

```
animated-lamp-1/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies (updated)
├── PREVIEW.md               # This preview file
├── venv/                     # Virtual environment
│   └── ...
└── IntentScope/              # Main application package
    ├── README.md             # Detailed documentation
    ├── canvas.yaml           # Canvas configuration
    ├── layer.yaml            # Layer configuration
    └── src/                  # Source code
        ├── __init__.py
        ├── lstm_intention_classifier.py    # NEW: LSTM Deep Learning
        ├── advanced_ai_analytics.py       # NEW: Anomaly, Churn, Segmentation, A/B Testing
        ├── engineer_behavioral_features.py
        ├── personalized_recommendation_engine.py
        ├── gamification_system_complete.py
        ├── heart_companion_layer.py
        ├── deploy_flask_api_endpoint.py
        └── [40+ additional modules]
```

## To Activate Virtual Environment

**Windows (cmd.exe):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Git Bash / Linux / macOS:**
```bash
source venv/bin/activate
```

## To Install Dependencies

After activating the virtual environment:
```bash
pip install -r requirements.txt
```

## Features Summary

### Core ML Features
- **LSTM Intention Classifier** - Deep learning for sequence prediction
- **Gradient Boosting Classifier** - Traditional ML approach
- **Behavioral Feature Engineering** - 50+ engineered features
- **Feature Importance & SHAP** - Model interpretability

### Advanced Analytics
- **Anomaly Detection** - Detect unusual user behavior
- **Churn Prediction** - Predict user attrition risk
- **User Segmentation** - Cluster-based user groups
- **A/B Testing** - Statistical experiment framework

### Production Features
- **Streaming Event Buffer** - Real-time data processing
- **Personalized Recommendations** - Next-best-action engine
- **Gamification System** - User engagement mechanics
- **Flask REST API** - Production-ready endpoints
- **Real-time Dashboards** - Live analytics visualization

## Quick Start

1. Activate virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Try new LSTM classifier:
   ```python
   from IntentScope.src.lstm_intention_classifier import run_lstm_classification
   lstm_classifier, results = run_lstm_classification()
   ```
4. Try Advanced Analytics:
   ```python
   from IntentScope.src.advanced_ai_analytics import run_advanced_analytics
   results = run_advanced_analytics()
   ```

---
*Generated: 2026-03-10*
