import os
import random
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

MODEL_PATH = "model/mobilenetv2_deepfake.keras"

FAKE_DIR = "dataset/train/fake"
REAL_DIR = "dataset/train/real"

model = load_model(MODEL_PATH)


def predict_image(img_path):

    img = image.load_img(
        img_path,
        target_size=(224, 224)
    )

    img_array = image.img_to_array(img)

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    img_array = preprocess_input(img_array)

    prediction = model.predict(
        img_array,
        verbose=0
    )[0][0]

    if prediction >= 0.5:
        predicted = "REAL"
        confidence = prediction * 100
    else:
        predicted = "FAKE"
        confidence = (1 - prediction) * 100

    return predicted, confidence, prediction


def test_folder(folder, actual_class, count=10):

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]

    random.seed(42)
    selected = random.sample(files, min(count, len(files)))

    correct = 0

    print("\n" + "=" * 70)
    print(f"TESTING {actual_class.upper()} IMAGES")
    print("=" * 70)

    for filename in selected:

        path = os.path.join(folder, filename)

        predicted, confidence, raw = predict_image(path)

        result = "✅" if predicted.lower() == actual_class.lower() else "❌"

        if predicted.lower() == actual_class.lower():
            correct += 1

        print(
            f"{result} {filename:<25} "
            f"Actual={actual_class.upper():<5} "
            f"Predicted={predicted:<5} "
            f"Confidence={confidence:6.2f}% "
            f"Raw={raw:.4f}"
        )

    accuracy = (correct / len(selected)) * 100

    print("\nResult:")
    print(f"Correct: {correct}/{len(selected)}")
    print(f"Accuracy: {accuracy:.2f}%")

    return correct, len(selected)


# =====================================
# TEST
# =====================================

fake_correct, fake_total = test_folder(
    FAKE_DIR,
    "fake",
    10
)

real_correct, real_total = test_folder(
    REAL_DIR,
    "real",
    10
)

total_correct = fake_correct + real_correct
total_images = fake_total + real_total

print("\n" + "=" * 70)
print("FINAL RESULT")
print("=" * 70)

print(f"Fake accuracy : {fake_correct}/{fake_total}")
print(f"Real accuracy : {real_correct}/{real_total}")
print(f"Overall       : {total_correct}/{total_images}")
print(
    f"Overall accuracy: "
    f"{(total_correct / total_images) * 100:.2f}%"
)