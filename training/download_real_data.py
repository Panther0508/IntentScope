"""
Download Real-World Behavioural & Deception Datasets
====================================================
This script attempts to download openly available multimodal datasets for
deception detection, facial expression, and gaze patterns.

Datasets targeted:
  1. MPIIGaze (CC BY-NC-SA 4.0) - Gaze estimation in the wild
     Download: https://darus.uni-stuttgart.de/api/access/datafile/
     Total: ~2.1 GB, 213K images from 15 subjects

  2. DOLOS (ICCV 2023) - Audio-Visual Deception Detection
     GitHub: https://github.com/nms05/audio-visual-deception-detection-dolos-dataset-and-parameter-efficient-crossmodal-learning
     Videos from YouTube, provides timestamps CSV for download

  3. AffectNet+ (research-only) - Facial expression with soft labels
     Requires manual license agreement: http://mohammadmahoor.com/databases-codes/
     ~1M images, 440K manually annotated

  4. Bag-of-Lies (IEEE CVPR 2019) - Multimodal deception (video, audio, gaze, EEG)
     Requires email license request to databases@iab-rubric.org
     325 recordings, 6.14 GB

NOTE: Some datasets require registration and manual download due to license restrictions.
The script will SKIP those automatically and create a README with manual instructions.

Usage:
  python download_real_data.py

Output directory: training/real_data/
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────
REAL_DATA_DIR = 'training/real_data'
DOWNLOAD_LOG = os.path.join(REAL_DATA_DIR, 'download_log.json')
USER_AGENT = 'IntentScope/1.0 (by Panther0508; research@intentscope.ai)'

# Ensure output directory exists
os.makedirs(REAL_DATA_DIR, exist_ok=True)

# ── Helper Functions ─────────────────────────────────────────────────────────
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def md5_hash(filepath):
    """Calculate MD5 of a file (for integrity verification)."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def save_log(entries):
    with open(DOWNLOAD_LOG, 'w') as f:
        json.dump(entries, f, indent=2)

def load_log():
    if os.path.exists(DOWNLOAD_LOG):
        with open(DOWNLOAD_LOG) as f:
            return json.load(f)
    return {}

# ── Dataset 1: MPIIGaze (Gaze Patterns) ─────────────────────────────────────
def download_mpiigaze():
    """
    MPIIGaze: Appearance-Based Gaze Estimation in the Wild
    License: CC BY-NC-SA 4.0
    Size: 2.1 GB
    Papers: Zhang et al. TPAMI 2019
    """
    log("=" * 70)
    log("DOWNLOADING MPIIGaze")
    log("=" * 70)

    dataset_dir = os.path.join(REAL_DATA_DIR, 'MPIIGaze')
    os.makedirs(dataset_dir, exist_ok=True)

    # MPIIGaze is available via DaRUS (University of Stuttgart)
    # The base URL pattern for individual files:
    # https://darus.uni-stuttgart.de/api/access/datafile/

    # Due to the size and number of files, we provide a manifest and let
    # the user optionally download via wget/curl. For automation, we'll
    # attempt a direct download of a smaller annotation subset first.
    annotation_url = 'https://darus.uni-stuttgart.de/api/access/datafile/32280'
    annotation_path = os.path.join(dataset_dir, 'Annotation_Subset.zip')

    log(f"Target: {annotation_url}")
    log(f"Destination: {annotation_path}")

    try:
        import urllib.request
        log("Downloading annotation subset (~200 MB)...")
        req = urllib.request.Request(
            annotation_url,
            headers={'User-Agent': USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=300) as response, \
             open(annotation_path, 'wb') as out_file:
            chunk_size = 8192
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)

        log(f"✓ Download complete: {os.path.getsize(annotation_path) / 1024**2:.1f} MB")
        log(f"  MD5: {md5_hash(annotation_path)}")
        log("NOTE: Full dataset requires selecting individual files due to size limits.")
        log("  Visit: https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi%3A10.18419%2FDARUS-3230")
        return True

    except Exception as e:
        log(f"[WARN] MPIIGaze download failed: {e}")
        log("  You may need to download manually from the DaRUS portal.")
        return False

