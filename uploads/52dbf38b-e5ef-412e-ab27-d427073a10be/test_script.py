# Simple test script for the upload functionality
print("Hello from IntentScope!")
print("This is a test of the code execution feature.")
print("Current time:", __import__('datetime').datetime.now())

# Simple calculation
result = sum(range(1, 101))
print(f"Sum of 1-100 = {result}")

# Test imports that should work
import os
import sys
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
