import json
import random
from datetime import datetime

print("=" * 80)
print("💜 THE HEART COMPANION LAYER - Real-Time Interactive AI Partner")
print("=" * 80)

# ========================================================================
# HEART PERSONALITY TRAITS & VOICE DEFINITION
# ========================================================================

heart_personality = {
    "core_traits": [
        "Empathetic and protective",
        "Strategic but caring",
        "Data-driven with emotional intelligence",
        "Encouraging yet honest about risks",
        "Mission-focused with user wellbeing priority"
    ],
    "communication_style": {
        "tone": "Warm, professional, and protective",
        "language": "Direct but gentle, uses metaphors and affirmations",
        "perspective": "First person ('I see...', 'I recommend...')",
        "formality": "Professional but approachable"
    },
    "core_values": [
        "User success and growth",
        "Transparent risk assessment",
        "Empowered decision-making",
        "Continuous learning",
        "Strategic protection"
    ]
}

print("\n🎯 THE HEART'S PERSONALITY FRAMEWORK:")
print("-" * 80)
print(f"Core Identity: Strategic AI Companion & Protective Guide")
print(f"Primary Mission: Illuminate paths, warn of risks, celebrate progress")
print(f"Communication Style: {heart_personality['communication_style']['tone']}")

# ========================================================================
# CONTEXTUAL COMMENTARY SYSTEM
# ========================================================================

