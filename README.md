# 🚀 TruthLens AI – Fake News Detection & News Forensics System

> **"Analyze. Detect. Understand. Verify."**

A complete, modern, academic, and portfolio-ready **AI-Powered Fake News Detection & News Forensics System** built using **Python 3, Flask, Machine Learning (Scikit-Learn), SQLite, HTML5, CSS3 (Custom Glassmorphism Design), JavaScript, and Chart.js**.

---

## 🌟 Key Highlights & Features

TruthLens AI goes beyond basic binary classification by providing an executive **News Forensics Report** for every analyzed article.

### 🔮 Core Features
1. **AI Fake News Detection**: High-accuracy TF-IDF Vectorizer combined with benchmarked classification models (Logistic Regression, Naive Bayes, Linear SVM).
2. **News Forensics Report**: Detailed report with confidence score, credibility rating, risk level, detected linguistic indicators, and text statistics.
3. **Credibility Score (0–100)**: Transparent heuristic index evaluating ML probability, clickbait risk, emotional tone, ALL CAPS ratio, and text length.
4. **Clickbait Detector**: Pattern recognition module detecting sensational headlines, curiosity gaps, excessive punctuation, and trigger phrases.
5. **Emotional Language Audit**: Lexicon-based scanning for manipulative fear, anger, and urgency trigger words.
6. **Explainable AI (XAI)**: Rationale breakdown revealing top TF-IDF keywords and feature attributions driving the model's decision.
7. **Personal User Dashboard**: Analytics hub with Chart.js visual graphs (Prediction Distribution & Credibility Tiers).
8. **Searchable Analysis History**: Archive of past analyses with keyword search, category filtering, individual report views, and single/bulk deletion options.
9. **Dynamic Model Performance Page**: Displays real live training metrics (Accuracy, Precision, Recall, F1 Score, Confusion Matrix, Model Comparison) read directly from `metrics.json`.
10. **Secure Authentication System**: User registration and login using Werkzeug password hashing (`pbkdf2:sha256`) and Flask sessions.

---

## 🏗️ System Architecture & Workflow

```text
               ┌───────────────────────────┐
               │    User Submits Article   │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │ Text Cleaning & Preprocess│
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │   TF-IDF Feature Extract  │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │   ML Model Classification │
               └─────────────┬─────────────┘
                             │
 ┌───────────────────────────┼───────────────────────────┐
 │                           │                           │
▼                           ▼                           ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Clickbait Audit │ │ Emotional Audit │ │ Text Statistics │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
               ┌─────────────▼─────────────┐
               │  Credibility Score (0-100)│
               │   & Risk Assessment       │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │  Save to SQLite Database  │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │   News Forensics Report   │
               └───────────────────────────┘
```

---

## 🛠️ Technology Stack

* **Backend**: Python 3, Flask, Werkzeug
* **Machine Learning**: Scikit-Learn (TF-IDF Vectorizer, Logistic Regression, MultinomialNB, LinearSVC), Pandas, NumPy, Joblib
* **Database**: SQLite3 (`database.db`)
* **Frontend**: HTML5, CSS3 (Vanilla Glassmorphism Dark Accent Theme), JavaScript (ES6+), Jinja2
* **Visualization**: Chart.js (CDN)

---

## 📁 Project Folder Structure

