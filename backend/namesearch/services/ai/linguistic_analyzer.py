"""Linguistic analysis service for domain names."""
from typing import Dict, List, Tuple
import re
import spacy
from spacy.language import Language

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def analyze_domain_name(domain: str) -> Dict[str, any]:
    """
    Analyze a domain name for linguistic properties.
    
    Args:
        domain: The domain name to analyze (without TLD)
        
    Returns:
        Dict containing linguistic analysis results
    """
    # Basic cleanup
    domain = domain.lower().strip()
    
    # Initialize results
    results = {
        'word_count': 0,
        'syllable_count': 0,
        'character_count': len(domain),
        'vowel_count': 0,
        'consonant_count': 0,
        'digit_count': 0,
        'has_hyphen': '-' in domain,
        'has_number': any(char.isdigit() for char in domain),
        'words': [],
        'pos_tags': [],
        'sentiment': 0.0,
        'is_english_word': False,
        'is_pronounceable': False,
        'complexity_score': 0.0
    }
    
    # Basic character analysis
    vowels = set('aeiou')
    for char in domain:
        if char in vowels:
            results['vowel_count'] += 1
        elif char.isalpha():
            results['consonant_count'] += 1
        elif char.isdigit():
            results['digit_count'] += 1
    
    # Word tokenization and analysis
    doc = nlp(domain)
    results['words'] = [token.text for token in doc if not token.is_punct and not token.is_space]
    results['word_count'] = len(results['words'])
    results['pos_tags'] = [(token.text, token.pos_) for token in doc]
    
    # Calculate syllable count (approximate)
    results['syllable_count'] = sum([count_syllables(word) for word in results['words']])
    
    # Calculate complexity score (lower is better)
    results['complexity_score'] = calculate_complexity_score(results)
    
    # Determine if pronounceable
    results['is_pronounceable'] = is_pronounceable(domain, results)
    
    return results

def count_syllables(word: str) -> int:
    """Approximate syllable counting for English words."""
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    
    if word[0] in vowels:
        count += 1
    
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    
    if word.endswith('e'):
        count -= 1
    if word.endswith('le') and len(word) > 1 and word[-3] not in vowels:
        count += 1
    if count == 0:
        count = 1
        
    return count

def calculate_complexity_score(analysis: Dict) -> float:
    """Calculate a complexity score for the domain."""
    score = 0.0
    
    # Penalize hyphens
    if analysis['has_hyphen']:
        score += 0.5
        
    # Penalize numbers
    if analysis['has_number']:
        score += 0.5
        
    # More words = more complex
    score += min(1.0, analysis['word_count'] * 0.2)
    
    # Balance of vowels and consonants
    vowel_ratio = analysis['vowel_count'] / max(1, analysis['consonant_count'])
    if vowel_ratio < 0.2 or vowel_ratio > 2.0:  # Too many consonants or vowels
        score += 0.3
        
    # Length penalty
    length_score = min(1.0, analysis['character_count'] / 20)
    score += length_score
    
    return min(score, 5.0)  # Cap at 5.0

def is_pronounceable(domain: str, analysis: Dict) -> bool:
    """Determine if a domain is easily pronounceable."""
    # Very short domains are generally pronounceable
    if len(domain) <= 3:
        return True
        
    # Check for common unpronounceable patterns
    unpronounceable_patterns = [
        r'[^aeiouy]{4,}',  # 4+ consonants in a row
        r'[aeiouy]{4,}',   # 4+ vowels in a row
        r'([a-z])\1{2,}',  # 3+ repeating characters
    ]
    
    for pattern in unpronounceable_patterns:
        if re.search(pattern, domain):
            return False
            
    # Check syllable count
    if analysis['syllable_count'] > 5:  # Arbitrary threshold
        return False
        
    return True