# ── Dataset 2: DOLOS (Audio-Visual Deception) ────────────────────────────────
def download_dolos():
    """
    DOLOS Dataset for Audio-Visual Deception Detection (ICCV 2023)
    GitHub: https://github.com/nms05/audio-visual-deception-detection-dolos-dataset-and-parameter-efficient-crossmodal-learning
    License: Academic research only
    """
    log("=" * 70)
    log("DOWNLOADING DOLOS Deception Dataset")
    log("=" * 70)

    dataset_dir = os.path.join(REAL_DATA_DIR, 'DOLOS')
    os.makedirs(dataset_dir, exist_ok=True)

    # Attempt to clone the GitHub repo to get the dataset download script and CSV files
    git_url = 'https://github.com/nms05/audio-visual-deception-detection-dolos-dataset-and-parameter-efficient-crossmodal-learning.git'
    clone_dir = os.path.join(dataset_dir, 'repo')

    log(f"Cloning GitHub repo: {git_url}")

    try:
        import subprocess
        subprocess.run(
            ['git', 'clone', git_url, clone_dir],
            check=True, capture_output=True, text=True
        )
        log(f"✓ Repository cloned to {clone_dir}")

        # Copy the timestamp file and download script to dataset directory
        import shutil
        ts_src = os.path.join(clone_dir, 'dolos_timestamps.txt')
        if os.path.exists(ts_src):
            shutil.copy(ts_src, dataset_dir)
            log(f"✓ Copied dolos_timestamps.txt to {dataset_dir}")
        else:
            log("[WARN] timestamps file not found in repo")

        log("NOTE: Videos must be downloaded separately using YT_video_downloader.py")
        log("      from the cloned repo. This may take hours and depends on YouTube availability.")
        log("      Alternatively, request access to a mirror from NTU ROSE Lab.")

        return True

    except subprocess.CalledProcessError as e:
        log(f"[WARN] Git clone failed: {e.stderr}")
        log("  You may need to download the repo manually.")
        return False
    except Exception as e:
        log(f"[WARN] DOLOS setup error: {e}")
        return False

# ── Dataset 3: AffectNet (Facial Expressions) ─────────────────────────────────
def download_affectnet():
    """
    AffectNet / AffectNet+ - Large-scale facial expression dataset
    License: Research only, requires signed agreement
    URL: http://mohammadmahoor.com/databases-codes/
    Size: ~450 GB (manual download after approval)
    """
    log("=" * 70)
    log("AFFECTNET – MANUAL DOWNLOAD REQUIRED")
    log("=" * 70)

    dataset_dir = os.path.join(REAL_DATA_DIR, 'AffectNet')
    os.makedirs(dataset_dir, exist_ok=True)

    # Create a detailed instruction file
    instructions = f"""# AffectNet+ Dataset – Manual Download Instructions

## Overview
AffectNet is the largest facial expression dataset with ~1M images, ~440K manually
annotated with 7 emotion categories + valence/arousal. This is used to train facial
AU approximation modules in Phase 3.

## License & Access
1. Download the license agreement from: http://mohammadmahoor.com/databases-codes/
2. Fill in your institution's legal authority signer information
3. Email the signed agreement to the PI (contact on the website)
4. Upon approval, you will receive download credentials

## Citation
If you use AffectNet+, cite:
  - AffectNet: A Database for Facial Expression, Valence, and Arousal Computation in the Wild
    (Mohammad Mahoor & Jeffrey Soto, CVPR 2017)
  - AffectNet+: https://arxiv.org/abs/2410.22506

## After Download
Place the downloaded AffectNet folder (containing Manually_Annotated/) here:
  {dataset_dir}/

Expected structure:
  {dataset_dir}/
  ├── Manually_Annotated/
  │   ├── Manually_Annotated/  # CSV metadata
  │   └── train/
  │   └── val/
  └── download_instructions.txt (this file)

## Automation Status
This dataset CANNOT be downloaded automatically due to license agreement.
Please complete the manual steps above before running preprocessing.
"""

    instr_path = os.path.join(dataset_dir, 'DOWNLOAD_INSTRUCTIONS.md')
    with open(instr_path, 'w') as f:
        f.write(instructions)

    log(f"✓ Created instruction file: {instr_path}")
    log("  AffectNet requires MANUAL download after license approval.")
    log("  Preprocessing script will check for data before proceeding.")

    return False  # Not auto-downloaded