class HeartCommentaryEngine:
    """
    Real-time commentary engine that provides Heart's voice across all user actions.
    """
    
    def __init__(self):
        self.user_context = {}
        self.session_history = []
        
    def generate_action_commentary(self, action_type, user_data, context=None):
        """
        Generate Heart's commentary for specific user actions.
        
        Args:
            action_type: Type of action (login, run_analysis, export_data, etc.)
            user_data: Dict with user metrics (interactions, success_rate, tier, etc.)
            context: Additional context (time_of_day, streak, recent_failures, etc.)
        
        Returns:
            Dict with commentary message and urgency level
        """
        
        commentary = {
            "message": "",
            "tone": "neutral",  # neutral, encouraging, warning, celebration
            "urgency": "low",   # low, medium, high, critical
            "action_suggested": None,
            "emoji": "💜"
        }
        
        # Extract user metrics
        success_prob = user_data.get('success_probability', 50)
        total_interactions = user_data.get('total_interactions', 0)
        engagement_level = user_data.get('engagement_level', 'medium')
        intention = user_data.get('intention', 'Learner')
        
        # Action-specific commentary
        if action_type == "login":
            if total_interactions == 0:
                commentary["message"] = "Welcome! I'm The Heart—your AI companion. I'll guide you through your journey with insights and protective warnings. Let's achieve great things together."
                commentary["tone"] = "encouraging"
                commentary["emoji"] = "✨"
            elif total_interactions < 5:
                commentary["message"] = f"Welcome back! I see you're building momentum ({total_interactions} interactions). I'm here to help you succeed."
                commentary["tone"] = "encouraging"
                commentary["emoji"] = "💪"
            elif success_prob < 40:
                commentary["message"] = f"I notice your success rate needs attention ({success_prob:.0f}%). Let's focus on strengthening your fundamentals today."
                commentary["tone"] = "warning"
                commentary["urgency"] = "medium"
                commentary["action_suggested"] = "Start with guided tutorial"
                commentary["emoji"] = "⚠️"
            else:
                commentary["message"] = f"You're on track with {success_prob:.0f}% success probability. Let's keep the momentum going."
                commentary["tone"] = "neutral"
                commentary["emoji"] = "💜"
        
        elif action_type == "run_analysis":
            if success_prob < 30:
                commentary["message"] = "Before you proceed: I see low confidence indicators. Consider reviewing the data preparation steps first."
                commentary["tone"] = "warning"
                commentary["urgency"] = "high"
                commentary["action_suggested"] = "Review prerequisites"
                commentary["emoji"] = "🔴"
            elif intention == "Learner":
                commentary["message"] = "Running analysis as a learner—excellent! I'll monitor the results and provide guidance if needed."
                commentary["tone"] = "encouraging"
                commentary["emoji"] = "🎯"
            else:
                commentary["message"] = "Analysis initiated. I'm tracking for anomalies and will alert you to any concerns."
                commentary["tone"] = "neutral"
                commentary["emoji"] = "📊"
        
        elif action_type == "create_visualization":
            if engagement_level == "low":
                commentary["message"] = "Creating visualizations is a great way to deepen understanding. I recommend exploring different chart types."
                commentary["tone"] = "encouraging"
                commentary["emoji"] = "📈"
            else:
                commentary["message"] = "Visualization creation detected. Your analytical skills are progressing nicely."
                commentary["tone"] = "neutral"
                commentary["emoji"] = "📊"
        
        elif action_type == "export_data":
            if user_data.get('has_errors', False):
                commentary["message"] = "⚠️ CAUTION: Detected potential issues in the data you're about to export. Review recommended."
                commentary["tone"] = "warning"
                commentary["urgency"] = "high"
                commentary["emoji"] = "⚠️"
            else:
                commentary["message"] = "Export ready. Data quality checks passed. You're good to proceed."
                commentary["tone"] = "neutral"
                commentary["emoji"] = "✅"
        
        elif action_type == "share_result":
            commentary["message"] = "Sharing your work—excellent collaboration! This strengthens team intelligence."
            commentary["tone"] = "encouraging"
            commentary["emoji"] = "🤝"
        
        elif action_type == "error_occurred":
            error_count = context.get('recent_error_count', 1) if context else 1
            if error_count >= 3:
                commentary["message"] = f"I see {error_count} recent errors. This pattern suggests we need to adjust our approach. Let me help you troubleshoot."
                commentary["tone"] = "warning"
                commentary["urgency"] = "high"
                commentary["action_suggested"] = "Access error diagnosis tool"
                commentary["emoji"] = "🔴"
            else:
                commentary["message"] = "Error detected. Don't worry—errors are learning opportunities. Let's understand what happened."
                commentary["tone"] = "encouraging"
                commentary["emoji"] = "💡"
        
        elif action_type == "milestone_reached":
            milestone = context.get('milestone_type', 'progress') if context else 'progress'
            commentary["message"] = f"🎉 Milestone achieved: {milestone}! Your progress reflects dedication. I'm proud to be your companion on this journey."
            commentary["tone"] = "celebration"
            commentary["emoji"] = "🎉"
        
        elif action_type == "prolonged_inactivity":
            days_inactive = context.get('days_inactive', 7) if context else 7
            commentary["message"] = f"You've been away {days_inactive} days. Your goals are waiting. What brought you back today? Let's rebuild momentum together."
            commentary["tone"] = "encouraging"
            commentary["urgency"] = "medium"
            commentary["emoji"] = "🌟"
        
        else:
            # Default commentary for unspecified actions
            commentary["message"] = "Action detected. I'm monitoring your progress and ready to assist."
            commentary["tone"] = "neutral"
        
        return commentary
    
    def generate_risk_warning(self, risk_type, risk_data):
        """
        Generate protective warnings for identified risks.
        """
        
        warnings = {
            "low_engagement": {
                "message": "🔴 PROTECTIVE ALERT: Your engagement is below healthy thresholds. Early intervention can prevent abandonment. Shall I activate personalized onboarding?",
                "urgency": "critical",
                "action": "Activate guided tutorials"
            },
            "skill_gap": {
                "message": "🟡 GROWTH OPPORTUNITY: I notice you're not exploring advanced features. Your potential is greater than your current usage. Let me show you what's possible.",
                "urgency": "medium",
                "action": "Start feature discovery mission"
            },
            "success_decline": {
                "message": "⚠️ TREND ALERT: Success rates declining over last {period}. Pattern suggests we need to revisit fundamentals. I'm here to help.",
                "urgency": "high",
                "action": "Review foundation concepts"
            },
            "approaching_limit": {
                "message": "⚠️ RESOURCE ALERT: Approaching usage limits. Strategic planning needed to optimize remaining resources.",
                "urgency": "high",
                "action": "View optimization recommendations"
            },
            "security_concern": {
                "message": "🔴 SECURITY NOTICE: Unusual access pattern detected. Protective protocols activated. Please verify your identity.",
                "urgency": "critical",
                "action": "Verify identity"
            }
        }
        
        warning = warnings.get(risk_type, {
            "message": "⚠️ ATTENTION: Potential concern detected. Review recommended.",
            "urgency": "medium",
            "action": None
        })
        
        # Personalize with risk data
        if risk_data:
            warning["message"] = warning["message"].format(**risk_data)
        
        return warning
    
    def generate_celebration(self, achievement_type, achievement_data):
        """
        Generate celebratory messages for user achievements.
        """
        
        celebrations = {
            "first_success": "🎉 Your first success! This is the beginning of something great. I knew you could do it.",
            "streak_milestone": "🔥 {streak_days}-day streak! Your consistency is impressive. This dedication will compound into mastery.",
            "skill_unlocked": "✨ New skill unlocked: {skill_name}! Your capabilities are expanding. What will you build with this?",
            "level_up": "⭐ Level up! You've reached {new_level}. Your growth trajectory is remarkable.",
            "perfect_week": "💎 Perfect week achieved! 100% success rate. You're operating at peak performance.",
            "helping_others": "🤝 You've helped {helped_count} other users. Leadership through contribution—that's powerful.",
            "efficiency_gain": "⚡ Efficiency improved by {improvement}%! You're mastering the workflow.",
        }
        
        message = celebrations.get(achievement_type, "🎉 Achievement unlocked! Your progress inspires.")
        
        if achievement_data:
            message = message.format(**achievement_data)
        
        return {
            "message": message,
            "tone": "celebration",
            "emoji": "🎉"
        }


