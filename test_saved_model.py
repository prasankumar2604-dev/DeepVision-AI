import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from config import TEST_DIR, IMAGE_SIZE, MODEL_PATH, BATCH_SIZE

print("=" * 60)
print("DEEPVISION AI - SAVED MODEL TEST")
print("=" * 60)

# -----------------------------
# Dataset
# -----------------------------

datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

test_generator = datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

print("\nClass mapping:")
print(test_generator.class_indices)

# -----------------------------
# Load model
# -----------------------------

model = load_model(MODEL_PATH)

print("\nModel loaded successfully.")

# -----------------------------
# Evaluate
# -----------------------------

loss, accuracy = model.evaluate(
    test_generator,
    verbose=1
)

print("\n" + "=" * 60)
print("TEST RESULT")
print("=" * 60)

print(f"Test Loss     : {loss:.4f}")
print(f"Test Accuracy : {accuracy * 100:.2f}%")

# -----------------------------
# Predictions
# -----------------------------

predictions = model.predict(
    test_generator,
    verbose=1
).flatten()

labels = test_generator.classes

predicted_classes = (predictions >= 0.5).astype(int)

# -----------------------------
# Confusion matrix manually
# -----------------------------

fake_actual = labels == 0
real_actual = labels == 1

fake_pred = predicted_classes == 0
real_pred = predicted_classes == 1

fake_correct = np.sum(fake_actual & fake_pred)
fake_wrong = np.sum(fake_actual & real_pred)

real_correct = np.sum(real_actual & real_pred)
real_wrong = np.sum(real_actual & fake_pred)

fake_total = np.sum(fake_actual)
real_total = np.sum(real_actual)

print("\n" + "=" * 60)
print("CLASS RESULTS")
print("=" * 60)

print(
    f"Fake accuracy : "
    f"{fake_correct}/{fake_total} "
    f"({fake_correct / fake_total * 100:.2f}%)"
)

print(
    f"Real accuracy : "
    f"{real_correct}/{real_total} "
    f"({real_correct / real_total * 100:.2f}%)"
)

print("\n" + "=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print(
    f"Actual FAKE → Predicted FAKE : {fake_correct}"
)

print(
    f"Actual FAKE → Predicted REAL : {fake_wrong}"
)

print(
    f"Actual REAL → Predicted FAKE : {real_wrong}"
)

print(
    f"Actual REAL → Predicted REAL : {real_correct}"
)

print("=" * 60)