import math
import secrets
import string
from datetime import datetime, timedelta
import nltk
import random

# Download NLTK words if not available
try:
    from nltk.corpus import words
    WORDS = words.words()
except:
    WORDS = [
        "apple", "banana", "secure", "dragon", "sunshine", "mountain",
        "ocean", "forest", "keyboard", "guitar", "piano", "castle",
        "window", "sunset", "coffee", "diamond", "silver", "gold"
    ]

def generate_passphrase(word_count=4, add_number=True, add_symbol=True):
    """Generates a secure passphrase with optional numbers and symbols."""
    # Select unique words
    words = [secrets.choice(WORDS).capitalize() for _ in range(word_count)]

    # Optionally add a number
    if add_number:
        words.append(str(random.randint(10, 99)))

    # Optionally add a symbol
    if add_symbol:
        words.append(secrets.choice("!@#$%^&*()"))

    return " ".join(words)


def calculate_entropy(password):
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(c in string.punctuation for c in password):
        charset += 32
    
    if charset == 0:
        return 0
    
    entropy = len(password) * math.log2(charset)
    return round(entropy, 2)

def classify_strength(entropy):
    if entropy < 40:
        return "Weak"
    elif 40 <= entropy < 60:
        return "Medium"
    else:
        return "Strong"

def check_password_health(password):
    weak_patterns = [
        "123", "password", "qwerty", "abc", "111", "000",
        "asdf", "zxcv", "iloveyou", "letmein"
    ]
    
    issues = []
    
    # Check length
    if len(password) < 8:
        issues.append("Too short (minimum 8 characters)")
    
    # Check character diversity
    char_types = 0
    if any(c.islower() for c in password):
        char_types += 1
    if any(c.isupper() for c in password):
        char_types += 1
    if any(c.isdigit() for c in password):
        char_types += 1
    if any(c in string.punctuation for c in password):
        char_types += 1
    
    if char_types < 2:
        issues.append("Low character diversity")
    
    # Check common patterns
    lower_pass = password.lower()
    if any(pattern in lower_pass for pattern in weak_patterns):
        issues.append("Contains common pattern")
    
    # Check repetition
    if len(set(password)) < len(password) / 2:
        issues.append("Too many repeated characters")
    
    return "Good password!" if not issues else ", ".join(issues)

def time_to_crack(entropy):
    # Assuming 1 trillion guesses per second
    seconds = (2 ** entropy) / 1e12
    
    if seconds < 1:
        return "Instant"
    
    intervals = (
        ('years', 31536000),
        ('months', 2592000),
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1)
    )
    
    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{int(value)} {name}")
    
    return ", ".join(result[:2])