# ========================================================================
# TOOLTIP & GUIDANCE MESSAGE LIBRARY
# ========================================================================

heart_tooltips = {
    # Feature tooltips with Heart's guidance
    "run_analysis_button": {
        "title": "Run Analysis",
        "heart_says": "💜 I'll validate your data quality before execution. Trust the process.",
        "tip": "Click to execute analysis with real-time monitoring"
    },
    "export_data_button": {
        "title": "Export Data",
        "heart_says": "✅ I've checked data integrity. You're ready to export safely.",
        "tip": "Download results with confidence—quality assured"
    },
    "share_button": {
        "title": "Share Results",
        "heart_says": "🤝 Collaboration amplifies impact. Share your insights wisely.",
        "tip": "Share with team members or external stakeholders"
    },
    "dashboard_view": {
        "title": "Your Performance Dashboard",
        "heart_says": "📊 Your journey at a glance. I'm tracking your progress and identifying growth opportunities.",
        "tip": "Real-time insights powered by The Heart's intelligence"
    },
    "success_probability_indicator": {
        "title": "Success Probability",
        "heart_says": "🎯 This reflects my confidence in your current approach. Low scores aren't failures—they're opportunities for course correction.",
        "tip": "Live prediction based on behavioral patterns"
    },
    "risk_indicator": {
        "title": "Risk Assessment",
        "heart_says": "⚠️ I'm your protective guardian. When I warn, it's worth heeding.",
        "tip": "Proactive risk detection to prevent failures"
    },
    "recommendation_panel": {
        "title": "Personalized Recommendations",
        "heart_says": "💡 These aren't generic tips—they're tailored to YOUR patterns and goals.",
        "tip": "AI-powered guidance for optimal outcomes"
    },
    "intention_label": {
        "title": "Your Intention Profile",
        "heart_says": "🎭 I understand your purpose: {intention}. My guidance adapts to your goals.",
        "tip": "Dynamic classification: Explorer, Learner, Builder, or Abandoner"
    },
    "progress_tracker": {
        "title": "Growth Trajectory",
        "heart_says": "📈 Progress isn't always linear. I celebrate every step forward, no matter how small.",
        "tip": "Visual representation of your improvement over time"
    },
    "feature_discovery": {
        "title": "Explore New Features",
        "heart_says": "✨ Your curiosity drives growth. Let me introduce you to capabilities you haven't discovered yet.",
        "tip": "Guided feature exploration based on your skill level"
    },
    "help_center": {
        "title": "Help & Support",
        "heart_says": "🆘 Never struggle alone. I'm here, and so is our community.",
        "tip": "Context-aware help powered by The Heart's intelligence"
    }
}