```text
TruthLens-AI/
│
├── app.py                     # Flask web application routes, auth, API logic
├── train_model.py             # ML dataset preprocessing, training, model evaluation
├── config.py                  # System & Flask configuration parameters
├── database.py                # SQLite database management and helper CRUD functions
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive project documentation
├── database.db                # SQLite database (auto-created on run)
│
├── dataset/
│   └── news.csv               # Demonstration dataset (title, text, label)
│
├── model/
│   ├── fake_news_model.pkl    # Serialized ML classifier
│   ├── tfidf_vectorizer.pkl   # Serialized TF-IDF vectorizer
│   └── metrics.json           # Live evaluation metrics output
│
├── utils/
│   ├── text_analyzer.py       # Structural text metrics (word, char, punctuation counts)
│   ├── clickbait_detector.py  # Clickbait pattern & headline scanner
│   ├── emotional_analyzer.py  # Emotional manipulation & lexicon auditor
│   ├── credibility.py         # 0-100 credibility scoring algorithm & risk mapper
│   └── explanation.py         # Explainable AI keyword attribution generator
│
├── templates/
│   ├── base.html              # Core layout, navbar, dynamic flash alerts, footer
│   ├── index.html             # Landing page with news analysis input box
│   ├── login.html             # User login page
│   ├── register.html          # User registration page
│   ├── dashboard.html         # Personal analytics dashboard with Chart.js
│   ├── result.html            # Immediate news forensics analysis view
│   ├── report.html            # Detailed printable forensics report
│   ├── history.html           # User analysis history table with search & filter
│   ├── model_performance.html # Dynamic model evaluation & benchmark dashboard
│   └── about.html             # Project background, architecture & tech stack
│
└── static/
    ├── css/
    │   └── style.css          # Glassmorphism dark/modern responsive theme
    ├── js/
    │   └── script.js          # Interactive counters, toggle buttons, Chart.js wrappers
    └── images/
```

---

## ⚙️ Installation & Setup Guide

### 1. Prerequisite
Ensure you have **Python 3.8+** installed on your system.

### 2. Open Command Prompt / Terminal
Navigate to the project root directory:

```bash
cd "c:/Users/Abhijit/OneDrive/Desktop/Fake News Detection System"
```

### 3. Create & Activate Virtual Environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Train the Machine Learning Model
Run the automated benchmarking and training pipeline:
```bash
python train_model.py
```
*This will evaluate Logistic Regression, Naive Bayes, and Linear SVM models, select the top performer based on F1-Score, and output `fake_news_model.pkl`, `tfidf_vectorizer.pkl`, and `metrics.json`.*

### 6. Run the Flask Web Application
```bash
python app.py
```

### 7. Access Application in Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## 📊 Database Schema (SQLite)

### Table 1: `users`
* `id` INTEGER PRIMARY KEY AUTOINCREMENT
* `name` TEXT NOT NULL
* `email` TEXT UNIQUE NOT NULL
* `password_hash` TEXT NOT NULL
* `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Table 2: `predictions`
* `id` INTEGER PRIMARY KEY AUTOINCREMENT
* `user_id` INTEGER NOT NULL (FK -> `users.id`)
* `news_text` TEXT NOT NULL
* `prediction` TEXT NOT NULL (`REAL` / `FAKE`)
* `confidence` REAL NOT NULL
* `credibility_score` INTEGER NOT NULL
* `risk_level` TEXT NOT NULL (`LOW` / `MEDIUM` / `HIGH`)
* `clickbait_score` INTEGER NOT NULL
* `emotional_score` INTEGER NOT NULL
* `word_count` INTEGER NOT NULL
* `character_count` INTEGER NOT NULL
* `sentence_count` INTEGER NOT NULL
* `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Table 3: `detected_indicators`
* `id` INTEGER PRIMARY KEY AUTOINCREMENT
* `prediction_id` INTEGER NOT NULL (FK -> `predictions.id`)
* `indicator_type` TEXT NOT NULL
* `indicator_text` TEXT NOT NULL
* `severity` TEXT NOT NULL (`LOW` / `MEDIUM` / `HIGH`)

---

## 🔒 Security & Privacy Features

* **Password Protection**: Passwords are hashed using Werkzeug (`pbkdf2:sha256`) before database storage.
* **SQL Injection Prevention**: All database queries utilize parameterized SQL statements.
* **Access Control**: Users can only view, search, report, or delete their own private analysis records.
* **Session Management**: Secure server-side Flask sessions for user state tracking.

---

## 📜 Disclaimer

**TruthLens AI** is an academic software project created for demonstration, educational evaluation, and portfolio presentation. It operates as a probabilistic machine learning prediction and linguistic text auditing tool and does **not** constitute an official or authoritative fact-checking service.
