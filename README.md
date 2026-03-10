# IntentScope - Behavioral Analytics Platform

This repository contains the **IntentScope** project - a production-ready behavioral analytics platform.

## Project Structure

```
animated-lamp-1/
├── IntentScope/          # Main project folder
│   ├── README.md        # Project documentation
│   ├── canvas.yaml      # Canvas configuration
│   ├── layer.yaml       # Layer definitions
│   └── src/             # Source code
│       ├── __init__.py
│       ├── load_dataset.py
│       ├── engineer_behavioral_features.py
│       ├── train_lstm_intention_classifier.py
│       ├── gamification_system_complete.py
│       ├── personalized_recommendation_engine.py
│       ├── deploy_flask_api_endpoint.py
│       └── ... (40+ modules)
└── requirements.txt     # Python dependencies
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Navigate to project
cd IntentScope

# Run data loading
python -m src.load_dataset
```

For full documentation, see [IntentScope/README.md](IntentScope/README.md)

## Description

IntentScope is a production-ready behavioral analytics platform combining offline machine learning training with real-time streaming inference. Features include:

- 54-feature behavioral engineering
- Gradient Boosting success prediction
- LSTM sequence modeling
- K-Means intention clustering (4 archetypes)
- Real-time REST API (<50ms latency)
- Gamification system
- Professional Plotly dashboards

## License

MIT License
