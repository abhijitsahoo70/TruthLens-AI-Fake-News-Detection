import re

CLICKBAIT_PHRASES = [
    "you won't believe", "you wont believe", "shocking", "breaking news",
    "secret revealed", "secrets revealed", "will change everything",
    "doctors hate this", "financial experts hate this", "simple trick",
    "miracle cure", "miracle herb", "what happens next", "will blow your mind",
    "must see", "must watch", "unbelievable", "mind blowing", "exposed",
    "leaked", "don't want you to know", "dont want you to know",
    "guaranteed to", "overnight", "magic pill", "proof", "deep state",
    "whistleblower", "conspiracy", "illuminati", "share before deleted"
]

def analyze_clickbait(text, stats=None):
    """
    Detects clickbait indicators and calculates a clickbait score (0-100) and risk level.
    """
    if not text:
        return {
            'score': 0,
            'clickbait_score': 0,
            'risk_level': 'LOW',
            'detected_phrases': [],
            'indicators': []
        }

    text_lower = text.lower()
    detected_phrases = []
    indicators = []

    # 1. Search for specific clickbait phrases
    for phrase in CLICKBAIT_PHRASES:
        if phrase in text_lower:
            detected_phrases.append(phrase)

    if detected_phrases:
        indicators.append({
            'type': 'Clickbait Phrases',
            'text': f"Found clickbait phrases: '{', '.join(detected_phrases[:3])}'",
            'severity': 'HIGH' if len(detected_phrases) > 1 else 'MEDIUM'
        })

    # 2. Check for excessive exclamation marks
    exclamation_count = text.count('!')
    if exclamation_count >= 3:
        indicators.append({
            'type': 'Excessive Punctuation',
            'text': f"High count of exclamation marks ({exclamation_count}) indicating sensationalism",
            'severity': 'HIGH' if exclamation_count > 5 else 'MEDIUM'
        })

    # 3. Check for ALL CAPS words count
    words = re.findall(r'\b\w+\b', text)
    uppercase_words = [w for w in words if len(w) > 1 and w.isupper()]
    if len(uppercase_words) >= 3:
        indicators.append({
            'type': 'Excessive Capitalization',
            'text': f"Multiple ALL CAPS words ({', '.join(uppercase_words[:4])}) used for attention grabbing",
            'severity': 'MEDIUM'
        })

    # 4. Check for sensational question formats
    if re.search(r'^(who|what|why|how|is this|are these|could this).*\?', text_lower) or text.count('?') >= 2:
        indicators.append({
            'type': 'Sensational Question',
            'text': "Text utilizes open sensational question framing",
            'severity': 'LOW'
        })

    # Calculate clickbait score (0 - 100)
    score = 0
    score += len(detected_phrases) * 25
    score += min(exclamation_count * 10, 30)
    score += min(len(uppercase_words) * 8, 25)
    if text.count('?') >= 2:
        score += 15

    score = min(score, 100)

    # Determine risk level
    if score >= 60:
        risk_level = 'HIGH'
    elif score >= 30:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    return {
        'score': score,
        'clickbait_score': score,
        'risk_level': risk_level,
        'detected_phrases': detected_phrases,
        'indicators': indicators
    }
