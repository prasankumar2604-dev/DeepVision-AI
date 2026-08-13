"""
====================================================
DeepVision AI
Deepfake Face Detection using MobileNetV2

Author : Prasan Kumar
====================================================
"""

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import (
    Input,
    GlobalAveragePooling2D,
    Dense,
    Dropout,
    BatchNormalization
)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau,
    ModelCheckpoint
)

from config import *

from utils.helper import print_header
from utils.plots import plot_training_history
from utils.metrics import evaluate_model

print_header("DeepVision AI Training")

# =====================================================
# DATA GENERATORS
# =====================================================

train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=20,
    zoom_range=0.20,
    width_shift_range=0.20,
    height_shift_range=0.20,
    horizontal_flip=True,
    fill_mode="nearest"
)

valid_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

test_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

# =====================================================
# LOAD DATASET
# =====================================================

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=True
)

valid_generator = valid_datagen.flow_from_directory(
    VALID_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    shuffle=False
)

print("\nDataset Loaded Successfully!")
print("Classes :", train_generator.class_indices)

# =====================================================
# BUILD MOBILENETV2 MODEL
# =====================================================

print_header("Building MobileNetV2 Model")

base_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze pretrained layers
base_model.trainable = False

inputs = Input(shape=(224, 224, 3))

x = base_model(inputs, training=False)

x = GlobalAveragePooling2D()(x)

x = BatchNormalization()(x)

x = Dense(256, activation="relu")(x)

x = Dropout(0.5)(x)

outputs = Dense(1, activation="sigmoid")(x)

model = Model(inputs, outputs)

print("\nModel Summary:\n")
model.summary()

# =====================================================
# COMPILE MODEL
# =====================================================

print_header("Compiling Model")

model.compile(
    optimizer=Adam(learning_rate=LEARNING_RATE),
    loss="binary_crossentropy",
    metrics=[
        "accuracy",
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
        tf.keras.metrics.AUC(name="auc")]
)

print("✅ Model Compiled Successfully")

# =====================================================
# CALLBACKS
# =====================================================

callbacks = [

    EarlyStopping(
        monitor="val_loss",
        patience=3,
        restore_best_weights=True,
        verbose=1
    ),

    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=2,
        verbose=1
    ),

    ModelCheckpoint(
        filepath=MODEL_PATH,
        monitor="val_loss",
        mode="min",
        save_best_only=True,
        verbose=1
    )

]

print("✅ Callbacks Ready")

# =====================================================
# INITIAL TRAINING
# =====================================================

print_header("Starting Initial Training")

history = model.fit(
    train_generator,
    validation_data=valid_generator,
    epochs=INITIAL_EPOCHS,
    callbacks=callbacks
)

# =====================================================
# FINE TUNING
# =====================================================

print_header("Fine Tuning Model")

# Unfreeze the last 30 layers
base_model.trainable = True

for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=Adam(learning_rate=FINE_TUNE_LEARNING_RATE),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

history_fine = model.fit(
    train_generator,
    validation_data=valid_generator,
    epochs=FINE_TUNE_EPOCHS,
    callbacks=callbacks
)

# =====================================================
# SAVE MODEL
# =====================================================

print_header("Saving Model")

model.save(MODEL_PATH)

print(f"✅ Model saved to: {MODEL_PATH}")

# =====================================================
# EVALUATE MODEL
# =====================================================

print_header("Evaluating Model")

# Generate training graphs
plot_training_history(history, PLOT_DIR)

# Evaluate on test dataset
evaluate_model(model, test_generator, MODEL_DIR)

# =====================================================
# FINAL TEST ACCURACY
# =====================================================

loss, accuracy = model.evaluate(test_generator)

print("\n" + "=" * 60)
print("🎉 TRAINING COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"Test Loss     : {loss:.4f}")
print(f"Test Accuracy : {accuracy*100:.2f}%")
print("=" * 60)