# Prakriti AI - Facial Analysis System

Welcome to the Prakriti AI Facial Analysis project! This application combines a Node.js Express backend with a Python Flask machine learning service to deliver AI-driven facial analysis for Ayurveda (Vata, Pitta, Kapha classification) and comprehensive skin health diagnostics.

---

## 🛠️ Prerequisites (If running on another PC)

Before running the application on a new computer, ensure the following software is installed on the system:

1. **Python 3.8 or higher**: Download from [python.org](https://www.python.org/downloads/)
   - *Important:* Ensure you check the box that says **"Add Python to PATH"** during installation.
2. **Node.js**: Download from [nodejs.org](https://nodejs.org/) (LTS version is recommended).
   - This will also install `npm`.
   
*(Optional)* **MongoDB**: The application is built to fall back to local file storage if MongoDB is not provided! To use a database natively, ensure MongoDB is installed locally or you provide a cloud MongoDB URI in the `.env` file.

---

## 🚀 Installation

Open your terminal (or Command Prompt / PowerShell) inside the root directory (`prakriti-ai-ready-deploy`).

### 1. Install Node.js Backend Dependencies
Install all Javascript dependencies for the web server:
```bash
npm install
```

### 2. Install Python ML Service Dependencies
Install all Python libraries for the AI models:
```bash
pip install -r ml_service/requirements.txt
```

*(Highly Recommended)* **Virtual Environment:** If you prefer isolating Python dependencies to this project, setup a virtual environment first:
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

pip install -r ml_service/requirements.txt
```

---

## ▶️ How to Run the Project

You can either use the provided startup script, or run the services manually in two separate terminal windows.

### Method 1: One-Click Start (Windows Only)
Simply double-click the **`start.bat`** file in the root directory. 
This completely automates the process: it checks for installations, safely starts the ML Service, boots up the Backend server, and opens the terminal popups for logs.

### Method 2: Manual Start (Mac / Linux / Windows)

You will need to open **two** separate terminal windows.

**Terminal 1: Start the ML Service**
```bash
# Make sure your virtual env is active if you created one!
python ml_service/app.py
```
*Wait until you see:* `* Running on http://127.0.0.1:5000`

**Terminal 2: Start the Backend Server**
```bash
npm start
```
*Wait until you see:* `Backend server running on http://localhost:3000`

### 3. Open in Browser
Finally, open your internet browser and navigate to:
**http://localhost:3000**

---

## 💡 Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`**: This means the Python dependencies haven't been successfully installed. Ensure you run `pip install -r ml_service/requirements.txt`.
- **Port already in use**: The system uses ports `3000` (Node.js) and `5000` (Python). If these are busy, find the process using them (e.g. `netstat -ano | findstr :3000`) and manually close them using Task Manager or command line (`taskkill /PID <id> /F`).
- **No trained model found**: The ML service requires a trained ML model to provide predictions. If prompted, you can manually train it by executing `python ml_service/train.py`.
