import sqlite3
import os
from config import Config

def get_db_connection():
    """Establishes SQLite connection with row factory enabled."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: predictions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            news_text TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            credibility_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            clickbait_score INTEGER NOT NULL,
            emotional_score INTEGER NOT NULL,
            word_count INTEGER NOT NULL,
            character_count INTEGER NOT NULL,
            sentence_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Table 3: detected_indicators
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detected_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER NOT NULL,
            indicator_type TEXT NOT NULL,
            indicator_text TEXT NOT NULL,
            severity TEXT NOT NULL,
            FOREIGN KEY (prediction_id) REFERENCES predictions (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def save_prediction(user_id, news_text, prediction, confidence, credibility_score, 
                    risk_level, clickbait_score, emotional_score, stats, indicators):
    """Saves news analysis and associated indicators to database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO predictions (
            user_id, news_text, prediction, confidence, credibility_score,
            risk_level, clickbait_score, emotional_score, word_count,
            character_count, sentence_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        news_text,
        prediction,
        round(confidence, 2),
        credibility_score,
        risk_level,
        clickbait_score,
        emotional_score,
        stats['word_count'],
        stats['character_count'],
        stats['sentence_count']
    ))

    prediction_id = cursor.lastrowid

    # Insert detected indicators
    for ind in indicators:
        cursor.execute('''
            INSERT INTO detected_indicators (prediction_id, indicator_type, indicator_text, severity)
            VALUES (?, ?, ?, ?)
        ''', (prediction_id, ind['type'], ind['text'], ind['severity']))

    conn.commit()
    conn.close()
    return prediction_id

def get_user_predictions(user_id, search_query=None, filter_prediction=None):
    """Fetches list of predictions for a given user with optional search & filter."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM predictions WHERE user_id = ?"
    params = [user_id]

    if filter_prediction and filter_prediction in ['REAL', 'FAKE']:
        query += " AND prediction = ?"
        params.append(filter_prediction)

    if search_query:
        query += " AND news_text LIKE ?"
        params.append(f"%{search_query}%")

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_prediction_by_id(prediction_id, user_id):
    """Fetches detailed prediction record and associated indicators for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions WHERE id = ? AND user_id = ?", (prediction_id, user_id))
    pred_row = cursor.fetchone()

    if not pred_row:
        conn.close()
        return None

    pred_dict = dict(pred_row)

    cursor.execute("SELECT * FROM detected_indicators WHERE prediction_id = ?", (prediction_id,))
    indicator_rows = cursor.fetchall()
    conn.close()

    pred_dict['indicators'] = [dict(row) for row in indicator_rows]
    return pred_dict

def delete_prediction(prediction_id, user_id):
    """Deletes a single prediction record belonging to user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ? AND user_id = ?", (prediction_id, user_id))
    conn.commit()
    conn.close()

def clear_user_history(user_id):
    """Clears all prediction records belonging to user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_dashboard_stats(user_id):
    """Calculates summary statistics for user dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM predictions WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()['total']

    if total == 0:
        conn.close()
        return {
            'total': 0, 'fake_count': 0, 'real_count': 0,
            'avg_confidence': 0.0, 'avg_credibility': 0.0,
            'high_credibility': 0, 'moderate_credibility': 0,
            'low_credibility': 0, 'very_low_credibility': 0
        }

    cursor.execute("SELECT COUNT(*) as f_count FROM predictions WHERE user_id = ? AND prediction = 'FAKE'", (user_id,))
    fake_count = cursor.fetchone()['f_count']

    cursor.execute("SELECT COUNT(*) as r_count FROM predictions WHERE user_id = ? AND prediction = 'REAL'", (user_id,))
    real_count = cursor.fetchone()['r_count']

    cursor.execute("SELECT AVG(confidence) as avg_conf, AVG(credibility_score) as avg_cred FROM predictions WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    avg_confidence = round(row['avg_conf'] or 0.0, 1)
    avg_credibility = round(row['avg_cred'] or 0.0, 1)

    # Credibility breakdown tiers
    cursor.execute("SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND credibility_score >= 80", (user_id,))
    high_credibility = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND credibility_score >= 60 AND credibility_score < 80", (user_id,))
    moderate_credibility = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND credibility_score >= 40 AND credibility_score < 60", (user_id,))
    low_credibility = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM predictions WHERE user_id = ? AND credibility_score < 40", (user_id,))
    very_low_credibility = cursor.fetchone()['cnt']

    conn.close()
    return {
        'total': total,
        'fake_count': fake_count,
        'real_count': real_count,
        'avg_confidence': avg_confidence,
        'avg_credibility': avg_credibility,
        'high_credibility': high_credibility,
        'moderate_credibility': moderate_credibility,
        'low_credibility': low_credibility,
        'very_low_credibility': very_low_credibility
    }
