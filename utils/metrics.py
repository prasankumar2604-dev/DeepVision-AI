"""
==========================================
Evaluation Metrics
DeepVision AI
==========================================
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)


def evaluate_model(model, test_generator, save_dir):
    """
    Evaluate trained model and save results.
    """

    os.makedirs(save_dir, exist_ok=True)

    predictions = model.predict(test_generator)

    predictions = (predictions > 0.5).astype(int)

    y_true = test_generator.classes

    cm = confusion_matrix(y_true, predictions)

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Fake", "Real"]
    )

    plt.figure(figsize=(6,6))
    disp.plot(cmap="Blues", colorbar=False)
    plt.savefig(os.path.join(save_dir, "confusion_matrix.png"))
    plt.close()

    report = classification_report(
        y_true,
        predictions,
        target_names=["Fake", "Real"]
    )

    with open(
        os.path.join(save_dir, "classification_report.txt"),
        "w"
    ) as f:
        f.write(report)

    print(report)

    print("✅ Evaluation completed.")