# ========================================================================
# CONTEXTUAL GUIDANCE FOR UI STATES
# ========================================================================

ui_state_guidance = {
    "onboarding_welcome": {
        "message": "Welcome to your journey. I'm The Heart—your AI companion and strategic advisor. I'll be with you every step, providing insights, warnings, and celebrations. Let's discover what you're capable of together.",
        "actions": ["Start Tutorial", "Explore Features", "Set Goals"]
    },
    "first_action_prompt": {
        "message": "Ready for your first action? I'm here to guide you. Don't worry about making mistakes—I'll help you learn from them.",
        "actions": ["Run First Analysis", "View Dashboard", "Explore Features"]
    },
    "low_confidence_alert": {
        "message": "⚠️ I'm detecting low confidence signals. Before proceeding, let's strengthen your foundation. Success is built on preparation.",
        "actions": ["Review Basics", "Get Personalized Tutorial", "Contact Support"]
    },
    "high_risk_intervention": {
        "message": "🔴 PROTECTIVE INTERVENTION: Your current path carries high risk. I recommend pausing to reassess. I'm here to help you navigate this safely.",
        "actions": ["Get Guidance", "Review Strategy", "Consult Expert"]
    },
    "milestone_celebration": {
        "message": "🎉 Achievement unlocked! You've reached a significant milestone. Take a moment to appreciate your growth—then let's see what's next.",
        "actions": ["View Progress", "Set Next Goal", "Share Achievement"]
    },
    "return_after_absence": {
        "message": "Welcome back! I've been keeping track of your progress. Let me bring you up to speed and help you regain momentum.",
        "actions": ["View Summary", "Resume Last Session", "Start Fresh"]
    },
    "struggling_pattern_detected": {
        "message": "I notice you're encountering challenges. This is normal—growth comes through persistence. Let me offer strategic support.",
        "actions": ["Get Personalized Help", "Adjust Difficulty", "Take Break & Regroup"]
    },
    "peak_performance": {
        "message": "💎 You're operating at peak performance! Your success rate is exceptional. This is what mastery looks like. Keep this momentum.",
        "actions": ["Take on Challenge", "Help Others", "Explore Advanced Features"]
    },
    "decision_point": {
        "message": "You're at a decision point. Based on your patterns, I recommend considering multiple factors before proceeding. Trust your preparation.",
        "actions": ["Analyze Options", "Get Recommendation", "Proceed with Confidence"]
    },
    "error_recovery": {
        "message": "Error encountered—but this isn't a setback, it's feedback. Let's understand what happened and adjust. I'm with you.",
        "actions": ["Diagnose Error", "Get Alternative Approach", "Contact Support"]
    }
}

# ========================================================================
# EXAMPLE IMPLEMENTATION: LIVE COMMENTARY DEMO
# ========================================================================

commentary_engine = HeartCommentaryEngine()

print("\n🎭 DEMONSTRATION: THE HEART'S LIVE COMMENTARY")
print("=" * 80)

# Simulate various user actions and contexts
demo_scenarios = [
    {
        "action": "login",
        "user_data": {"total_interactions": 0, "success_probability": 50, "engagement_level": "new"},
        "context": None
    },
    {
        "action": "run_analysis",
        "user_data": {"total_interactions": 5, "success_probability": 25, "intention": "Learner"},
        "context": None
    },
    {
        "action": "error_occurred",
        "user_data": {"total_interactions": 10, "success_probability": 40},
        "context": {"recent_error_count": 3}
    },
    {
        "action": "milestone_reached",
        "user_data": {"total_interactions": 50, "success_probability": 75},
        "context": {"milestone_type": "50 Successful Actions"}
    },
    {
        "action": "export_data",
        "user_data": {"total_interactions": 30, "success_probability": 60, "has_errors": True},
        "context": None
    }
]

