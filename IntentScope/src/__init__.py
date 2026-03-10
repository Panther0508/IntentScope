"""
IntentScope - Behavioral Analytics Platform

A production-ready behavioral analytics platform combining offline machine learning 
training with real-time streaming inference.
"""

__version__ = "1.0.0"
__author__ = "IntentScope Team"

# Import data loading for convenience (this is the entry point)
def load_data():
    """Load the user behavior dataset."""
    from .load_dataset import user_behavior_df
    return user_behavior_df
