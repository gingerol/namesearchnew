"""Domain name generation and variation utilities."""
from typing import List, Set, Optional
import random
import string
import re

# Common TLDs for domain generation
COMMON_TLDS = [
    'com', 'io', 'ai', 'app', 'dev', 'net', 'org', 'co', 'us', 'ca', 'uk', 'de',
    'cloud', 'tech', 'hq', 'inc', 'me', 'blog', 'shop', 'store', 'online', 'site'
]

# Common prefixes and suffixes for domain variations
PREFIXES = [
    'get', 'try', 'go', 'my', 'the', 'we', 'use', 'join', 'find', 'meet', 'lets',
    'hi', 'hey', 'hello', 'app', 'hq', 'inc', 'co', 'pro', 'new', 'best', 'top'
]

SUFFIXES = [
    'app', 'hq', 'inc', 'ai', 'io', 'co', 'pro', 'dev', 'tech', 'labs', 'hq',
    'now', 'xyz', 'ly', 'fy', 'lyst', 'list', 'it', 'that', 'this', 'today', 'live'
]

def generate_domain_variations(keyword: str, limit: int = 20) -> List[str]:
    """
    Generate domain name variations from a keyword.
    
    Args:
        keyword: The base keyword to generate variations from
        limit: Maximum number of variations to return
        
    Returns:
        List of domain name variations
    """
    if not keyword or not isinstance(keyword, str):
        return []
    
    # Clean the keyword
    keyword = keyword.lower().strip()
    keyword = re.sub(r'[^a-z0-9]', '', keyword)  # Remove non-alphanumeric
    
    if not keyword:
        return []
    
    variations: Set[str] = set()
    
    # 1. Basic variations with different TLDs
    for tld in COMMON_TLDS:
        variations.add(f"{keyword}.{tld}")
        if len(variations) >= limit:
            return list(variations)[:limit]
    
    # 2. Add common prefixes
    for prefix in PREFIXES:
        variations.add(f"{prefix}{keyword}.com")
        variations.add(f"{prefix}{keyword}.io")
        if len(variations) >= limit:
            return list(variations)[:limit]
    
    # 3. Add common suffixes
    for suffix in SUFFIXES:
        variations.add(f"{keyword}{suffix}.com")
        variations.add(f"{keyword}{suffix}.io")
        if len(variations) >= limit:
            return list(variations)[:limit]
    
    # 4. Add hyphenated variations
    if len(keyword) > 3:
        for i in range(1, min(4, len(keyword))):
            variations.add(f"{keyword[:i]}-{keyword[i:]}.com")
            if len(variations) >= limit:
                return list(variations)[:limit]
    
    # 5. Add random character variations if we still need more
    while len(variations) < limit and len(keyword) > 3:
        # Add/remove a random character
        idx = random.randint(0, len(keyword)-1)
        # Remove a character
        new_word = keyword[:idx] + keyword[idx+1:]
        variations.add(f"{new_word}.com")
        
        # Replace a character with a vowel
        vowels = 'aeiou'
        if keyword[idx] not in vowels and len(variations) < limit:
            for vowel in vowels:
                new_word = keyword[:idx] + vowel + keyword[idx+1:]
                variations.add(f"{new_word}.com")
        
        if len(variations) >= limit:
            break
    
    return list(variations)[:limit]

def is_valid_domain(domain: str) -> bool:
    """
    Check if a domain name is valid.
    
    Args:
        domain: Domain name to validate
        
    Returns:
        bool: True if the domain is valid, False otherwise
    """
    if not domain or not isinstance(domain, str):
        return False
    
    # Basic regex for domain validation
    pattern = r'^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,}$'
    return bool(re.match(pattern, domain))
