"""
====================================================
DeepVision AI
Prediction Module
====================================================
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Optimize TensorFlow runtime flags for cloud/container deployment
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from config import MODEL_PATH, IMAGE_SIZE

# Thread pool optimization for constrained free-tier environments
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
    
    img = image.img_to_array(img)

    img = np.expand_dims(img, axis=0)

    img = preprocess_input(img)

    # Predict
    prediction = model.predict(img, verbose=0)[0][0]

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
