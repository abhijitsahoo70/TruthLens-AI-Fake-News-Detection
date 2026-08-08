import numpy as np

def generate_prediction_explanation(model, vectorizer, text, prediction, confidence, clickbait_info, emotional_info, text_stats):
    """
    Generates explainable rationale for the ML prediction using TF-IDF feature weights
    and linguistic heuristic findings.
    """
    explanations = []
    top_features = []
    top_words = []

    if model and vectorizer and hasattr(model, 'coef_'):
        try:
            # Vectorize input text
            tfidf_vec = vectorizer.transform([text])
            feature_names = np.array(vectorizer.get_feature_names_out())
            
            # Non-zero feature indices for input text
            nonzero_indices = tfidf_vec.nonzero()[1]
            
            if len(nonzero_indices) > 0:
                coefs = model.coef_[0][nonzero_indices]
                values = tfidf_vec.data
                
                # Feature contributions = TFIDF value * coefficient
                contributions = values * coefs
                
                # Pair with feature names
                feature_tuples = [(feature_names[idx], contributions[i], coefs[i]) for i, idx in enumerate(nonzero_indices)]
                
                classes = list(model.classes_)
                if prediction.upper() == 'FAKE':
                    sorted_features = sorted(feature_tuples, key=lambda x: x[1])
                else:
                    sorted_features = sorted(feature_tuples, key=lambda x: x[1], reverse=True)

                top_features = [
                    {
                        'term': f[0],
                        'weight': round(float(f[1]), 3),
                        'impact': 'FAKE' if f[2] < 0 else 'REAL'
                    } for f in sorted_features[:6]
                ]
                top_words = [f['term'] for f in top_features]
        except Exception as e:
            top_features = []
            top_words = []

    # 1. Prediction-level explanations
    conf_val = float(confidence)
    if prediction.upper() == 'FAKE':
        explanations.append(f"The Machine Learning model assigned a confidence probability of {conf_val:.1f}% to the FAKE class.")
        if top_words:
            explanations.append(f"Keywords matching suspicious training corpus terms detected: {', '.join([repr(w) for w in top_words[:4]])}.")
    else:
        explanations.append(f"The Machine Learning model assigned a confidence probability of {conf_val:.1f}% to the REAL class.")
        if top_words:
            explanations.append(f"Keywords matching verified news corpus terms detected: {', '.join([repr(w) for w in top_words[:4]])}.")

    # 2. Clickbait explanations
    cb_score = clickbait_info.get('score', clickbait_info.get('clickbait_score', 0))
    if cb_score > 30:
        explanations.append(f"Detected clickbait indicators (Risk Level: {clickbait_info.get('risk_level', 'MEDIUM')}) designed to provoke emotional clicks.")

    # 3. Emotional explanations
    emo_intensity = emotional_info.get('intensity', emotional_info.get('intensity_level', 'LOW'))
    if emo_intensity in ['MEDIUM', 'HIGH']:
        explanations.append(f"Contains {emo_intensity.lower()} density of emotionally manipulative language.")

    # 4. Syntactic explanations
    excl = text_stats.get('exclamation_count', text_stats.get('exclamation_marks', 0))
    if excl >= 2:
        explanations.append(f"Unusual punctuation detected with {excl} exclamation marks.")

    caps_ratio = text_stats.get('uppercase_ratio', 0)
    if caps_ratio > 10:
        explanations.append("High ratio of ALL CAPS uppercase text detected.")

    return {
        'explanations': explanations,
        'top_features': top_features,
        'top_words': top_words
    }
