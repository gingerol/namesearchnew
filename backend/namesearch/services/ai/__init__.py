"""AI services for domain name analysis and generation."""

# Import key components for easier access
from .linguistic_analyzer import analyze_domain_name, count_syllables
from .brand_analyzer import analyze_brand_archetype, get_brand_archetype

__all__ = [
    'analyze_domain_name',
    'count_syllables',
    'analyze_brand_archetype',
    'get_brand_archetype'
]
