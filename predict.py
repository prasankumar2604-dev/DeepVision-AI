"""
====================================================
DeepVision AI
Prediction Module
====================================================
"""

import os
import sys
import gc

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Optimize memory management for free cloud tiers (Render 512MB RAM)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["MALLOC_TRIM_THRESHOLD_"] = "100000"

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from config import MODEL_PATH, IMAGE_SIZE

# Thread pool optimization for single-core / low-RAM cloud instances
try:
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.threading.set_intra_op_parallelism_threads(2)
except Exception:
    pass

# ---------------------------------------------------
# Load Model
# ---------------------------------------------------

print("Loading AI model...")

model = load_model(MODEL_PATH)

print("✅ AI Model Loaded Successfully")


# ---------------------------------------------------
# Prediction Function
# ---------------------------------------------------

def predict_image(image_path):

    print("\n==============================")
    print("Predicting image:", image_path)

    img = image.load_img(
        image_path,
        target_size=IMAGE_SIZE
    )

    print("Image loaded successfully")
    
    img_array = image.img_to_array(img)
    img_tensor = np.expand_dims(img_array, axis=0)
    img_preprocessed = preprocess_input(img_tensor)

    # Direct model inference: significantly faster and uses far less memory than model.predict()
    raw_output = model(img_preprocessed, training=False).numpy()
    prediction = float(raw_output[0][0])

    # Explicit memory cleanup to stay strictly under 512MB RAM
    del img, img_array, img_tensor, img_preprocessed, raw_output
    gc.collect()

    # Print raw output
    print("=" * 50)
    print("Raw prediction:", prediction)

    if prediction >= 0.5:
        print("Model thinks: REAL")
        label = "Real"
        confidence = prediction * 100
    else:
        print("Model thinks: FAKE")
        label = "Fake"
        confidence = (1 - prediction) * 100

    print("=" * 50)

    return {
        "label": label,
        "confidence": round(float(confidence), 2)
    }


# ---------------------------------------------------
# Test Prediction
# ---------------------------------------------------

if __name__ == "__main__":

    sample = input("Enter image path: ")

    result = predict_image(sample)

    print("\nPrediction Result")
    print("-----------------------")
    print("Label      :", result["label"])
    print("Confidence :", f"{result['confidence']}%")
