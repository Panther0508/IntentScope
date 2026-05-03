# IntentScope

**Real-time intention reading from face, voice, and keyboard — powered by local AI.**

<div align="center">

<img src="assets/logo.png" alt="IntentScope" width="200"/>

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://panther0508.github.io/IntentScope/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge)](https://github.com/Panther0508/IntentScope/actions)

</div>

## 🚀 Try It Live

**[→ Launch IntentScope ←](https://panther0508.github.io/IntentScope/)**

Allow camera and microphone permissions when prompted. Best experienced on desktop Chrome/Edge.

## 📹 Demo

[Watch the 90-second showcase](assets/demo.mp4) to see:
- Real-time gaze tracking & intention prediction
- AI narrator commenting on your mental state
- Deception detection in action
- Intent-driven robotic arm control

## ✨ Features

### 🎯 Multi-Modal Sensor Fusion
- **Face Tracking** – MediaPipe FaceLandmarker extracts 6 Action Units + gaze vector (x, y)
- **Voice Stress Analysis** – Meyda extracts 13 MFCCs, pitch, loudness, jitter, shimmer
- **Keyboard Dynamics** – Capture typing patterns (inter-key interval, hold duration, variance)
- **Sliding Window Buffer** – 50-timestep sequences → 28-D feature vectors

### 🧠 Local AI Inference
- **Bi-LSTM with Attention** – Trained on 5000+ synthetic sequences + real-world datasets
- **ONNX Runtime Web** – 20 Hz inference entirely in-browser; no server
- **Eight Intent Classes:** Exploring, BuyIntent, Hesitation, Deception, ActionConfirm, RobotPick, RobotPlace, RobotIdle
- **Deception Probability** – Continuous gauge (0–100%) with color-coded alerts

### 🌍 World Knowledge Integration
- **Live News Feed** – Fetches from Hacker News, Dev.to, Reddit; relevance-ranked by current intent
- **IndexedDB Cache** – Offline article access with 5-minute refresh
- **Retrieval-Augmented Narration** – AI narrator consults latest headlines when commenting

### 🤖 Intent-Driven Robotics
- **Robot Lab Page** – 3D robotic arm (Three.js) that physically reacts to your intentions
- **Mode Toggle:** Mind-Controlled (intent-based) vs Expression-Only (manual)
- **Actions:** Pick, Place, Scan, Suspend (when deception detected)

### 🎙️ AI Observer (WebLLM)
- **Llama-3-8B-Instruct-q4** – Runs locally via WebLLM (WebGPU); ~4GB download on first use
- **Context-Aware Narration** – Generates concise sci-fi observer commentary (max 2 sentences)
- **User Questions** – Ask "What am I thinking?" and get AI analysis based on sensor state

### 🔬 Advanced Developer Tools
- **Local API Gateway** – `curl http://localhost:3000/api/intent` returns live predictions during `npm run dev`
- **Sensor Simulator & Replay** – Pre-recorded scenarios for testing without camera/mic; record your own sessions
- **Diagnostics Overlay** – `Ctrl+Shift+D` reveals performance metrics, worker logs, event stream
- **Developer Playground** – Page dedicated to API experimentation and live debugging

### 🎲 Interactive Challenge
- **Deception Challenge Game** – Answer personal questions; watch the deception gauge in real-time
- **Scoring System** – Threshold-based verdicts ("Truthful", "Deceptive", "Uncertain")

### 🎨 Premium UX
- **Black & Gold Sci-Fi Theme** – High-contrast glassmorphism panels
- **Animated Starfield** – Canvas particles float across the background
- **Responsive Design** – Mobile-friendly navigation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Application (Vite)                 │
├─────────────────────────────────────────────────────────────┤
│  Pages: Home, Dashboard, Analysis, RobotLab, Narrator,     │
│         DeceptionChallenge, Tutorial, API Playground       │
├─────────────────────────────────────────────────────────────┤
│  SensorContext – Global State (React Context)              │
│  ├─ Face Worker (MediaPipe) → Gaze + 6 AUs                 │
│  ├─ Voice Worker (Meyda) → MFCCs + Stress Features        │
│  ├─ Keyboard Tracker → Dynamics                           │
│  └─ SensorAggregator → 50×28 buffer                       │
├─────────────────────────────────────────────────────────────┤
│  Fusion Worker (ONNX Runtime Web)                          │
│  └─ Bi-LSTM Model → Intent probs + 32-D embedding         │
├─────────────────────────────────────────────────────────────┤
│  Services: NewsEngine (HN+Dev.to+Reddit)                   │
│            IndexedDB (Dexie) Cache                         │
├─────────────────────────────────────────────────────────────┤
│  External APIs (dev only): WebLLM (Llama-3)                │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 18 + React Router 6 | SPA routing, component lifecycle |
| Build | Vite 6 | Fast dev server, production bundling |
| Styling | Plain CSS (variables) | Black/gold theme, glassmorphism |
| Workers | Web Workers (3) | Off-main-thread sensor & fusion |
| Face | MediaPipe Tasks Vision 0.10 | GPU-accelerated face landmarks |
| Audio | Meyda 4.3 | Real-time audio feature extraction |
| Inference | ONNX Runtime Web 1.20 | Cross-platform model execution |
| LLM | WebLLM 0.2.55 (Llama-3-8B-Instruct-q4f16_1) | Local generative AI |
| Database | Dexie 4.0 (IndexedDB) | News cache, scenario storage |
| 3D | Three.js 0.169 (future) | Robotic arm visualization |

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Panther0508/IntentScope.git
cd IntentScope

# Install frontend dependencies
npm install

# (Optional) Set up Python environment for model training
cd training
python -m venv venv
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt

# Run the app
npm run dev
# → http://localhost:3000
```

## 🧪 Training the Fusion Model

The ONNX model (`public/fusion_model.onnx`) must be generated from the training pipeline. If absent, the app runs in **simulation mode** with mock predictions.

```bash
cd training

# Generate synthetic training data (5000 sequences)
python generate_dataset.py

# Train Bi-LSTM with attention and export to ONNX
python train_fusion_model.py

# The trained model is copied to public/fusion_model.onnx
# Restart the dev server to load it
```

**Note:** Real-data integration scripts are included (`download_real_data.py`, `preprocess_real_data.py`) for MPIIGaze, DOLOS, AffectNet, and Bag-of-Lies datasets (requires manual download due to licenses).

## 🧩 Development

### Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server at http://localhost:3000 |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview built app locally |
| `npm run lint` | ESLint with zero warnings policy |

### Project Structure

```
IntentScope/
├── public/                    # Static assets (ONNX model, scenarios)
│   └── scenarios/             # Pre-recorded sensor sequences (JSON)
├── src/
│   ├── components/            # Reusable UI (Layout, LoadingScreen, NewsTicker)
│   ├── context/               # SensorContext (global state)
│   ├── hooks/                 # Custom hooks (useStarfield)
│   ├── pages/                 # Route pages (9 total)
│   ├── services/              # newsEngine.js
│   ├── utils/                 # sensorAggregator, keyboardTracker
│   └── workers/               # faceWorker, voiceWorker, fusionWorker
├── training/                  # Python training pipeline
│   ├── generate_dataset.py    # Synthetic data generator
│   ├── train_fusion_model.py  # PyTorch trainer + ONNX export
│   ├── download_real_data.py  # Dataset acquisition (manual steps)
│   └── preprocess_real_data.py# Real data preprocessing
├── e2e/                       # Playwright end-to-end tests
├── __tests__/                 # Vitest unit tests
└── docs/                      # Architecture docs (optional)
```

### Adding a New Sensor Modality

1. Create a new Web Worker in `src/workers/` (e.g., `poseWorker.js`)
2. Export `{ init, postMessage }` interface; send `{ type: 'result', ... }` messages
3. Register the worker in `SensorContext.jsx` (add state, refs, start/stop logic)
4. Extend `sensorAggregator.js` to accept the new modality's features
5. Update training pipeline to include the new features in the 28-D vector

### Improving the Fusion Model

1. Collect more data (real or synthetic) in `training/data/`
2. Adjust hyperparameters (layers, hidden size, dropout) in `train_fusion_model.py`
3. Re-train and export ONNX (`python train_fusion_model.py`)
4. Replace `public/fusion_model.onnx` and reload the app

## 🧪 Testing

### Unit Tests (Vitest)

```bash
npm test
```

Test coverage targets:
- `sensorAggregator` – buffer logic, sliding window
- `keyboardTracker` – dynamics computation
- `newsEngine` – IndexedDB operations, relevance matching
- `fusionWorker` – ONNX loading, inference (mock)

### End-to-End Tests (Playwright)

```bash
npx playwright test
```

Critical paths covered:
- Dashboard loads and starts sensors (mocked)
- Intent prediction updates after buffer fills
- DeceptionChallenge question flow
- API Playground endpoint responses

## 📚 Documentation

- **[README.md](README.md)** – This file; project overview, quick start
- **[CONTRIBUTING.md](CONTRIBUTING.md)** – Developer setup, code standards, PR process
- **[ROADMAP.md](ROADMAP.md)** – Version roadmap, community suggestions
- **[CHANGELOG.md](CHANGELOG.md)** – Version-by-version changes
- **[training/README.md](training/README.md)** – ML pipeline deep-dive
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** – Data flow, worker architecture, model details

## 🔧 Developer Tools

### Local API Gateway (dev only)

During `npm run dev`, special endpoints are available:

```bash
curl http://localhost:3000/api/sensors    # Latest face, voice, keyboard data
curl http://localhost:3000/api/intent     # Intent probabilities + top prediction
curl http://localhost:3000/api/narration  # Latest AI narrator text
curl http://localhost:3000/api/robot      # Robot arm state
curl http://localhost:3000/api/status     # System health (workers, models)
```

Implementation: Vite plugin (`vite-plugin-local-api.js`) + WebSocket bridge from browser context.

### Diagnostics Overlay

Press `Ctrl+Shift+D` anywhere to reveal:
- FPS of each worker
- Fusion inference latency (ms)
- IndexedDB cache size
- Raw event stream log
- Toggle between "minimal" and "detailed" views

### Sensor Simulator

Visit `/playground` to:
- Load pre-recorded scenarios from `public/scenarios/` (e.g., `buy_intent.json`)
- Scrub through timeline, pause/resume
- Record your own live session as a downloadable JSON scenario
- Override live sensors with simulated data pipeline

## 🌐 Deployment

### GitHub Pages (automatic)

```bash
# Already configured via GitHub Actions
# Push to main → auto-deploy to https://panther0508.github.io/IntentScope/
```

### Manual Build

```bash
npm run build
npx serve dist
```

**Important:** Serve over HTTPS for camera/mic permissions (GitHub Pages provides this automatically).

## 📄 License

MIT – see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgements

- **Datasets:** MPIIGaze (gaze), DOLOS (deception), AffectNet (emotions), Bag-of-Lies (micro-expressions)
- **Libraries:** MediaPipe, Meyda, ONNX Runtime, WebLLM, Three.js, Dexie
- **Inspiration:** "Read the unspoken."

---

<div align="center">

**Built with ❤️ by [Panther0508](https://github.com/Panther0508)**

[Report Bug](https://github.com/Panther0508/IntentScope/issues) • [Request Feature](https://github.com/Panther0508/IntentScope/issues)

</div>
