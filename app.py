import os
import json
import joblib
import numpy as np
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import (
    init_db, get_db_connection, save_prediction, get_user_predictions,
    get_prediction_by_id, delete_prediction, clear_user_history, get_user_dashboard_stats
)
from utils.text_analyzer import analyze_text_statistics
from utils.clickbait_detector import analyze_clickbait
from utils.emotional_analyzer import analyze_emotional_language
from utils.credibility import calculate_credibility_score
from utils.explanation import generate_prediction_explanation

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database on app startup
init_db()

# Load ML Model and Vectorizer safely
model = None
vectorizer = None

def load_ml_assets():
    global model, vectorizer
    if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.VECTORIZER_PATH):
        try:
            model = joblib.load(Config.MODEL_PATH)
            vectorizer = joblib.load(Config.VECTORIZER_PATH)
            print("[+] Loaded Machine Learning Model and Vectorizer successfully.")
        except Exception as e:
            print(f"[!] Warning: Could not load ML model: {e}")

load_ml_assets()

# Authentication Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor for Jinja templates
@app.context_processor
def inject_user():
    return {
        'logged_in': 'user_id' in session,
        'user_name': session.get('user_name', ''),
        'user_id': session.get('user_id', None)
    }

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', name=name, email=email)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            flash('An account with this email address already exists.', 'danger')
            return render_template('register.html', name=name, email=email)

        password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                       (name, email, password_hash))
        conn.commit()

        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        new_user = cursor.fetchone()
        conn.close()

        session['user_id'] = new_user['id']
        session['user_name'] = name
        flash('Account created successfully! Welcome to TruthLens AI.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', email=email)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    news_text = request.form.get('news_text', '').strip()

    if not news_text:
        flash('Please enter or paste a news article or headline to analyze.', 'warning')
        return redirect(url_for('index'))

    # Load model if not loaded
    global model, vectorizer
    if model is None or vectorizer is None:
        load_ml_assets()

    if model is None or vectorizer is None:
        flash('Machine Learning model is not trained yet. Please run train_model.py first.', 'danger')
        return redirect(url_for('index'))

    # 1. Machine Learning Prediction & Confidence Calculation
    cleaned_text = news_text.lower()
    text_vector = vectorizer.transform([cleaned_text])

    # Check model capabilities for probability estimation
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(text_vector)[0]
        classes = list(model.classes_)
        fake_idx = classes.index('FAKE') if 'FAKE' in classes else 0
        real_idx = classes.index('REAL') if 'REAL' in classes else 1

        prob_fake = float(probabilities[fake_idx])
        prob_real = float(probabilities[real_idx])

        if prob_fake > prob_real:
            prediction = 'FAKE'
            confidence = prob_fake * 100.0
        else:
            prediction = 'REAL'
            confidence = prob_real * 100.0
    else: # e.g. LinearSVC decision function
        raw_pred = model.predict(text_vector)[0]
        prediction = str(raw_pred).upper()
        if hasattr(model, 'decision_function'):
            decision_val = float(model.decision_function(text_vector)[0])
            confidence = float(min(99.0, max(55.0, 50.0 + abs(decision_val) * 20.0)))
        else:
            confidence = 85.0

    # 2. Text Statistics Analysis
    text_stats = analyze_text_statistics(news_text)

    # 3. Clickbait Detection
    clickbait_data = analyze_clickbait(news_text)

    # 4. Emotional Language Analysis
    emotional_data = analyze_emotional_language(news_text)

    # 5. Credibility Score & Risk Level Assessment
    credibility_data = calculate_credibility_score(
        prediction, confidence, clickbait_data, emotional_data, text_stats
    )

    # 6. Explainable AI Breakdown
    explanation_data = generate_prediction_explanation(
        model, vectorizer, news_text, prediction, confidence,
        clickbait_data, emotional_data, text_stats
    )

    # Aggregate detected indicators for report
    all_indicators = []
    all_indicators.extend(clickbait_data['indicators'])
    all_indicators.extend(emotional_data['indicators'])

    if prediction == 'FAKE':
        all_indicators.append({
            'type': 'ML Classifier Flag',
            'text': f"Statistical term distribution strongly matches trained fake news corpus ({confidence:.1f}% confidence)",
            'severity': 'HIGH'
        })
    if text_stats['uppercase_ratio'] > 12:
        all_indicators.append({
            'type': 'Formatting Flag',
            'text': f"High proportion of uppercase text ({text_stats['uppercase_ratio']}%)",
            'severity': 'MEDIUM'
        })

    # Save to SQLite DB if user is logged in
    prediction_id = None
    if 'user_id' in session:
        prediction_id = save_prediction(
            user_id=session['user_id'],
            news_text=news_text,
            prediction=prediction,
            confidence=confidence,
            credibility_score=credibility_data['score'],
            risk_level=credibility_data['risk_level'],
            clickbait_score=clickbait_data['score'],
            emotional_score=emotional_data['score'],
            stats=text_stats,
            indicators=all_indicators
        )

    return render_template(
        'result.html',
        news_text=news_text,
        prediction=prediction,
        confidence=round(confidence, 2),
        credibility=credibility_data,
        clickbait=clickbait_data,
        emotional=emotional_data,
        stats=text_stats,
        explanation=explanation_data,
        indicators=all_indicators,
        prediction_id=prediction_id
    )

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    stats = get_user_dashboard_stats(user_id)
    recent_predictions = get_user_predictions(user_id)[:5]
    return render_template('dashboard.html', stats=stats, recent=recent_predictions)

@app.route('/history')
@login_required
def history():
    user_id = session['user_id']
    search_query = request.args.get('q', '').strip()
    filter_pred = request.args.get('prediction', '').strip()

    predictions = get_user_predictions(user_id, search_query=search_query, filter_prediction=filter_pred)
    return render_template('history.html', predictions=predictions, search_query=search_query, filter_pred=filter_pred)

@app.route('/report/<int:id>')
@login_required
def report(id):
    user_id = session['user_id']
    record = get_prediction_by_id(id, user_id)

    if not record:
        flash('Report not found or you do not have permission to view it.', 'danger')
        return redirect(url_for('history'))

    # Re-derive stats & visual attributes for the saved report view
    credibility_data = calculate_credibility_score(
        record['prediction'], record['confidence'],
        {'score': record['clickbait_score']},
        {'score': record['emotional_score']},
        {'uppercase_ratio': 0, 'exclamation_count': 0, 'word_count': record['word_count']}
    )

    stats = {
        'word_count': record['word_count'],
        'character_count': record['character_count'],
        'sentence_count': record['sentence_count']
    }

    return render_template('report.html', record=record, credibility=credibility_data, stats=stats)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_record(id):
    user_id = session['user_id']
    delete_prediction(id, user_id)
    flash('Analysis record deleted successfully.', 'success')
    return redirect(url_for('history'))

@app.route('/clear-history', methods=['POST'])
@login_required
def clear_history():
    user_id = session['user_id']
    clear_user_history(user_id)
    flash('Your analysis history has been cleared.', 'info')
    return redirect(url_for('history'))

@app.route('/model-performance')
def model_performance():
    metrics = None
    if os.path.exists(Config.METRICS_PATH):
        try:
            with open(Config.METRICS_PATH, 'r') as f:
                metrics = json.load(f)
        except Exception as e:
            print(f"Error reading metrics.json: {e}")

    return render_template('model_performance.html', metrics=metrics)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
