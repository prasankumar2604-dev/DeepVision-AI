# 🧠 DeepVision AI

### AI-Powered Deepfake Image Detection System

DeepVision AI is a web-based deepfake image detection system developed using
Deep Learning, TensorFlow, MobileNetV2, and Flask.

The system analyzes uploaded face images and predicts whether the image is
**REAL** or **FAKE**, along with a confidence score.

---

## 🚀 Features

- 🔍 AI-powered deepfake image detection
- 🧠 MobileNetV2 deep learning model
- ⚡ Real-time image prediction
- 📊 Prediction confidence score
- 👤 User registration and login
- 🔐 User authentication
- 🗃️ SQLite database
- 📜 Prediction history
- 🖥️ Responsive web interface
- 📁 Image upload support
- 📈 Model performance evaluation
- 🧪 Test dataset evaluation

---

## 🛠️ Technologies Used

### Backend

- Python
- Flask
- SQLite

### Deep Learning

- TensorFlow
- Keras
- MobileNetV2
- NumPy
- Pillow

### Frontend

- HTML5
- CSS3
- JavaScript

### Machine Learning / Evaluation

- Scikit-learn
- Pandas
- Matplotlib

---

## 🧠 AI Model

DeepVision AI uses **MobileNetV2**, a lightweight convolutional neural
network architecture for image classification.

The model classifies facial images into two classes:

- **Fake**
- **Real**

### Model Input

Images are resized to:

```text
224 × 224 pixels
```

MobileNetV2 preprocessing is then applied before the image is passed to the
trained model.

---

## 📊 Model Performance

The final model was evaluated using a separate test dataset containing
**2,000 previously unseen images**.

| Metric | Score |
|---|---:|
| Test Images | 2,000 |
| Accuracy | **90.85%** |
| Precision | **89.93%** |
| Recall | **92.00%** |
| F1 Score | **90.95%** |

### Confusion Matrix

```text
                 Predicted
                 Fake    Real

Actual Fake       897     103
Actual Real        80     920
```

### Performance Summary

- **Accuracy:** 90.85%
- **Precision:** 89.93%
- **Recall:** 92.00%
- **F1 Score:** 90.95%

These results show that the model performs well in distinguishing real and
fake facial images on the evaluation dataset.

---

## 📂 Project Structure

```text
deepfake-detector/
│
├── database/
│   └── deepvision.db
│
├── dataset/
│   ├── train/
│   ├── valid/
│   └── test/
│
├── model/
│   ├── mobilenetv2_deepfake.keras
│   └── plots/
│
├── static/
│   ├── css/
│   ├── images/
│   └── uploads/
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── detect.html
│   ├── result.html
│   └── history.html
│
├── app.py
├── config.py
├── database.py
├── predict.py
├── train.py
├── test_model.py
├── test_predict.py
├── test_saved_model.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### 2. Open the project directory

```bash
cd deepfake-detector
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the Flask application:

```bash
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

---

## 🔍 How DeepVision AI Works

```text
                User
                 │
                 ▼
          Upload Image
                 │
                 ▼
        Flask Web Application
                 │
                 ▼
       Image Preprocessing
          224 × 224
                 │
                 ▼
           MobileNetV2
                 │
                 ▼
            Prediction
             /      \
            /        \
          Fake       Real
            \        /
             \      /
              ▼    ▼
          Confidence
             Score
                 │
                 ▼
          Display Result
                 │
                 ▼
       Save Prediction History
```

---

## 🔐 User Authentication

DeepVision AI provides user authentication features including:

- User registration
- Login
- Logout
- Session management

User information and prediction history are stored in the SQLite database.

---

## 🗃️ Database

DeepVision AI uses SQLite to store application and prediction information.

### Users Table

```text
users
├── id
├── username
├── email
├── password
└── created_at
```

### Predictions Table

```text
predictions
├── id
├── user_id
├── image_name
├── prediction
├── confidence
└── created_at
```

---

## 🧪 Testing

The project includes testing scripts for checking the trained model and
prediction pipeline.

### Test Model

```bash
python test_model.py
```

### Test Prediction

```bash
python test_predict.py
```

### Test Saved Model

```bash
python test_saved_model.py
```

---

## ⚠️ Limitations

DeepVision AI provides an AI-based prediction and should not be considered
absolute proof that an image is real or fake.

Performance can vary depending on:

- Image quality
- Face resolution
- Image compression
- Lighting conditions
- Facial pose
- Deepfake generation technique
- Differences between training and real-world images

The prediction should therefore be treated as **AI-assisted analysis**.

---

## 🔮 Future Enhancements

Future versions of DeepVision AI could include:

- 🎥 Video deepfake detection
- 🎙️ Audio deepfake detection
- ☁️ AWS/Azure cloud deployment
- 📱 Mobile application
- 🤖 Transformer-based deepfake detection
- 📊 Advanced analytics dashboard
- 🌐 REST API
- 🔄 Continuous model improvement
- ⚡ GPU-accelerated inference

---

## 👨‍💻 Author

**Prasan Kumar**

BE – Computer Science and Engineering  
APS College of Engineering  
Expected Graduation: 2027

---

## 📜 License

This project is developed for educational and academic purposes.

---

# ⭐ DeepVision AI

### Detect • Analyze • Protect