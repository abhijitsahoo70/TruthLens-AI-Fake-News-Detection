def calculate_credibility_score(prediction, confidence, clickbait_input, emotional_input, text_stats):
    """
    Calculates a project-specific Credibility Score (0-100) and overall Risk Level.
    Accepts integer scores or dictionaries for clickbait_input and emotional_input.
    """
    # Extract numerical scores safely
    if isinstance(clickbait_input, dict):
        cb_score = float(clickbait_input.get('score', 0))
    else:
        cb_score = float(clickbait_input or 0)

    if isinstance(emotional_input, dict):
        emo_score = float(emotional_input.get('score', 0))
    else:
        emo_score = float(emotional_input or 0)

    # 1. Base Score calculation according to ML prediction and confidence
    conf_pct = float(confidence)
    if conf_pct > 1.0:
        conf_pct = conf_pct / 100.0  # normalize if passed as percentage (e.g. 87.4 -> 0.874)

    if prediction.upper() == 'REAL':
        base_score = 65.0 + (conf_pct * 30.0) # Range: ~65 - 95
    else: # FAKE
        base_score = 40.0 - (conf_pct * 30.0) # Range: ~10 - 40

    # 2. Deductions
    clickbait_penalty = (cb_score / 100.0) * 20.0
    emotional_penalty = (emo_score / 100.0) * 15.0

    # Punctuation and Capitalization anomalies
    excl_count = text_stats.get('exclamation_count', text_stats.get('exclamation_marks', 0))
    punctuation_penalty = min(excl_count * 3.0, 10.0)

    caps_ratio = text_stats.get('uppercase_ratio', 0)
    caps_count = text_stats.get('uppercase_word_count', text_stats.get('uppercase_words', 0))
    if caps_ratio > 10 or caps_count > 3:
        caps_penalty = 10.0
    elif caps_ratio > 5 or caps_count > 1:
        caps_penalty = 5.0
    else:
        caps_penalty = 0.0

    # Text length adjustment
    word_count = text_stats.get('word_count', 0)
    length_bonus = 0.0
    if word_count < 15:
        length_bonus = -10.0  # Extremely short text lacks context
    elif 40 <= word_count <= 300:
        length_bonus = 5.0   # Healthy length for analysis

    # Final combined score calculation
    final_score = base_score - clickbait_penalty - emotional_penalty - punctuation_penalty - caps_penalty + length_bonus
    
    # Clamp score strictly to range 0 - 100
    score_val = max(0, min(100, int(round(final_score))))

    # Credibility Label assignment
    if score_val >= 80:
        label = "High Credibility"
        badge_class = "success"
    elif score_val >= 60:
        label = "Moderate Credibility"
        badge_class = "info"
    elif score_val >= 40:
        label = "Low Credibility"
        badge_class = "warning"
    else:
        label = "Very Low Credibility"
        badge_class = "danger"

    # Overall Risk Level assignment
    if score_val < 45 or prediction.upper() == 'FAKE':
        if score_val < 30 or cb_score > 50:
            risk_level = "HIGH"
            risk_class = "danger"
        else:
            risk_level = "MEDIUM"
            risk_class = "warning"
    elif score_val < 75:
        risk_level = "MEDIUM"
        risk_class = "warning"
    else:
        risk_level = "LOW"
        risk_class = "success"

    return {
        'score': score_val,
        'credibility_score': score_val,
        'label': label,
        'badge_class': badge_class,
        'risk_level': risk_level,
        'risk_class': risk_class,
        'breakdown': {
            'base_score': round(base_score, 1),
            'clickbait_penalty': round(clickbait_penalty, 1),
            'emotional_penalty': round(emotional_penalty, 1),
            'punctuation_penalty': round(punctuation_penalty, 1),
            'caps_penalty': round(caps_penalty, 1),
            'length_bonus': round(length_bonus, 1)
        }
    }
