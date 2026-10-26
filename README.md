---
title: DeepVision AI
emoji: 👁️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 5000
pinned: false
---

# 🧠 DeepVision AI

### AI-Powered Deepfake Image Detection System

DeepVision AI is a web-based **AI-powered deepfake image detection system** built using **Python, Flask, TensorFlow, and MobileNetV2**.

The application allows users to upload facial images and uses a trained deep learning model to classify them as **REAL** or **FAKE**, along with a confidence score. User accounts and prediction history are managed using **SQLite**.

---

## 🚀 Key Features

* 🔍 AI-powered deepfake image detection
* 🧠 MobileNetV2-based deep learning model
* ⚡ Fast image prediction
* 📊 Prediction confidence score
* 🛡️ **Production-Grade Authentication & Security:**
  * 📧 **Two-Step Email Verification (2FA)** for signup and login
  * 🔐 **Scrypt Cryptographic Password Hashing** (zero plaintext storage, automatic migration)
  * ⏱️ **Cryptographic OTP Tokens** (5-minute expiry, 5-attempt limit, SHA-256 hashed storage)
  * 🛑 **Account Lockout & Brute-Force Throttling** (15-minute lockout after 5 failed attempts)
  * 🔑 **Forgot Password & Single-Use Password Reset** via secure email tokens
  * 🛡️ **CSRF Protection** across all state-changing endpoints
  * 🍪 **Persistent Session Management** (HttpOnly, SameSite=Lax, Secure across restarts)
* 🗃️ **SQLite Database with WAL Mode** (high-concurrency, zero database-locked collisions)
* 📜 Prediction history with filtering and search
* 🖥️ Responsive luxury dark gold web interface
* 📁 Image upload support (PNG, JPG, JPEG, WEBP up to 16MB)
* 📈 Model performance evaluation
* 🧪 Comprehensive automated unit and integration test suite

---

## 🛠️ Technology Stack

### Backend

* Python
* Flask
* SQLite

### Artificial Intelligence & Machine Learning

* TensorFlow
* Keras
* MobileNetV2
* NumPy
* Pillow
* Scikit-learn
* Pandas
* Matplotlib

### Frontend

* HTML5
* CSS3
* JavaScript

### Development & Version Control

* Git
* GitHub
* Python Virtual Environment

---

## 🧠 Deep Learning Model

DeepVision AI uses **MobileNetV2**, a lightweight convolutional neural network architecture designed for efficient image classification.

The model was trained to classify facial images into two categories:

| Class   | Description                              |
| ------- | ---------------------------------------- |
| 🟢 Real | Authentic facial image                   |
| 🔴 Fake | AI-generated or manipulated facial image |

### Model Input

Images are resized to:

```text
224 × 224 pixels
```

MobileNetV2 preprocessing is applied before the image is passed to the trained model.

### Model File

The trained model is stored in:

```text
model/deepvision_mobilenetv2_stage2_best.keras
```

---

# 📊 Model Performance

The final model was evaluated using a separate test dataset containing **2,000 previously unseen images**.

| Metric      |     Result |
| ----------- | ---------: |
| Test Images |      2,000 |
| Accuracy    | **90.85%** |
| Precision   | **89.93%** |
| Recall      | **92.00%** |
| F1 Score    | **90.95%** |

### Confusion Matrix

```text
                     Predicted
                  Fake       Real

Actual Fake       897        103
Actual Real        80        920
```

### Performance Summary

* **Accuracy:** 90.85%
* **Precision:** 89.93%
* **Recall:** 92.00%
* **F1 Score:** 90.95%

The results indicate that the model can effectively distinguish between real and fake facial images on the evaluation dataset.

> ⚠️ Model performance may vary when detecting deepfakes created using different generation techniques or datasets.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────┐
                         │      User       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Flask Web App  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Image Upload   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Image Processing│
                         │   224 × 224     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   MobileNetV2   │
                         │  Deep Learning  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    Prediction   │
                         └────────┬────────┘
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                      ┌───────┐        ┌───────┐
                      │  FAKE │        │  REAL │
                      └───┬───┘        └───┬───┘
                          │                │
                          └───────┬────────┘
                                  ▼
                         ┌─────────────────┐
                         │ Confidence Score│
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Display Result  │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Prediction      │
                         │ History / DB    │
                         └─────────────────┘
```

---

# 📂 Project Structure

```text
DeepVision-AI/
│
├── model/
│   └── deepvision_mobilenetv2_stage2_best.keras
│
├── static/
│   ├── css/
│   │   ├── animation.css
│   │   ├── dashboar.css
│   │   ├── detect.css
│   │   ├── history.css
│   │   ├── login.css
│   │   ├── navbar.css
│   │   ├── responsive.css
│   │   ├── result.css
│   │   └── style.css
│   │
│   └── images/
│       ├── ai-eye.png
│       └── sample.png
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── detect.html
│   ├── history.html
│   ├── index.html
│   ├── landing_base.html
│   ├── loading.html
│   ├── login.html
│   ├── result.html
│   └── signup.html
│
├── utils/
│   ├── helper.py
│   ├── metrics.py
│   └── plots.py
│
├── app.py
├── config.py
├── database.py
├── predict.py
├── train.py
├── check_model.py
├── test_model.py
├── test_predict.py
├── test_saved_model.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/prasankumar2604-dev/DeepVision-AI.git
```

## 2. Open the Project Directory

```bash
cd DeepVision-AI
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

## 4. Activate the Virtual Environment

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure Environment Variables

Copy the provided `.env.example` template:

```bash
cp .env.example .env
```