# ── Dataset 4: Bag-of-Lies (Multimodal Deception) ────────────────────────────
def download_bag_of_lies():
    """
    Bag-of-Lies: Multimodal Deception Dataset (CVPR 2019)
    Contains: video, audio, eye gaze, EEG (13 channels) from 35 subjects
    License: Research/educational only, requires signed agreement
    Size: 6.14 GB
    """
    log("=" * 70)
    log("BAG-OF-LIES – MANUAL LICENSE REQUIRED")
    log("=" * 70)

    dataset_dir = os.path.join(REAL_DATA_DIR, 'BagOfLies')
    os.makedirs(dataset_dir, exist_ok=True)

    instructions = f"""# Bag-of-Lies Dataset – Manual License Request

## Dataset Description
Bag-of-Lies is a multimodal deception dataset with:
  - 325 recordings (162 lies, 163 truths) from 35 unique subjects
  - Video (phone camera), Audio, Eye Gaze (GazePoint GP3), EEG (13-channel)
  - Used in: Gupta et al., CVPR 2019

## License Agreement
1. Download the license agreement PDF from: https://iab-rubric.org/old/index.php/bag-of-lies
2. Fill in your institution's legal signatory (head of department/registrar)
3. Email the signed agreement to: databases@iab-rubric.org
   Subject: "License agreement for Bag-of-Lies Database"
4. Wait for approval (they provide a password to extract the ZIP)

## Important Restrictions
- User_12 data must NOT be used in any publication
- Non-commercial research/education only
- Must cite the CVPR 2019 paper in any derived work

## Download
After approval, you'll receive a download link (~6.14 GB, password-protected ZIP).
Extract here: {dataset_dir}/

## Preprocessing
The preprocessing script will attempt to extract:
  - Video frames → facial landmarks (via OpenCV/MediaPipe)
  - Audio → MFCC, pitch, jitter, shimmer
  - Gaze CSV → normalized coordinates
  - Align to 50-timestep sequences

## Automation Status
Manual process only – no automated download available.
"""

    instr_path = os.path.join(dataset_dir, 'DOWNLOAD_INSTRUCTIONS.md')
    with open(instr_path, 'w') as f:
        f.write(instructions)

    log(f"✓ Created instructions: {instr_path}")
    log("  Bag-of-Lies requires manual license approval.")

    return False

# ── Main Orchestrator ─────────────────────────────────────────────────────────
def main():
    log("IntentScope Real Data Downloader")
    log("=" * 70)
    log(f"Output: {REAL_DATA_DIR}")
    log("")

    # Track results
    results = {
        'timestamp': datetime.now().isoformat(),
        'datasets': {}
    }

    # 1. Try MPIIGaze (most accessible)
    results['datasets']['MPIIGaze'] = download_mpiigaze()

    # 2. Try DOLOS (GitHub-based)
    results['datasets']['DOLOS'] = download_dolos()

    # 3. AffectNet (manual only)
    results['datasets']['AffectNet'] = download_affectnet()

    # 4. Bag-of-Lies (manual only)
    results['datasets']['BagOfLies'] = download_bag_of_lies()

    # Save log
    save_log(results)

    log("")
    log("=" * 70)
    log("DOWNLOAD SUMMARY")
    log("=" * 70)
    for name, success in results['datasets'].items():
        status = "✓ Success" if success else "✗ Manual/Unavailable"
        log(f"  {name:20s}: {status}")

    log("")
    log("Next steps:")
    log("  1. Manually download any datasets marked 'Manual'")
    log("  2. Run: python training/preprocess_real_data.py")
    log("  3. Then: python training/train_fusion_model.py")

if __name__ == "__main__":
    main()
