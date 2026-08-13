"""
==========================================
DeepVision AI
Deepfake Face Detection using MobileNetV2

Author : Prasan Kumar
Backend: Flask
Framework: TensorFlow / Keras
==========================================
"""

import os

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, "dataset")

TRAIN_DIR = os.path.join(DATASET_DIR, "train")
VALID_DIR = os.path.join(DATASET_DIR, "valid")
TEST_DIR = os.path.join(DATASET_DIR, "test")

MODEL_DIR = os.path.join(BASE_DIR, "model")

PLOT_DIR = os.path.join(MODEL_DIR, "plots")

UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

# ==========================================================
# Model Configuration
# ==========================================================

IMAGE_SIZE = (224, 224)

BATCH_SIZE = 32

INITIAL_EPOCHS = 15

FINE_TUNE_EPOCHS = 10

LEARNING_RATE = 0.0001

FINE_TUNE_LEARNING_RATE = 0.00001

MODEL_NAME = "deepvision_mobilenetv2_stage2_best.keras"

MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

# ==========================================================
# Class Names
# ==========================================================

CLASS_NAMES = [
    "Fake",
    "Real"
]

# ==========================================================
# Create Required Folders Automatically
# ==========================================================

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)