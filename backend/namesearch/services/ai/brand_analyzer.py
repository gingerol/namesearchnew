"""Brand analysis service for domain names."""
from typing import Dict, List, Optional, Tuple
import random
from dataclasses import dataclass

@dataclass
class BrandArchetype:
    """Represents a brand archetype with its characteristics."""
    name: str
    description: str
    traits: List[str]
    example_brands: List[str]
    keywords: List[str]

# Define common brand archetypes
BRAND_ARCHETYPES = [
    BrandArchetype(
        name="The Hero",
        description="Embodies courage, achievement, and determination. Motivates others to overcome obstacles.",
        traits=["bold", "determined", "inspiring", "achiever"],
        example_brands=["Nike", "BMW", "FedEx"],
        keywords=["achieve", "overcome", "power", "strength", "victory"]
    ),
    BrandArchetype(
        name="The Sage",
        description="Represents wisdom, knowledge, and truth. Helps people understand the world.",
        traits=["wise", "intelligent", "thoughtful", "analytical"],
        example_brands=["Google", "BBC", "HuffPost"],
        keywords=["knowledge", "wisdom", "insight", "truth", "expert"]
    ),
    BrandArchetype(
        name="The Explorer",
        description="Seeks freedom, adventure, and new experiences. Inspires discovery.",
        traits=["adventurous", "free-spirited", "independent", "daring"],
        example_brands=["The North Face", "Red Bull", "Patagonia"],
        keywords=["adventure", "discover", "explore", "freedom", "journey"]
    ),
    BrandArchetype(
        name="The Creator",
        description="Encourages innovation, imagination, and self-expression.",
        traits=["creative", "imaginative", "artistic", "visionary"],
        example_brands=["Lego", "Adobe", "Apple"],
        keywords=["create", "imagine", "design", "innovate", "build"]
    ),
    BrandArchetype(
        name="The Caregiver",
        description="Represents compassion, nurturing, and generosity. Protects and cares for others.",
        traits=["caring", "generous", "nurturing", "protective"],
        example_brands=["Pampers", "UNICEF", "Toms"],
        keywords=["care", "nurture", "protect", "help", "support"]
    )
]

def analyze_brand_archetype(domain: str) -> Dict[str, any]:
    """
    Analyze a domain name to determine its brand archetype.
    
    Args:
        domain: The domain name to analyze (without TLD)
        
    Returns:
        Dict containing archetype analysis results
    """
    # Simple keyword matching for demonstration
    # In production, this would use more sophisticated NLP
    domain_lower = domain.lower()
    
    # Initialize scores for each archetype
    scores = {archetype.name: 0 for archetype in BRAND_ARCHETYPES}
    
    # Score based on keyword matching
    for archetype in BRAND_ARCHETYPES:
        for keyword in archetype.keywords:
            if keyword in domain_lower:
                scores[archetype.name] += 1
    
    # Get top matches
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_archetype_name = sorted_scores[0][0]
    top_archetype = next(a for a in BRAND_ARCHETYPES if a.name == top_archetype_name)
    
    # Calculate confidence (0-1)
    total_keywords = sum(scores.values())
    confidence = scores[top_archetype_name] / max(1, total_keywords) if total_keywords > 0 else 0.1
    
    # If no keywords matched, return a random archetype with low confidence
    if total_keywords == 0:
        top_archetype = random.choice(BRAND_ARCHETYPES)
        confidence = 0.1
    
    return {
        'archetype': top_archetype.name,
        'description': top_archetype.description,
        'confidence': min(1.0, max(0.1, confidence)),
        'traits': top_archetype.traits,
        'example_brands': top_archetype.example_brands
    }

def get_brand_archetype(name: str) -> Optional[BrandArchetype]:
    """Get a brand archetype by name."""
    return next((a for a in BRAND_ARCHETYPES if a.name.lower() == name.lower()), None)
