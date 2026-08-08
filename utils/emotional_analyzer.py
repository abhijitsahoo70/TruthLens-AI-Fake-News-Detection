import re

FEAR_WORDS = [
    "danger", "deadly", "lethal", "terrifying", "warning", "threat", "disaster",
    "catastrophe", "poison", "toxic", "panic", "fear", "crisis", "fatal", "emergency",
    "scare", "horrifying", "nightmare", "armageddon", "collapse", "risk", "harmful"
]

ANGER_WORDS = [
    "furious", "outrage", "corrupt", "scandal", "hate", "evil", "disgrace", "shame",
    "rebellion", "fury", "betrayal", "treason", "illegal", "criminal", "attack",
    "destroy", "conspiracy", "scam", "fraud", "tyranny", "oppression", "enemy"
]

URGENCY_WORDS = [
    "urgent", "immediately", "right now", "instant", "instantly", "before deleted",
    "overnight", "emergency", "alert", "act now", "limited time", "don't wait",
    "fast", "quick", "critical", "now", "today", "breaking"
]

POSITIVE_WORDS = [
    "miracle", "amazing", "cure", "breakthrough", "incredible", "unbelievable",
    "secret", "magic", "wonderful", "guaranteed", "unlocked", "revolution",
    "spectacular", "paradise", "blessing", "best", "perfect", "victory"
]

NEGATIVE_WORDS = [
    "terrible", "horrible", "fake", "lies", "deceit", "banned", "denied",
    "brawled", "ruined", "failed", "disastrous", "suffering", "loss", "tragedy"
]

def analyze_emotional_language(text):
    """
    Analyzes manipulative and emotional language intensity based on keyword lexicons.
    """
    if not text:
        return {
            'fear_count': 0,
            'anger_count': 0,
            'urgency_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'score': 0,
            'emotional_score': 0,
            'intensity': 'LOW',
            'intensity_level': 'LOW',
            'detected_words': [],
            'indicators': []
        }

    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    fear_matches = [w for w in FEAR_WORDS if w in text_lower]
    anger_matches = [w for w in ANGER_WORDS if w in text_lower]
    urgency_matches = [w for w in URGENCY_WORDS if w in text_lower]
    positive_matches = [w for w in POSITIVE_WORDS if w in text_lower]
    negative_matches = [w for w in NEGATIVE_WORDS if w in text_lower]

    fear_count = len(fear_matches)
    anger_count = len(anger_matches)
    urgency_count = len(urgency_matches)
    positive_count = len(positive_matches)
    negative_count = len(negative_matches)

    total_emotional_triggers = fear_count + anger_count + urgency_count + positive_count + negative_count
    
    word_count = max(len(words), 1)
    density_ratio = (total_emotional_triggers / word_count) * 100
    
    emotional_score = min(int(total_emotional_triggers * 15 + density_ratio * 10), 100)

    if emotional_score >= 60 or total_emotional_triggers >= 6:
        intensity_level = 'HIGH'
    elif emotional_score >= 30 or total_emotional_triggers >= 3:
        intensity_level = 'MEDIUM'
    else:
        intensity_level = 'LOW'

    detected_words = list(set(fear_matches + anger_matches + urgency_matches + positive_matches + negative_matches))

    indicators = []
    if fear_count > 0:
        indicators.append({
            'type': 'Emotional Manipulation',
            'text': f"Fear-inducing trigger words detected ({', '.join(fear_matches[:3])})",
            'severity': 'HIGH' if fear_count >= 2 else 'MEDIUM'
        })
    if anger_count > 0:
        indicators.append({
            'type': 'Emotional Manipulation',
            'text': f"Outrage or anger trigger words detected ({', '.join(anger_matches[:3])})",
            'severity': 'HIGH' if anger_count >= 2 else 'MEDIUM'
        })
    if urgency_count > 0:
        indicators.append({
            'type': 'Emotional Manipulation',
            'text': f"High urgency or panic indicators detected ({', '.join(urgency_matches[:3])})",
            'severity': 'MEDIUM'
        })

    return {
        'fear_count': fear_count,
        'anger_count': anger_count,
        'urgency_count': urgency_count,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'total_emotional_triggers': total_emotional_triggers,
        'score': emotional_score,
        'emotional_score': emotional_score,
        'intensity': intensity_level,
        'intensity_level': intensity_level,
        'detected_words': detected_words[:8],
        'indicators': indicators
    }
