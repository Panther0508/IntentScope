#!/bin/bash
set -e

# Install system dependencies required for sentencepiece
apt-get update && apt-get install -y cmake libsentencepiece-dev

# Install PyTorch from official source
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements (excluding sentencepiece which we'll install separately)
pip install -r requirements.txt

# Install sentencepiece (now with system libraries available)
pip install sentencepiece
