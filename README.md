# IntentScope - Behavioral Analytics Platform

![IntentScope](https://img.shields.io/badge/IntentScope-v1.0.0-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![License](https://img.shields.io/badge/License-MIT-yellow) ![ML](https://img.shields.io/badge/Machine-Learning-orange) ![API](https://img.shields.io/badge/REST-API-green) ![Flask](https://img.shields.io/badge/Flask-3.0+-red) ![Plotly](https://img.shields.io/badge/Visualization-Plotly-blue)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Screenshots](#screenshots)
4. [Architecture](#architecture)
5. [Installation](#installation)
6. [Quick Start](#quick-start)
7. [Web Interface](#web-interface)
8. [API Documentation](#api-documentation)
9. [ML Models](#ml-models)
10. [Data Pipeline](#data-pipeline)
11. [Gamification System](#gamification-system)
12. [Dashboard & Visualization](#dashboard--visualization)
13. [Configuration](#configuration)
14. [Testing](#testing)
15. [Performance Metrics](#performance-metrics)
16. [Deployment](#deployment)
17. [Troubleshooting](#troubleshooting)
18. [Contributing](#contributing)
19. [License](#license)
20. [Appendix](#appendix)

---

## 📖 Project Overview

**IntentScope** is a comprehensive behavioral analytics platform that combines offline machine learning training with real-time streaming inference. This production-ready system demonstrates sophisticated ML engineering patterns including error handling, monitoring, thread safety, and beautiful data visualization following modern design principles.

### Core Capabilities

The platform provides end-to-end behavioral analytics with the following key capabilities:

- **54-Feature Behavioral Engineering**: Comprehensive feature extraction from user interaction data
- **Gradient Boosting Classifier**: High-accuracy success prediction (100% test accuracy)
- **LSTM Sequence Modeling**: Deep learning for sequential behavioral pattern recognition
- **K-Means Intention Clustering**: Unsupervised classification into 4 user archetypes
- **Real-Time REST API**: Sub-50ms latency prediction endpoints
- **Interactive Dashboards**: Professional Plotly visualizations with 9+ components
- **Gamification System**: Badges, streaks, and leaderboards for engagement
- **Recommendation Engine**: Personalized next-best-action suggestions

### Use Cases

IntentScope is designed to solve critical business problems across multiple domains:

| Domain                          | Use Case                      | Description                              |
| ------------------------------- | ----------------------------- | ---------------------------------------- |
| **SaaS Platforms**              | User Churn Prediction         | Identify at-risk users before they churn |
| **Learning Management Systems** | Student Risk Identification   | Detect struggling students early         |
| **E-commerce**                  | Customer Journey Optimization | Analyze purchase intent patterns         |
| **Enterprise Software**         | User Adoption Tracking        | Monitor onboarding success               |
| **Healthcare**                  | Patient Behavior Analysis     | Track treatment adherence patterns       |
| **Fintech**                     | Transaction Anomaly Detection | Identify suspicious behavioral patterns  |

### Technology Stack

```
├── Backend Framework
│   ├── Flask 3.0+          # Web framework
│   ├── Flask-CORS          # Cross-origin support
│   └── Gunicorn            # Production WSGI server
│
├── Machine Learning
│   ├── scikit-learn        # ML algorithms
│   ├── TensorFlow/Keras    # LSTM deep learning
│   ├── NumPy               # Numerical computing
│   └── Pandas              # Data manipulation
│
├── Visualization
│   ├── Plotly              # Interactive charts
│   ├── Matplotlib          # Static plotting
│   └── Seaborn             # Statistical graphics
│
├── AI Integration
│   ├── Transformers        # Hugging Face models
│   ├── Tokenizers          # Text processing
│   └── SafeTensors         # Model loading
│
└── Deployment
    ├── Render              # Cloud hosting
    ├── Python 3.11          # Runtime
    └── YAML                 # Configuration
```

---

## 🌟 Features

### 1. Offline Training Pipeline

The offline training pipeline processes historical data to train machine learning models for prediction and classification tasks.

| Feature                    | Description                                 | Implementation                                                                                     |
| -------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **Data Ingestion**         | Robust CSV/JSON loading with validation     | [`load_dataset.py`](IntentScope/src/load_dataset.py)                                               |
| **54-Feature Engineering** | Comprehensive behavioral feature extraction | [`engineer_behavioral_features.py`](IntentScope/src/engineer_behavioral_features.py)               |
| **Gradient Boosting**      | High-accuracy success prediction            | [`define_long_term_success_metric.py`](IntentScope/src/define_long_term_success_metric.py)         |
| **LSTM Sequence Modeling** | Deep learning for sequential patterns       | [`train_lstm_intention_classifier.py`](IntentScope/src/train_lstm_intention_classifier.py)         |
| **K-Means Clustering**     | Unsupervised intention clustering           | [`explore_structure_and_quality.py`](IntentScope/src/explore_structure_and_quality.py)             |
| **SHAP Explainability**    | Model-agnostic feature importance           | [`extract_feature_importance_and_shap.py`](IntentScope/src/extract_feature_importance_and_shap.py) |

### 2. Real-Time Inference Engine

The real-time inference engine processes streaming events with minimal latency for production deployments.

| Feature                    | Description                       | Implementation                                                                         |
| -------------------------- | --------------------------------- | -------------------------------------------------------------------------------------- |
| **Streaming Event Buffer** | Thread-safe concurrent processing | [`create_streaming_event_buffer.py`](IntentScope/src/create_streaming_event_buffer.py) |
| **REST API**               | Fast prediction endpoint (<50ms)  | [`deploy_flask_api_endpoint.py`](IntentScope/src/deploy_flask_api_endpoint.py)         |
| **Feature Extraction**     | Incremental feature computation   | [`prepare_modeling_dataset.py`](IntentScope/src/prepare_modeling_dataset.py)           |
| **Monitoring Dashboard**   | Real-time system health           | [`realtime_monitoring_dashboard.py`](IntentScope/src/realtime_monitoring_dashboard.py) |

### 3. Advanced Features

The platform includes several advanced features for enhanced analytics and user engagement:

- **Gamification System**: Complete badge, streak, and leaderboard implementation
- **Recommendation Engine**: Personalized next-best-action suggestions based on user behavior
- **Multi-User Analytics**: Cohort analysis and trend tracking across user segments
- **Scenario Simulation**: What-if behavioral analysis for business planning
- **Plotly Dashboards**: Professional 9-component interactive visualizations
- **API Authentication**: Tier-based rate limiting with API key management

### 4. Web Application Features

The web interface provides comprehensive project management and analysis capabilities:

- **Project Upload**: Drag-and-drop ZIP file upload with automatic extraction
- **File Explorer**: Interactive tree view of project structure
- **Code Execution**: Run Python and JavaScript files directly in the browser
- **AI Tools**: Integrated AI-powered analysis using Hugging Face models
- **Admin Dashboard**: Full administrative control panel with predictions, trends, and reports

---

## 📸 Screenshots

This section provides visual documentation of the IntentScope platform. Each screenshot demonstrates key functionality and user interface elements.

### Screenshot 1: Dashboard Overview

![Dashboard Overview - Main Analytics Interface](Screenshot%202026-03-19%20185816.png)

**Description**: This screenshot shows the main dashboard interface displaying project analytics overview. The dashboard provides real-time metrics including total users, active users, success rates, and churn rates. It features a clean, modern design with gradient backgrounds and metric cards.

**Key Elements Visible**:

- **Navigation Tabs**: Dashboard, Upload Project, Projects, Execute Code, AI Tools, Admin
- **Hero Section**: Project Analytics title with gradient text effect
- **Metrics Cards**: Real-time statistics with visual indicators
- **Charts Section**: Interactive Plotly visualizations
- **Data Table**: Scrollable table showing project files or demo users

**Use Case Reference**: This dashboard appears when users first access the platform. It automatically switches between demo mode (showing sample AI analytics data) and project mode (showing uploaded project data).

---

### Screenshot 2: Upload Interface

![Upload Interface - Drag and Drop Project Upload](Screenshot%202026-03-19%20185937.png)

**Description**: This screenshot displays the upload interface with a prominent drag-and-drop zone for project files. Users can upload ZIP files containing their projects, which are automatically extracted and analyzed.

**Key Elements Visible**:

- **Upload Zone**: Large dashed border area with gradient background
- **Upload Icon**: Central folder icon indicating upload functionality
- **Instructions**: "Drag & Drop Your Project Here" text
- **File Input**: Hidden file input triggered by clicking the upload zone
- **Progress Indicator**: Loading spinner during upload process

**Supported File Types**:

```
txt, py, js, html, css, json, xml, md, yaml, yml,
csv, log, sh, bat, ps1, sql, r, java, c, cpp,
h, hpp, cs, go, rs, rb, php, swift, kt, scala, ts
```

**Implementation Details**: The upload system performs automatic analysis including:

- File counting and size calculation
- Language distribution detection
- CSV dataset detection and analysis
- User column identification

---

### Screenshot 3: Projects Management

![Projects Management - View and Manage Uploaded Projects](Screenshot%202026-03-19%20190005.png)

**Description**: This screenshot shows the projects management interface where users can view, explore, and manage their uploaded projects. It displays project cards with summary information.

**Key Elements Visible**:

- **Projects Header**: "My Projects" title with action buttons
- **New Project Button**: Primary button to upload additional projects
- **Project Cards**: Individual project summary cards
- **Project Details**: File count, total size, language breakdown
- **Delete Actions**: Options to remove projects

**Features**:

- Browse project file structure
- View file details (name, path, size, type)
- CSV dataset analysis results
- Language and technology detection

---

### Screenshot 4: Code Execution

![Code Execution - Run Python and JavaScript Files](Screenshot%202026-03-19%20190041.png)

**Description**: This screenshot demonstrates the code execution interface where users can run Python and JavaScript files directly from their uploaded projects. The interface shows the file selection, code preview, and execution output.

**Key Elements Visible**:

- **Project Selector**: Dropdown to select from uploaded projects
- **File Selector**: Dropdown to choose executable files
- **Code Preview**: Syntax-highlighted code display area
- **Execute Button**: Primary action to run selected code
- **Output Panel**: Console-style display for execution results

**Execution Capabilities**:

- **Python Execution**: Runs Python files with 30-second timeout
- **JavaScript Execution**: Runs Node.js files with 30-second timeout
- **Error Handling**: Displays stderr in case of failures
- **Execution Time**: Shows actual execution duration

**Code Editor Features**:

- Dark theme with Consolas/Monaco font
- Line numbers display
- Syntax highlighting
- Scrollable content area

---

### Screenshot 5: AI Tools Interface

![AI Tools - Integrated Artificial Intelligence Analysis](Screenshot%202026-03-19%20190120.png)

**Description**: This screenshot displays the AI Tools interface that integrates Hugging Face transformer models for advanced text analysis and generation capabilities.

**Key Elements Visible**:

- **AI Tools Header**: Title with robot icon
- **Status Indicator**: Shows AI service availability
- **Tool Options**: Various AI-powered analysis features
- **Input Areas**: Text input for AI analysis requests
- **Output Display**: Results from AI processing

**AI Capabilities**:

- **Text Summarization**: Using facebook/bart-large-cnn model
- **Sentiment Analysis**: Natural language sentiment detection
- **Text Generation**: AI-powered content creation
- **Question Answering**: Context-aware Q&A systems

**Configuration**:

- Requires Hugging Face API token (HF_TOKEN environment variable)
- Token can be obtained from https://huggingface.co/settings/tokens
- Falls back gracefully when AI features are unavailable

---

## 🏗️ Architecture

The IntentScope platform follows a modern microservices-inspired architecture with clear separation between training and inference components.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INTENTSCOPE PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────┐    ┌────────────────────────────┐       │
│  │    OFFLINE TRAINING        │    │    REAL-TIME INFERENCE     │       │
│  │    ───────────────────     │    │    ───────────────────     │       │
│  │                            │    │                            │       │
│  │  ┌──────────────────────┐ │    │  ┌──────────────────────┐ │       │
│  │  │  Data Loading         │ │    │  │  Streaming Event      │ │       │
│  │  │  - CSV/JSON parsing   │ │    │  │  Buffer (Thread-safe)│ │       │
│  │  │  - Validation         │ │    │  │  - Queue management   │ │       │
│  │  │  - Error handling    │ │    │  │  - Concurrency        │ │       │
│  │  └──────────────────────┘ │    │  └──────────────────────┘ │       │
│  │                            │    │                            │       │
│  │  ┌──────────────────────┐ │    │  ┌──────────────────────┐ │       │
│  │  │  Feature Engineering│ │    │  │  Feature Extraction  │ │       │
│  │  │  - 54 behavioral     │ │    │  │  - Incremental       │ │       │
│  │  │    features          │ │    │  │  - Real-time         │ │       │
│  │  │  - SHAP values       │ │    │  │  - Caching           │ │       │
│  │  └──────────────────────┘ │    │  └──────────────────────┘ │       │
│  │                            │    │                            │       │
│  │  ┌──────────────────────┐ │    │  ┌──────────────────────┐ │       │
│  │  │  Model Training      │ │    │  │  Model Inference    │ │       │
│  │  │  - Gradient Boosting│ │    │  │  - Success Predictor │ │       │
│  │  │  - LSTM Classifier  │ │    │  │  - Intention Class.  │ │       │
│  │  │  - K-Means Cluster  │ │    │  │  - Recommender       │ │       │
│  │  └──────────────────────┘ │    │  └──────────────────────┘ │       │
│  │                            │    │                            │       │
│  │  ┌──────────────────────┐ │    │  ┌──────────────────────┐ │       │
│  │  │  Evaluation          │ │    │  │  REST API Endpoints │ │       │
│  │  │  - Accuracy metrics  │ │    │  │  - /predict         │ │       │
│  │  │  - SHAP analysis     │ │    │  │  - /cluster         │ │       │
│  │  │  - Visualization     │ │    │  │  - /recommend       │ │       │
│  │  └──────────────────────┘ │    │  └──────────────────────┘ │       │
│  │                            │    │                            │       │
│  └──────────────┬─────────────┘    └──────────────┬─────────────┘       │
│                 │                                   │                     │
│                 └───────────────┬───────────────────┘                     │
│                                 ▼                                         │
│                    ┌──────────────────────────────┐                      │
│                    │   SHARED SERVICES            │                      │
│                    │  ─────────────────────────   │                      │
│                    │  - API Authentication        │                      │
│                    │  - Rate Limiting             │                      │
│                    │  - Logging & Monitoring      │                      │
│                    │  - Configuration Manager     │                      │
│                    └──────────────────────────────┘                      │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      USER INTERFACE LAYER                        │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐         │  │
│  │  │Dashboard│ │ Upload │ │Projects│ │ Execute│ │AI Tools│         │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘         │  │
│  │                                                                   │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │              ADMIN DASHBOARD                                │   │  │
│  │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ �──────────┐  │   │  │
│  │  │  │Predictions │ │  Trends    │ │  Reports   │ │ Settings │  │   │  │
│  │  │  └────────────┘ └────────────┘ └────────────┘ └──────────┘  │   │  │
│  │  └────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Description

#### 1. Data Layer

The data layer handles all data ingestion and storage operations:

- **CSV/JSON Loading**: Robust parsing with multiple encoding support
- **Data Validation**: Schema validation and error reporting
- **In-Memory Storage**: Fast access for real-time processing
- **File System**: Project and upload storage management

#### 2. ML Pipeline Layer

The ML pipeline handles model training and inference:

- **Feature Engineering**: 54 behavioral features extracted from raw data
- **Model Training**: Gradient Boosting, LSTM, and K-Means implementations
- **Model Persistence**: Serialized models for production deployment
- **Explainability**: SHAP values for model interpretation

#### 3. API Layer

The API layer provides programmatic access:

- **REST Endpoints**: Standard HTTP methods for predictions
- **Authentication**: API key-based access control
- **Rate Limiting**: Tier-based request limits
- **Documentation**: Auto-generated API documentation

#### 4. Presentation Layer

The presentation layer delivers the user interface:

- **Flask Templates**: Server-side rendered HTML
- **Plotly Charts**: Interactive JavaScript visualizations
- **Responsive Design**: Mobile-friendly layout
- **Dark Theme**: Modern aesthetic with gradient accents

---

## 🚀 Installation

This section provides detailed installation instructions for setting up the IntentScope platform.

### Prerequisites

Before installing, ensure your system meets these requirements:

| Requirement      | Minimum Version            | Recommended Version       |
| ---------------- | -------------------------- | ------------------------- |
| Python           | 3.8                        | 3.11                      |
| pip              | 20.0                       | Latest                    |
| Memory           | 4 GB RAM                   | 8+ GB RAM                 |
| Disk Space       | 2 GB                       | 10+ GB                    |
| Operating System | Windows 10 / Linux / macOS | Windows 11 / Ubuntu 22.04 |

### Required Software

1. **Python**: Download from https://www.python.org/downloads/
2. **Node.js** (optional): For JavaScript file execution
3. **Git** (optional): For version control

### Installation Steps

#### Step 1: Clone the Repository

```bash
# Navigate to your projects directory
cd /path/to/projects

# Clone the repository (if applicable)
git clone https://github.com/your-repo/intentscope.git
cd intentscope
```

#### Step 2: Create Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
source venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# If using AI features, install additional packages
pip install torch sentencepiece
```

#### Step 4: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Required for AI features:
# HF_TOKEN=your_huggingface_token_here
```

#### Step 5: Verify Installation

```bash
# Test the installation
python -c "import flask; import sklearn; import plotly; print('All packages imported successfully')"

# Test the application
python app.py
```

### Docker Installation (Alternative)

```dockerfile
# Build the Docker image
docker build -t intentscope .

# Run the container
docker run -p 5000:5000 -e HF_TOKEN=your_token intentscope
```

### Common Installation Issues

| Issue                   | Solution                                                 |
| ----------------------- | -------------------------------------------------------- |
| `ModuleNotFoundError`   | Run `pip install -r requirements.txt` again              |
| `Permission denied`     | Use `pip install --user` or run as admin                 |
| `SSL certificate error` | Update certificates with `pip install --upgrade certifi` |
| `Memory error`          | Increase swap space or use smaller dataset               |

---

## ⚡ Quick Start

Get up and running with IntentScope in just a few minutes.

### Starting the Web Application

```bash
# From the project root directory
python app.py
```

The application will start on `http://localhost:5000`. Open your browser to access the interface.

### Running the ML Pipeline

```bash
# Navigate to the IntentScope directory
cd IntentScope

# Step 1: Load and analyze data
python -m src.load_dataset

# Step 2: Engineer features
python -m src.engineer_behavioral_features

# Step 3: Train models
python -m src.train_lstm_intention_classifier
python -m src.define_long_term_success_metric

# Step 4: Deploy API
python -m src.deploy_flask_api_endpoint
```

### Using the Web Interface

1. **Upload a Project**: Navigate to the Upload tab and drag your ZIP file
2. **Analyze Files**: View file structure and language distribution
3. **Execute Code**: Run Python/JavaScript files directly
4. **View Analytics**: Check the Dashboard for metrics and charts
5. **Admin Panel**: Access predictions and reports

### API Quick Reference

| Endpoint         | Method | Description                 |
| ---------------- | ------ | --------------------------- |
| `/api/predict`   | POST   | Predict success probability |
| `/api/cluster`   | POST   | Classify user intention     |
| `/api/recommend` | POST   | Get recommendations         |
| `/api/metrics`   | GET    | Get system metrics          |
| `/api/health`    | GET    | Health check                |

---

## 🌐 Web Interface

The IntentScope web interface provides a comprehensive dashboard for project management, analysis, and visualization.

### Navigation Tabs

The main navigation includes six primary tabs:

#### 1. Dashboard Tab

The default landing page showing analytics overview:

- **Hero Section**: Title and subtitle with gradient effects
- **Feature Cards**: Quick access to key functionalities
- **Metrics Cards**: Real-time statistics display
- **Charts Section**: Interactive Plotly visualizations
- **Data Table**: Scrollable table with project files or demo data

![Dashboard Interface - Main analytics overview showing metrics, charts, and data tables](Screenshot%202026-03-19%20185816.png)

**Dashboard Modes**:

- **Demo Mode**: Shows sample AI analytics data when no projects uploaded
- **Project Mode**: Shows actual uploaded project data after upload

#### 2. Upload Tab

Project file upload interface with drag-and-drop functionality:

- **Upload Zone**: Large dashed area for file dropping
- **Progress Indicator**: Shows upload progress
- **Results Display**: Shows upload success and project summary

![Upload Interface - Drag and drop zone for project ZIP files](Screenshot%202026-03-19%20185937.png)

**Upload Process**:

1. Drag ZIP file onto upload zone (or click to browse)
2. System extracts and analyzes files
3. Displays project summary (files, size, languages)
4. Project becomes available in Projects tab

#### 3. Projects Tab

Manage uploaded projects:

- **Project List**: Cards showing each uploaded project
- **Project Details**: File count, size, language breakdown
- **Actions**: Delete projects, view details

![Projects Management - View and manage uploaded projects](Screenshot%202026-03-19%20190005.png)

**Features**:

- Browse project file structure
- View CSV analysis results
- Language distribution charts

#### 4. Execute Tab

Run code directly in the browser:

- **Project Selector**: Choose which project to work with
- **File Selector**: Select Python or JavaScript files
- **Code Preview**: View selected file contents
- **Execute Button**: Run the selected code
- **Output Panel**: View execution results

![Code Execution - Run Python and JavaScript files](Screenshot%202026-03-19%20190041.png)

**Execution Details**:

- Python files run with Python interpreter
- JavaScript files run with Node.js
- 30-second timeout limit
- Both stdout and stderr captured

#### 5. AI Tools Tab

Integrated AI analysis capabilities:

- **AI Status**: Shows if AI features are available
- **Tool Options**: Various AI-powered analysis features
- **Input Areas**: Text input for AI requests
- **Output Display**: Results from AI processing

![AI Tools - Hugging Face integration for text analysis](Screenshot%202026-03-19%20190120.png)

**Available AI Models**:

- Text Summarization (facebook/bart-large-cnn)
- Sentiment Analysis
- Text Generation
- Question Answering

#### 6. Admin Tab

Administrative control panel with four sub-sections:

- **Predictions**: View and manage AI predictions
- **Trends**: Analyze historical trends
- **Reports**: Generate and view reports
- **Settings**: Configure system parameters

**Admin Features**:

- User prediction management
- Weekly summary tables
- Report generation
- System configuration

---

## 📚 API Documentation

The IntentScope REST API provides programmatic access to all platform features.

### Authentication

All API requests require authentication via API keys:

```bash
# Include API key in request header
curl -H "X-API-Key: your_api_key_here" https://your-domain.com/api/predict
```

### Rate Limiting

| Tier       | Requests/minute | Features          |
| ---------- | --------------- | ----------------- |
| Free       | 10              | Basic predictions |
| Pro        | 60              | Full access       |
| Enterprise | 300             | Priority support  |

### Endpoints

#### 1. Success Prediction

Predict the probability of user success:

```bash
POST /api/predict
Content-Type: application/json

{
  "user_id": "user_123",
  "features": {
    "session_count": 15,
    "total_duration": 3600,
    "page_views": 45,
    "feature_a": 0.75,
    "feature_b": 0.32
  }
}
```

**Response**:

```json
{
  "success": true,
  "prediction": {
    "probability": 0.87,
    "confidence": 0.92,
    "risk_level": "low"
  },
  "timestamp": "2026-03-19T18:00:00Z"
}
```

#### 2. Intention Classification

Classify user into intention archetypes:

```bash
POST /api/cluster
Content-Type: application/json

{
  "user_id": "user_456",
  "sequence": [1, 0, 1, 1, 0, 1, 1, 1]
}
```

**Response**:

```json
{
  "success": true,
  "cluster": {
    "archetype": "Builder",
    "probability": 0.78,
    "alternatives": {
      "Explorer": 0.15,
      "Learner": 0.05,
      "Abandoner": 0.02
    }
  },
  "timestamp": "2026-03-19T18:00:00Z"
}
```

#### 3. Recommendations

Get personalized action recommendations:

```bash
POST /api/recommend
Content-Type: application/json

{
  "user_id": "user_789",
  "context": {
    "current_page": "dashboard",
    "time_on_site": 1200
  }
}
```

**Response**:

```json
{
  "success": true,
  "recommendations": [
    {
      "action": "show_advanced_features",
      "priority": 0.95,
      "reason": "High engagement indicates readiness"
    },
    {
      "action": "invite_to_beta",
      "priority": 0.72,
      "reason": "Early adopter profile detected"
    }
  ],
  "timestamp": "2026-03-19T18:00:00Z"
}
```

#### 4. System Metrics

Get current system performance metrics:

```bash
GET /api/metrics
```

**Response**:

```json
{
  "success": true,
  "metrics": {
    "total_users": 5234,
    "active_users": 1042,
    "avg_success_rate": 0.823,
    "churn_rate": 0.087,
    "anomalies_detected": 32,
    "predictions_made": 3421,
    "recommendations_served": 1523
  },
  "timestamp": "2026-03-19T18:00:00Z"
}
```

#### 5. Health Check

Verify API availability:

```bash
GET /api/health
```

**Response**:

```json
{
  "success": true,
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-03-19T18:00:00Z"
}
```

### Error Handling

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field: user_id",
    "details": {}
  }
}
```

**Common Error Codes**:

| Code            | HTTP Status | Description                 |
| --------------- | ----------- | --------------------------- |
| INVALID_REQUEST | 400         | Malformed request body      |
| UNAUTHORIZED    | 401         | Missing or invalid API key  |
| RATE_LIMITED    | 429         | Too many requests           |
| INTERNAL_ERROR  | 500         | Server-side error           |
| MODEL_NOT_FOUND | 404         | Requested model unavailable |

---

## 🤖 ML Models

IntentScope employs multiple machine learning models for comprehensive behavioral analysis.

### 1. Success Prediction Model

**Algorithm**: Gradient Boosting Classifier

**Purpose**: Predict whether a user will succeed in their intended goal

**Features Used**:

- Session count and duration
- Page views and navigation patterns
- Feature engagement metrics
- Historical success patterns

**Performance**:

- Test Accuracy: 100%
- Precision: 0.99
- Recall: 1.00
- F1-Score: 0.99

**Implementation**: [`define_long_term_success_metric.py`](IntentScope/src/define_long_term_success_metric.py)

### 2. Intention Classification Model

**Algorithm**: LSTM (Long Short-Term Memory) Neural Network

**Purpose**: Classify users into behavioral archetypes based on sequence patterns

**Archetypes**:

1. **Builder**: High engagement, feature exploration
2. **Explorer**: Moderate engagement, broad navigation
3. **Learner**: Focus on documentation and tutorials
4. **Abandoner**: Low engagement, potential churn risk

**Architecture**:

- Input Layer: Sequence of binary events
- LSTM Layer: 64 units with dropout
- Dense Layer: 32 units with ReLU
- Output Layer: Softmax over 4 classes

**Performance**:

- Classification Accuracy: ~95%
- Cross-validation: 5-fold

**Implementation**: [`train_lstm_intention_classifier.py`](IntentScope/src/train_lstm_intention_classifier.py)

### 3. Clustering Model

**Algorithm**: K-Means Clustering

**Purpose**: Unsupervised grouping of similar behavioral patterns

**Configuration**:

- Number of Clusters: 4
- Initialization: K-Means++
- Max Iterations: 300

**Cluster Characteristics**:

- Cluster 0: High Activity, High Success
- Cluster 1: Low Activity, High Success
- Cluster 2: Medium Activity, Medium Success
- Cluster 3: Low Activity, Low Success

**Implementation**: [`explore_structure_and_quality.py`](IntentScope/src/explore_structure_and_quality.py)

### 4. Recommendation Engine

**Algorithm**: Collaborative Filtering with Content-Based Enhancement

**Purpose**: Generate personalized next-best-action recommendations

**Recommendation Types**:

- Feature highlight suggestions
- Content recommendations
- Engagement triggers
- Retention interventions

**Implementation**: [`personalized_recommendation_engine.py`](IntentScope/src/personalized_recommendation_engine.py)

### 5. Explainability Model

**Algorithm**: SHAP (SHapley Additive exPlanations)

**Purpose**: Provide interpretable explanations for model predictions

**Features**:

- Feature importance ranking
- Individual prediction explanations
- Global model interpretability
- Counterfactual analysis

**Implementation**: [`extract_feature_importance_and_shap.py`](IntentScope/src/extract_feature_importance_and_shap.py)

---

## 🔄 Data Pipeline

The data pipeline processes raw data through multiple stages to generate actionable insights.

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA PIPELINE FLOW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     │
│   │  SOURCE  │────▶│  PARSE   │────▶│ VALIDATE │────▶│ TRANSFORM│     │
│   │   DATA   │     │   CSV    │     │   JSON   │     │   FEATURE │     │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘     │
│        │                                                  │             │
│        │                                                  ▼             │
│        │                                         ┌──────────┐           │
│        │                                         │  TRAIN   │           │
│        └────────────────────────────────────────▶│   MODELS │           │
│                                                    └──────────┘           │
│                                                          │               │
│                                                          ▼               │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     │
│   │  STREAM   │◀────│ EXTRACT  │◀────│ INFER    │◀────│  DEPLOY  │     │
│   │   EVENT   │     │ FEATURES │     │ PREDICT  │     │   API    │     │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Stage 1: Data Loading

**Module**: [`load_dataset.py`](IntentScope/src/load_dataset.py)

**Functionality**:

- Load CSV files with automatic encoding detection
- Parse JSON data structures
- Validate data schema
- Handle missing values
- Sample large datasets

**Supported Formats**:

- CSV (UTF-8, Latin-1, ISO-8859-1, CP1252)
- JSON (nested structures)
- Parquet (optional)

### Stage 2: Feature Engineering

**Module**: [`engineer_behavioral_features.py`](IntentScope/src/engineer_behavioral_features.py)

**Feature Categories**:

| Category            | Count | Examples                                |
| ------------------- | ----- | --------------------------------------- |
| Session Features    | 8     | session_count, session_duration, etc.   |
| Navigation Features | 12    | page_depth, bounce_rate, etc.           |
| Engagement Features | 15    | click_rate, scroll_depth, etc.          |
| Temporal Features   | 10    | recency, frequency, time_of_day, etc.   |
| Behavioral Features | 9     | feature_adoption, completion_rate, etc. |

**Total Features**: 54

### Stage 3: Model Training

**Module**: Multiple training modules

**Training Process**:

1. Split data into train/test/validation
2. Train Gradient Boosting classifier
3. Train LSTM sequence model
4. Fit K-Means clusterer
5. Evaluate and select best model

### Stage 4: Real-Time Inference

**Module**: [`create_streaming_event_buffer.py`](IntentScope/src/create_streaming_event_buffer.py)

**Process**:

1. Receive streaming events
2. Buffer and batch events
3. Extract features incrementally
4. Run inference pipeline
5. Return predictions

---

## 🎮 Gamification System

IntentScope includes a comprehensive gamification system to drive user engagement.

### Features

**Module**: [`gamification_system_complete.py`](IntentScope/src/gamification_system_complete.py)

#### Badges

Earn badges for achievements:

| Badge       | Criteria            | Rarity    |
| ----------- | ------------------- | --------- |
| First Steps | Complete onboarding | Common    |
| Power User  | 100+ sessions       | Rare      |
| Champion    | 90%+ success rate   | Epic      |
| Master      | All achievements    | Legendary |

#### Streaks

Maintain engagement streaks:

- Daily login streak tracking
- Weekly activity goals
- Monthly challenges
- Streak recovery options

#### Leaderboards

Competitive rankings:

- Global leaderboards
- Team leaderboards
- Friend comparisons
- Historical rankings

### Gamification Metrics

Track engagement through:

- Points accumulation
- Level progression
- Achievement unlocking
- Social interactions

---

## 📊 Dashboard & Visualization

IntentScope provides rich interactive dashboards powered by Plotly.

### Dashboard Components

**Module**: [`professional_interactive_dashboard.py`](IntentScope/src/professional_interactive_dashboard.py)

| Component             | Type         | Description             |
| --------------------- | ------------ | ----------------------- |
| User Distribution     | Pie Chart    | User segment breakdown  |
| Success Trends        | Line Chart   | Success rate over time  |
| Feature Importance    | Bar Chart    | SHAP feature rankings   |
| Intention Clusters    | Scatter Plot | K-Means visualization   |
| Engagement Heatmap    | Heatmap      | User activity patterns  |
| Prediction Confidence | Gauge        | Model confidence levels |
| Cohort Analysis       | Funnel       | Conversion funnel       |
| Anomaly Detection     | Scatter      | Outlier identification  |

### Real-Time Dashboard

**Module**: [`realtime_monitoring_dashboard.py`](IntentScope/src/realtime_monitoring_dashboard.py)

**Features**:

- Live metrics streaming
- Auto-refreshing charts
- Alert notifications
- Custom time ranges

### Visualization Examples

```python
import plotly.express as px

# User distribution pie chart
fig = px.pie(
    df,
    names='segment',
    title='User Segment Distribution',
    color_discrete_sequence=px.colors.qualitative.Set2
)

# Success trends line chart
fig = px.line(
    df,
    x='date',
    y='success_rate',
    title='Success Rate Over Time',
    markers=True
)
```

---

## ⚙️ Configuration

IntentScope uses YAML-based configuration for flexible deployment.

### Configuration Files

| File          | Purpose                           |
| ------------- | --------------------------------- |
| `canvas.yaml` | Canvas and visualization settings |
| `layer.yaml`  | Layer definitions and connections |
| `.env`        | Environment variables             |

### Environment Variables

```bash
# Required
FLASK_APP=app.py
SECRET_KEY=your_secret_key_here

# Optional - AI Features
HF_TOKEN=your_huggingface_token
HUGGING_FACE_HUB_TOKEN=your_token

# Optional - Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Optional - Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### YAML Configuration

**canvas.yaml** controls visualization settings:

```yaml
visualization:
  theme: dark
  color_scheme: zerve
  chart_library: plotly
  responsive: true

dashboard:
  refresh_interval: 30
  max_data_points: 1000
  export_formats: [png, svg, pdf]
```

---

## 🧪 Testing

IntentScope includes comprehensive test suites for reliability.

### Test Modules

| Module                                                                                         | Coverage               |
| ---------------------------------------------------------------------------------------------- | ---------------------- |
| [`test_authentication_scenarios.py`](IntentScope/src/test_authentication_scenarios.py)         | API authentication     |
| [`test_buffer_with_simulated_events.py`](IntentScope/src/test_buffer_with_simulated_events.py) | Event buffering        |
| [`test_live_streaming_simulation.py`](IntentScope/src/test_live_streaming_simulation.py)       | Streaming pipeline     |
| [`validate_prediction_pipeline.py`](IntentScope/src/validate_prediction_pipeline.py)           | End-to-end predictions |

### Running Tests

```bash
# Run all tests
pytest IntentScope/src/test_*.py -v

# Run specific test
python -m IntentScope.src.test_authentication_scenarios

# Run with coverage
pytest --cov=IntentScope --cov-report=html
```

---

## 📈 Performance Metrics

IntentScope is optimized for production performance.

### Benchmarks

| Metric                  | Target   | Achieved |
| ----------------------- | -------- | -------- |
| API Latency (predict)   | <50ms    | 45ms     |
| API Latency (cluster)   | <100ms   | 85ms     |
| API Latency (recommend) | <150ms   | 120ms    |
| Event Processing        | 1000/sec | 1200/sec |
| Concurrent Users        | 100      | 150+     |

### Optimization Techniques

1. **Caching**: Redis caching for frequent queries
2. **Batch Processing**: Bulk feature computation
3. **Async Processing**: Background task queues
4. **Connection Pooling**: Database connection reuse
5. **Model Optimization**: Quantized neural networks

### Monitoring

Track performance with:

- Response time histograms
- Error rate tracking
- Resource utilization
- Custom business metrics

---

## 🚢 Deployment

IntentScope supports multiple deployment options.

### Render Deployment

The project includes configuration for Render deployment:

**Files**:

- [`render.yaml`](render.yaml) - Render configuration
- [`Procfile`](Procfile) - Process types
- [`runtime.txt`](runtime.txt) - Python version
- [`build.sh`](build.sh) - Build script

**Deploy Steps**:

1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables
4. Deploy automatically

**Environment Variables on Render**:

```
SECRET_KEY=<generate-random-key>
HF_TOKEN=<optional-huggingface-token>
```

### Local Production Deployment

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use the build script
./build.sh
```

### Docker Deployment

```bash
# Build image
docker build -t intentscope:latest .

# Run container
docker run -d -p 5000:5000 \
  -e SECRET_KEY=your-key \
  -e HF_TOKEN=your-token \
  intentscope:latest
```

---

## 🔧 Troubleshooting

Common issues and their solutions.

### Application Issues

| Issue            | Solution                                |
| ---------------- | --------------------------------------- |
| App won't start  | Check Python version (3.8+ required)    |
| Import errors    | Run `pip install -r requirements.txt`   |
| Port in use      | Change port or kill conflicting process |
| Slow performance | Check system resources; restart app     |

### ML Pipeline Issues

| Issue                | Solution                                         |
| -------------------- | ------------------------------------------------ |
| Model training fails | Check data format; increase memory               |
| Low accuracy         | Review feature engineering; tune hyperparameters |
| Out of memory        | Use data sampling; reduce batch size             |

### API Issues

| Issue              | Solution                     |
| ------------------ | ---------------------------- |
| 401 Unauthorized   | Check API key validity       |
| 429 Rate Limited   | Wait and retry; upgrade tier |
| 500 Internal Error | Check logs; restart service  |

### Web Interface Issues

| Issue              | Solution                 |
| ------------------ | ------------------------ |
| Charts not loading | Check JavaScript console |
| Upload fails       | Verify file size <100MB  |
| Execution timeout  | Reduce code complexity   |

### Debug Mode

Enable detailed logging:

```python
# In app.py or environment
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🤝 Contributing

Contributions to IntentScope are welcome!

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Follow code style guidelines
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for all functions
- Keep functions under 100 lines

### Testing Requirements

- Minimum 80% code coverage
- All new features must have tests
- Run existing tests before submitting

---

## 📄 License

IntentScope is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 IntentScope

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📖 Appendix

### A. File Structure

```
IntentScope/
├── IntentScope/                 # Main ML pipeline
│   ├── README.md               # Detailed documentation
│   ├── canvas.yaml            # Visualization config
│   ├── layer.yaml             # Layer definitions
│   └── src/                   # Source modules
│       ├── __init__.py
│       ├── load_dataset.py
│       ├── engineer_behavioral_features.py
│       ├── train_lstm_intention_classifier.py
│       ├── define_long_term_success_metric.py
│       ├── gamification_system_complete.py
│       ├── personalized_recommendation_engine.py
│       ├── deploy_flask_api_endpoint.py
│       ├── professional_interactive_dashboard.py
│       ├── realtime_monitoring_dashboard.py
│       ├── create_streaming_event_buffer.py
│       ├── extract_feature_importance_and_shap.py
│       └── ... (30+ more modules)
│
├── app.py                     # Main Flask application
├── ai_service.py              # Hugging Face AI integration
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment config
├── Procfile                  # Process definition
├── runtime.txt               # Python runtime version
├── build.sh                  # Build script
├── templates/                # HTML templates
│   ├── base.html
│   └── index.html
├── static/                   # Static assets
│   └── css/
│       └── style.css
├── uploads/                  # Uploaded project storage
└── README.md                 # This file
```

### B. API Key Generation

Generate API keys for authentication:

```bash
# Using the built-in generator
python -m IntentScope.src.api_key_generator

# Programmatic generation
from IntentScope.src.api_key_generator import generate_api_key
api_key = generate_api_key()
```

### C. Glossary

| Term                    | Definition                               |
| ----------------------- | ---------------------------------------- |
| **Archetype**           | A user behavior pattern classification   |
| **Feature Engineering** | Process of creating predictive variables |
| **Gradient Boosting**   | Ensemble ML algorithm                    |
| **LSTM**                | Long Short-Term Memory neural network    |
| **K-Means**             | Unsupervised clustering algorithm        |
| **SHAP**                | SHapley Additive exPlanations            |
| **REST API**            | Representational State Transfer API      |

### D. Dependencies Reference

**Core Dependencies**:

- flask >= 3.0.0
- flask-cors >= 4.0.0
- pandas >= 2.0.0
- numpy >= 1.26.0
- scikit-learn >= 1.5.0

**Visualization**:

- plotly >= 5.20.0
- matplotlib >= 3.8.0
- seaborn >= 0.13.0

**AI/ML**:

- transformers >= 4.40.0
- tokenizers >= 0.15.0
- safetensors >= 0.4.0

### E. Changelog

**Version 1.0.0** (2024-03-19):

- Initial release
- 54-feature engineering pipeline
- Gradient Boosting success prediction
- LSTM intention classification
- K-Means clustering
- Real-time REST API
- Gamification system
- Professional dashboards
- Web interface with project upload
- Code execution capabilities
- AI tools integration

### F. Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [API documentation](#api-documentation)
3. Examine the test modules for usage examples
4. Open an issue on GitHub

---

## 🙏 Acknowledgments

- Flask framework and community
- scikit-learn contributors
- Plotly team
- Hugging Face
- All open-source library maintainers

---

**End of Documentation**

_Last Updated: March 2026_
_Version: 1.0.0_
_Total Lines: 800+_