Edit `.env` to configure your settings:

| Variable | Description | Default / Example |
| -------- | ----------- | ----------------- |
| `FLASK_SECRET_KEY` | Persistent session signing key | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | Environment mode (`development` / `production`) | `development` |
| `SESSION_COOKIE_SECURE` | Set `true` if serving over HTTPS | `false` |
| `PORT` | Web server listening port | `5000` |
| `APP_BASE_URL` | Base URL used in reset emails | `http://localhost:5000` |
| `SMTP_HOST` | Outgoing SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | Outgoing SMTP port (587 or 465) | `587` |
| `SMTP_USERNAME` | SMTP account email address | `your_email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password / App password | `your_app_password` |
| `SMTP_USE_TLS` | Enable STARTTLS | `true` |
| `MAIL_FROM` | Sender display name & address | `"DeepVision AI Security" <noreply@deepvision.ai>` |

> 💡 **Local Development Notice:** If SMTP credentials are not yet configured, DeepVision AI automatically logs 6-digit verification OTPs and password reset links to the server terminal console for testing. Accounts are never marked as verified without entering the code.

---

# 🧪 Automated Test Suite

Run the full automated authentication, security, and inference test suite:

```bash
python -m unittest tests/test_auth.py
```

---

# ▶️ Running the Application

### Local Development

Start the Flask application:

```bash
python app.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

### Docker & Docker Compose

Run DeepVision AI in a production-ready container with persistent database and upload volumes:

```bash
docker compose up -d --build
```

---

# 🔍 How DeepVision AI Works

The detection pipeline follows these steps:

```text
1. User uploads a facial image
             ↓
2. Flask receives the image
             ↓
3. Image is resized to 224 × 224
             ↓
4. MobileNetV2 preprocessing is applied
             ↓
5. Trained MobileNetV2 model processes the image
             ↓
6. Model generates prediction
             ↓
7. Prediction is classified as REAL or FAKE
             ↓
8. Confidence score is calculated
             ↓
9. Result is displayed to the user
             ↓
10. Prediction is stored in SQLite history
```

---

# 🔐 User Authentication

DeepVision AI includes user authentication functionality.

Users can:

* Create an account
* Log in
* Log out
* Maintain an authenticated session
* Access their prediction history

User information and prediction records are stored in the SQLite database.

---

# 🗃️ Database

DeepVision AI uses **SQLite** for local application data storage.

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

Prediction records are associated with individual users through `user_id`.

---

# 🧪 Testing

The project includes scripts for testing the trained model and prediction pipeline.

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

### Model Diagnostic

```bash
python check_model.py
```

The diagnostic script can be used to inspect model predictions and classification performance against the configured dataset.

---

# 🔒 Security & Data Handling

The repository is configured to prevent local and sensitive files from being committed.

The `.gitignore` excludes:

```text
venv/
__pycache__/
dataset/
*.zip
static/uploads/*
database/*.db
.env
*.log
.DS_Store
Thumbs.db
```

This keeps local datasets, uploaded images, databases, virtual environments, and environment files out of version control.

---

# ⚠️ Limitations

DeepVision AI provides an **AI-assisted prediction** and should not be considered absolute proof that an image is real or fake.

Prediction performance can vary depending on:

* Image quality
* Face resolution
* Image compression
* Lighting conditions
* Facial pose
* Deepfake generation method
* Dataset differences
* Image preprocessing
* Unseen manipulation techniques

The system should therefore be treated as an **experimental deepfake detection tool**, not a definitive forensic system.

---

# 🔮 Future Development Roadmap

The project can be extended with the following technologies and features:

### ☁️ Cloud

* AWS deployment
* Azure deployment
* Cloud-based model serving
* Cloud database integration
* Object storage for uploaded images

### 🐳 DevOps

* Docker containerization
* Docker Compose
* GitHub Actions
* CI/CD pipeline
* Automated testing
* Container image management

### 🤖 AI / Machine Learning

* Video deepfake detection
* Audio deepfake detection
* Transformer-based detection
* Improved model architectures
* GPU-accelerated inference
* Continuous model improvement

### 🌐 Application

* REST API
* Advanced analytics dashboard
* API authentication
* Mobile application
* Real-time monitoring
* Improved scalability

---

# 🗺️ Project Roadmap

```text
DeepVision AI
      │
      ├── ✅ Flask Web Application
      ├── ✅ MobileNetV2 Model
      ├── ✅ Image Detection
      ├── ✅ User Authentication
      ├── ✅ SQLite Database
      ├── ✅ Prediction History
      ├── ✅ Model Evaluation
      ├── ✅ GitHub Repository
      │
      ├── 🔜 Docker Containerization
      ├── 🔜 CI/CD with GitHub Actions
      ├── 🔜 AWS / Azure Deployment
      ├── 🔜 REST API
      ├── 🔜 Video Detection
      └── 🔜 Production Deployment
```

---

# 💻 GitHub

Project Repository:

**DeepVision AI**

https://github.com/prasankumar2604-dev/DeepVision-AI

---

# 👨‍💻 Author

### Prasan Kumar

**BE – Computer Science and Engineering**

APS College of Engineering
Expected Graduation: **2027**

Interested in:

* ☁️ Cloud Computing
* ⚙️ DevOps
* 🤖 Artificial Intelligence
* 🐍 Python
* 🌐 Web Development

---

# 📜 License

This project was developed for **educational and academic purposes**.

---

# ⭐ DeepVision AI

### Detect • Analyze • Protect

Built with ❤️ using Python, Flask, TensorFlow and MobileNetV2.
