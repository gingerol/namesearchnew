"""Password hashing, verification, and strength checking utilities."""
import re
import logging
from typing import List, Optional, Tuple

from passlib.context import CryptContext
from passlib.pwd import genword

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    # Increase the default number of rounds for password hashing
    bcrypt__rounds=14,  # ~100ms on a modern CPU (2023)
)

# Common passwords to prevent (top 1000 most common passwords)
COMMON_PASSWORDS = set([
    "password", "123456", "12345678", "1234", "qwerty", "12345", "dragon",
    # Add more common passwords as needed
])

# Password strength requirements
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPER = True
PASSWORD_REQUIRE_LOWER = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/\"'`~"  # noqa: B028

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash with constant-time comparison.
    
    Args:
        plain_password: The plain text password.
        hashed_password: The hashed password.
        
    Returns:
        bool: True if the password is valid, False otherwise.
        
    Note:
        This function uses a constant-time comparison to prevent timing attacks.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Log the error but don't expose details to the user
        logger.warning(f"Password verification error: {str(e)}")
        # Still hash the password to maintain constant time
        pwd_context.hash(plain_password)
        return False

def get_password_hash(password: str) -> str:
    """
    Generate a secure password hash.
    
    Args:
        password: The plain text password.
        
    Returns:
        str: The hashed password.
        
    Raises:
        ValueError: If the password is empty or too long.
    """
    if not password:
        raise ValueError("Password cannot be empty")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(f"Password is too long (max {PASSWORD_MAX_LENGTH} characters)")
    
    return pwd_context.hash(password)


def validate_password_strength(password: str, user_inputs: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate password strength and return a list of issues.
    
    Args:
        password: The password to validate.
        user_inputs: Optional list of user inputs (like username, email) to check against.
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, issues) where issues is a list of problems.
    """
    issues = []
    
    # Check minimum length
    if len(password) < PASSWORD_MIN_LENGTH:
        issues.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    
    # Check maximum length
    if len(password) > PASSWORD_MAX_LENGTH:
        issues.append(f"Password must be at most {PASSWORD_MAX_LENGTH} characters long")
    
    # Check for common patterns
    if password.lower() in COMMON_PASSWORDS:
        issues.append("Password is too common")
    
    # Check for user inputs in password
    if user_inputs:
        for user_input in user_inputs:
            if user_input and len(user_input) > 2 and user_input.lower() in password.lower():
                issues.append("Password should not contain personal information")
                break
    
    # Check character requirements
    if PASSWORD_REQUIRE_UPPER and not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    
    if PASSWORD_REQUIRE_LOWER and not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    
    if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")
    
    if PASSWORD_REQUIRE_SPECIAL and not any(c in PASSWORD_SPECIAL_CHARS for c in password):
        issues.append(f"Password must contain at least one special character: {PASSWORD_SPECIAL_CHARS}")
    
    # Check for sequential or repeated characters
    if re.search(r'(.)\1{2,}', password):
        issues.append("Password contains too many repeated characters")
    
    # Check for common patterns (e.g., 12345, abcde, qwerty)
    common_patterns = [
        r'12345', r'67890', r'qwerty', r'asdfg', r'zxcvb',
        r'qazwsx', r'1q2w3e', r'1qaz2wsx', r'!@#$%^',
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            issues.append("Password contains a common pattern")
            break
    
    return (len(issues) == 0, issues)


def generate_strong_password(length: int = 16) -> str:
    """
    Generate a strong, memorable password.
    
    Args:
        length: Desired length of the password.
        
    Returns:
        str: A strong password.
    """
    if length < 12:
        raise ValueError("Password length must be at least 12 characters")
    
    # Generate a password with a mix of character types
    while True:
        # Use passlib's word generator for better memorability
        password = genword(length=length, charset="ascii_72")
        
        # Ensure it meets our strength requirements
        is_strong, _ = validate_password_strength(password)
        if is_strong:
            return password


def is_password_breached(password: str) -> bool:
    """
    Check if a password has been exposed in known data breaches.
    
    Note: In a real implementation, this would call an external service like
    Have I Been Pwned's API. This is a placeholder implementation.
    
    Args:
        password: The password to check.
        
    Returns:
        bool: True if the password is known to be compromised.
    """
    # In a real implementation, this would make an API call to check the password
    # against known breaches. For example, using the k-anonymity model:
    # https://haveibeenpwned.com/API/v3#PwnedPasswords
    # 
    # For now, we'll just check against our list of common passwords
    return password.lower() in COMMON_PASSWORDS