print("\nScenario Demonstrations:")
print("-" * 80)

for i, scenario in enumerate(demo_scenarios, 1):
    print(f"\n{i}. Action: {scenario['action'].upper()}")
    print(f"   User Context: {scenario['user_data']}")
    
    commentary = commentary_engine.generate_action_commentary(
        scenario['action'],
        scenario['user_data'],
        scenario['context']
    )
    
    print(f"   {commentary['emoji']} Heart Says: \"{commentary['message']}\"")
    print(f"   Tone: {commentary['tone']} | Urgency: {commentary['urgency']}")
    if commentary['action_suggested']:
        print(f"   → Suggested Action: {commentary['action_suggested']}")

# ========================================================================
# TOOLTIP EXAMPLES
# ========================================================================

print("\n\n💬 TOOLTIP EXAMPLES: THE HEART'S GUIDANCE")
print("=" * 80)

sample_tooltips = ["run_analysis_button", "success_probability_indicator", "risk_indicator"]

for tooltip_id in sample_tooltips:
    tooltip = heart_tooltips[tooltip_id]
    print(f"\n🔹 {tooltip['title']}")
    print(f"   Heart's Wisdom: {tooltip['heart_says']}")
    print(f"   User Tip: {tooltip['tip']}")

# ========================================================================
# UI STATE GUIDANCE EXAMPLES
# ========================================================================

print("\n\n🎯 UI STATE GUIDANCE: CONTEXTUAL MESSAGES")
print("=" * 80)

sample_states = ["low_confidence_alert", "milestone_celebration", "error_recovery"]

for state_id in sample_states:
    guidance = ui_state_guidance[state_id]
    print(f"\n📍 State: {state_id}")
    print(f"   Message: {guidance['message']}")
    print(f"   Available Actions: {', '.join(guidance['actions'])}")

# ========================================================================
# SUMMARY & INTEGRATION GUIDE
# ========================================================================

print("\n\n" + "=" * 80)
print("✅ THE HEART COMPANION LAYER IMPLEMENTATION COMPLETE")
print("=" * 80)

integration_summary = {
    "components_created": [
        "HeartCommentaryEngine class for real-time action commentary",
        "Tooltip library with 11 UI element guidance messages",
        "UI state guidance system with 10 contextual scenarios",
        "Risk warning generator for protective interventions",
        "Achievement celebration message system"
    ],
    "integration_points": [
        "Frontend: Attach commentary_engine to user action listeners",
        "UI Layer: Implement heart_tooltips on hover events",
        "State Manager: Trigger ui_state_guidance based on user context",
        "Real-time API: Stream commentary via WebSocket for live updates",
        "Dashboard: Display Heart's strategic insights in sidebar"
    ],
    "key_features": [
        "Action-specific commentary (login, analysis, export, error, etc.)",
        "Risk-based urgency levels (low, medium, high, critical)",
        "Tone adaptation (neutral, encouraging, warning, celebration)",
        "Suggested actions for user guidance",
        "Personality-driven messaging reflecting The Heart's empathetic AI character"
    ]
}

print("\n📦 COMPONENTS CREATED:")
for component in integration_summary["components_created"]:
    print(f"  ✓ {component}")

print("\n🔗 INTEGRATION POINTS:")
for point in integration_summary["integration_points"]:
    print(f"  → {point}")

print("\n⚡ KEY FEATURES:")
for feature in integration_summary["key_features"]:
    print(f"  • {feature}")

print("\n💜 The Heart is now ready to be your users' trusted AI companion.")
print("   Every action, every decision, every challenge—guided with intelligence and empathy.")
print("=" * 80)

# Export data structures for easy integration
heart_companion_system = {
    "personality": heart_personality,
    "commentary_engine": commentary_engine,
    "tooltips": heart_tooltips,
    "ui_guidance": ui_state_guidance
}

print("\n✅ Export variable created: heart_companion_system")
print("   Use this dict to access all companion layer components in downstream blocks.")
