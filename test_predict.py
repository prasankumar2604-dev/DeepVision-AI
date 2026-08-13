from predict import predict_image, model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
import numpy as np

img_path = r"C:\Users\prasannakumar h a\deepfake-detector\dataset\test\fake\00JEP4Z36Z.jpg"

img = image.load_img(img_path, target_size=(224, 224))
img = image.img_to_array(img)
img = np.expand_dims(img, axis=0)
img = preprocess_input(img)

raw = model.predict(img, verbose=0)[0][0]

print("Raw output:", raw)
print(predict_image(img_path))