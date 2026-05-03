# Changelog

All notable changes to IntentScope will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] – Under Development (Phase 3 Complete)

**Current pre-release version**

### Added (Phase 1 – Foundation)
- React + Vite scaffold with routing (8 pages)
- Black & gold sci-fi theme with glassmorphism panels
- Starfield animated background (canvas particles)
- Loading screen with progress animation
- IndexedDB setup via Dexie
- ONNX placeholder for fusion model

### Added (Phase 2 – Sensor Pipeline)
- **Face Worker:** MediaPipe FaceLandmarker (GPU) → gaze + 6 Action Units
- **Voice Worker:** Meyda audio analysis → 13 MFCCs + pitch, loudness, jitter, shimmer
- **Keyboard Tracker:** Inter-key intervals, hold duration, variance, typing speed
- **SensorAggregator:** 50-timestep sliding window → 28-D feature vector
- **SensorContext:** Global React context managing all workers lifecycle
- **Dashboard:** Live sensor panels, start/stop controls, buffer fill indicator
- **Analysis:** Detailed sensor logs, AU breakdown view

### Added (Phase 3 – AI Fusion & Advanced Features)
- **Fusion Worker:** ONNX Runtime Web inference at 20 Hz
  - Bi-LSTM with attention (exported from PyTorch training)
  - 8 intent classes + 32-D embedding output
  - Simulation fallback when model unavailable
- **World Knowledge Engine:**
  - News fetching from Hacker News Algolia, Dev.to API, Reddit r/programming
  - IndexedDB caching (5-minute refresh)
  - Relevance matching based on current intent
- **AI Narrator (AINarrator page):**
  - WebLLM integration (Llama-3-8B-Instruct-q4)
  - Retrieval-augmented prompts (includes latest news)
  - Streaming responses, user Q&A
- **Deception Detection:**
  - Deception probability extracted from fusion output
  - Color-coded gauge in Dashboard, Analysis, DeceptionChallenge
  - Interactive lie-detection game with verdicts
- **Intent-Driven Robotics (RobotLab page):**
  - Robot arm visualization with mode toggle (Mind-Controlled vs Expression)
  - State machine maps intents to actions (Pick, Place, Scan, Suspend)
- **Training Pipeline (Python):**
  - `generate_dataset.py` – synthetic 5000-train + 500-val sequences
  - `train_fusion_model.py` – Bi-LSTM trainer + ONNX export + quantization
  - `preprocess_real_data.py` – MPIIGaze, DOLOS, AffectNet, Bag-of-Lies integration
  - `download_real_data.py` – automated dataset acquisition (manual license steps)

### Changed
- Updated Dashboard to display intent probability bars and deception gauge
- Integrated news ticker into Dashboard header
- DeceptionChallenge page now uses live fusion predictions for scoring
- RobotLab reacts to real-time intent changes with smooth animations

### Fixed
- Worker cleanup on sensor stop (video tracks, audio context, animation frames)
- ONNX model path resolution in Vite dev/prod
- AudioContext autoplay policy compliance (started via user gesture)
- NewsEngine error handling for individual source failures

### Known Issues
- ONNX model file is placeholder (22 bytes) until training pipeline is run
- No automated test suite yet (Phase 4 will add Vitest + Playwright)
- Settings page toggles are not fully wired to sensor state
- RobotLab 3D visualization not implemented (emoji placeholder)
- WebLLM model size ~4GB causes long initial load on slow connections

---

## [0.0.1] – Project Inception

**Date:** 2026-03-01

- Repository initialized
- Basic Vite + React setup
- Initial design system (colors, typography)
- Route scaffolding (Home, Dashboard, Analysis, Robot, Narrator, Deception, About, Settings)
- Placeholder components

---

*This changelog will be updated with each release. Older versions may be archived.*
