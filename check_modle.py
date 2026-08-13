import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from config import TRAIN_DIR, IMAGE_SIZE, MODEL_PATH

print("=" * 60)
print("DEEPVISION AI - MODEL DIAGNOSTIC")
print("=" * 60)

# Load dataset
datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

generator = datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=32,
    class_mode="binary",
    shuffle=False
)

print("\nClass mapping:")
print(generator.class_indices)

# Load model
model = load_model(MODEL_PATH)

print("\nModel loaded successfully.")

# Predict ALL training images
predictions = model.predict(
    generator,
    verbose=1
).flatten()

labels = generator.classes

# --------------------------------------------------
# Separate classes
# --------------------------------------------------

fake_mask = labels == 0
real_mask = labels == 1

fake_predictions = predictions[fake_mask]
real_predictions = predictions[real_mask]

# --------------------------------------------------
# Classification
# --------------------------------------------------

predicted_classes = (predictions >= 0.5).astype(int)

fake_correct = np.sum(
    predicted_classes[fake_mask] == 0
)

real_correct = np.sum(
    predicted_classes[real_mask] == 1
)

fake_total = np.sum(fake_mask)
real_total = np.sum(real_mask)

overall_correct = np.sum(
    predicted_classes == labels
)

overall_total = len(labels)

# --------------------------------------------------
# Results
# --------------------------------------------------

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\nFake images : {fake_total}")
print(f"Real images : {real_total}")

print("\nFake predictions:")
print(f"Average model output : {fake_predictions.mean():.4f}")
print(f"Minimum output       : {fake_predictions.min():.4f}")
print(f"Maximum output       : {fake_predictions.max():.4f}")

print("\nReal predictions:")
print(f"Average model output : {real_predictions.mean():.4f}")
print(f"Minimum output       : {real_predictions.min():.4f}")
print(f"Maximum output       : {real_predictions.max():.4f}")

print("\n" + "-" * 60)

print(
    f"Fake accuracy    : "
    f"{fake_correct / fake_total * 100:.2f}%"
)

print(
    f"Real accuracy    : "
    f"{real_correct / real_total * 100:.2f}%"
)

print(
    f"Overall accuracy : "
    f"{overall_correct / overall_total * 100:.2f}%"
)

print("-" * 60)

print("\nConfusion Matrix:")

print(
    f"Actual FAKE → Predicted FAKE : "
    f"{np.sum((labels == 0) & (predicted_classes == 0))}"
)

print(
    f"Actual FAKE → Predicted REAL : "
    f"{np.sum((labels == 0) & (predicted_classes == 1))}"
)

print(
    f"Actual REAL → Predicted FAKE : "
    f"{np.sum((labels == 1) & (predicted_classes == 0))}"
)

print(
    f"Actual REAL → Predicted REAL : "
    f"{np.sum((labels == 1) & (predicted_classes == 1))}"
)

print("=" * 60)