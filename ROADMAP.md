# Roadmap

This roadmap outlines IntentScope's evolution from prototype to production-ready platform. All dates are tentative and community-driven.

## Current Status: Phase 4 – Public Launch Preparation 🚀

**Target completion:** Q2 2026

We are currently completing Phase 4, which includes:
- Comprehensive bug hunting and stability fixes
- Unique differentiator features (Local API, Simulator, Diagnostics)
- Full documentation suite
- Testing framework (unit + e2e)
- Developer tools and playground

## Version 1.0.0 – First Stable Release

**Planned for:** Q3 2026

### Goals
- Polished, bug-free experience
- Trained fusion model with >85% validation accuracy
- Deployable on GitHub Pages with HTTPS
- Complete documentation and tutorials

### Features
- ✅ Multi-modal sensor fusion (face, voice, keyboard)
- ✅ Real-time intent prediction (8 classes)
- ✅ Deception detection with gauge
- ✅ AI Narrator (WebLLM)
- ✅ Intent-driven robotics (simulated arm)
- ✅ World knowledge (news integration)
- ✅ Sensor simulator & replay mode
- ✅ Local API gateway for developers
- ✅ Diagnostics overlay
- ✅ Interactive tutorial

## Version 2.0.0 – Multi-User & VR 🎯

**Planned for:** Q4 2026 – Q1 2027

### Goals
- Support multiple simultaneous users
- Immersive 3D visualization
- Real hardware robot integration

### Proposed Features
- **Multi-User Sessions:** Share a URL, see multiple participants' intent predictions in real-time
- **3D Mindscape:** Three.js rendered brain visualization showing fused intent as particles/shapes
- **VR Mode:** WebXR support for immersive analysis (Oculus, Vive)
- **Real Robot Arms:** WebSocket API to control physical robot arms (e.g., uArm, Dobot)
- **WebRTC Integration:** Peer-to-peer data sharing for collaborative research
- **Cloud Sync:** Optional encryption-keyed backup of session data to user's cloud storage

## Version 3.0.0 – Enterprise & Extensibility 🔌

**Planned for:** Q2 2027+

### Goals
- Enterprise deployment options
- Plugin architecture
- Advanced analytics and reporting

### Proposed Features
- **Plugin System:** SDK for third-party sensors (EEG, heart rate, eye-tracking glasses)
- **Dashboard Customization:** Drag-and-drop widgets, custom metrics
- **Data Export:** CSV/JSON/PDF reports, time-series analysis
- **Authentication:** Optional login to save preferences (no personal data stored)
- **Self-Hosted Gateway:** Docker image for intranet deployments (for research labs)
- **Advanced Analytics:** Longitudinal tracking, trend analysis, user profiling (opt-in)
- **API Expansions:** GraphQL endpoint, webhooks for intent events
- **Accessibility:** Screen reader support, keyboard-only navigation, WCAG 2.1 AA compliance

## Future Ideas (Community-Driven)

These ideas are open for discussion and contribution:

- **Mobile App:** React Native wrapper for iOS/Android (uses device camera/mic)
- **Chrome Extension:** Overlay on any webpage for intention-aware browsing
- ** wearables:** Integration with Apple Watch, Fitbit, Oura Ring for physiological signals
- **Dataset Collection:** Crowdsourced anonymized dataset to improve model (opt-in)
- **Real-Time Collaboration:** Multiple developers share a robot arm simultaneously
- **Custom Models:** UI to upload and switch between different ONNX models
- **Voice-Only Mode:** For visually impaired users
- **Gamification:** Achievements, daily challenges, leaderboards for deception detection accuracy
- **Research Partnerships:** Collaborate with universities for validation studies

## How to Influence the Roadmap

1. **Vote on Issues:** React with 👍 on GitHub Issues you'd like to see prioritized
2. **Donate:** Funding accelerates development (GitHub Sponsors coming soon)
3. **Contribute:** PRs are welcome—see [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Discuss:** Use GitHub Discussions to propose new features

## Track Progress

- **Milestones:** https://github.com/Panther0508/IntentScope/milestones
- **Project Board:** https://github.com/Panther0508/IntentScope/projects
- **Changelog:** See [CHANGELOG.md](CHANGELOG.md) for version history

---

*This roadmap is a living document. As the community grows, priorities will shift. We're committed to keeping IntentScope free, open-source, and privacy-first.*
