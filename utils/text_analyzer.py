import re
from collections import Counter

def analyze_text_statistics(text):
    """
    Analyzes input text and computes fundamental text metrics.
    """
    if not text or not isinstance(text, str):
        return {
            'word_count': 0,
            'character_count': 0,
            'sentence_count': 0,
            'avg_word_length': 0.0,
            'uppercase_word_count': 0,
            'exclamation_count': 0,
            'question_count': 0,
            'repeated_word_count': 0,
            'uppercase_ratio': 0.0
        }

    # Clean characters & extract words
    words = re.findall(r'\b[A-Za-z0-9\'-]+\b', text)
    word_count = len(words)
    character_count = len(text)

    # Sentences split by [.!?]+
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    sentence_count = max(1, len(sentences))

    # Average word length
    avg_word_length = round(sum(len(w) for w in words) / max(1, word_count), 2) if word_count > 0 else 0.0

    # ALL CAPS words (length >= 2 to avoid single 'I' or 'A')
    uppercase_words = [w for w in words if w.isupper() and len(w) >= 2]
    uppercase_word_count = len(uppercase_words)
    uppercase_ratio = round((uppercase_word_count / max(1, word_count)) * 100, 2)

    # Punctuation counts
    exclamation_count = text.count('!')
    question_count = text.count('?')

    # Repeated words calculation (words appearing more than twice)
    lower_words = [w.lower() for w in words if len(w) > 3]
    word_counts = Counter(lower_words)
    repeated_words = [w for w, count in word_counts.items() if count >= 3]
    repeated_word_count = len(repeated_words)

    return {
        'word_count': word_count,
        'character_count': character_count,
        'sentence_count': sentence_count,
        'avg_word_length': avg_word_length,
        'uppercase_word_count': uppercase_word_count,
        'uppercase_ratio': uppercase_ratio,
        'exclamation_count': exclamation_count,
        'question_count': question_count,
        'repeated_word_count': repeated_word_count
    }
