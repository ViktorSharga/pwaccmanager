"""Input validation utilities"""


def validate_login(login: str) -> tuple[bool, str]:
    """Validate login field"""
    if not login:
        return False, "Login is required"
    
    if len(login) < 3:
        return False, "Login must be at least 3 characters"
    
    if len(login) > 50:
        return False, "Login must be less than 50 characters"
    
    # Check for invalid characters
    if not all(c.isalnum() or c in '_-.' for c in login):
        return False, "Login can only contain letters, numbers, _, -, and ."
    
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password field"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 1:
        return False, "Password cannot be empty"
    
    if len(password) > 100:
        return False, "Password is too long"
    
    return True, ""


def validate_character_name(name: str) -> tuple[bool, str]:
    """Validate character name field (optional)"""
    if not name:  # Optional field
        return True, ""
    
    if len(name) > 50:
        return False, "Character name is too long"
    
    return True, ""


def validate_description(desc: str) -> tuple[bool, str]:
    """Validate description field (optional)"""
    if len(desc) > 200:
        return False, "Description is too long (max 200 characters)"
    
    return True, ""


def validate_owner(owner: str) -> tuple[bool, str]:
    """Validate owner field (optional)"""
    if len(owner) > 50:
        return False, "Owner name is too long (max 50 characters)"
    
    return True, ""