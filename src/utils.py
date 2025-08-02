"""
Utility functions for validating and parsing GEDCOM tokens.
"""

from src import enums


def is_valid_level(token: str) -> bool:
    '''
    Checks if the provided token represents a valid GEDCOM level.

    A valid level is a string that consists of digits only and represents
    an integer between 0 and 99 (inclusive).

    Args:
        token (str): The string to check for validity as a GEDCOM level.

    Returns:
        bool: True if the token is a valid level, False otherwise.
    '''
    try:
        return token.isdigit() and int(token) >= 0 and int(token) <= 99
    except ValueError:
        return False


def is_cross_ref_id(token: str) -> bool:
    '''
    Checks if the given token is a cross-reference ID in GEDCOM format.

    A valid cross-reference ID starts and ends with the '@' character
    and has at least one character in between.

    Args:
        token (str): The string token to check.

    Returns:
        bool: True if the token is a cross-reference ID, False otherwise.
    '''
    return len(token) > 2 and token[0] == '@' and token[len(token)-1] == '@'


def is_valid_cross_ref_id(token: str) -> bool:
    '''
    Checks if the given token is a valid GEDCOM cross-reference ID.

    A valid cross-reference ID must:
    - Be longer than 2 characters.
    - Have only alphanumeric characters (excluding '@') between the first and last character.

    Args:
        token (str): The string token to validate.

    Returns:
        bool: True if the token is a valid cross-reference ID, False otherwise.
    '''
    if len(token) <= 2:
        return False
    for c in token[1:-1]:
        if not c.isalnum() or c == '@':
            return False
    return True


def is_obsolete_tag(token: str) -> bool:
    '''
    Checks if the given token is an obsolete GEDCOM tag.

    Args:
        token (str): The tag to check.

    Returns:
        bool: True if the token is an obsolete tag, False otherwise.
    '''
    return token in enums.ObsoleteTag._member_map_


def is_valid_tag(token: str) -> bool:
    '''
    Checks if the given token is a valid tag defined in the Tag enum.

    Args:
        token (str): The tag string to validate.

    Returns:
        bool: True if the token is a valid tag, False otherwise.
    '''
    return token in enums.Tag._member_map_


def is_user_defined_tag(token: str, allow_redefined: bool) -> bool:
    '''
    Determines if a given token is a user-defined GEDCOM tag.

    A user-defined tag must start with a single underscore, must not contain
    additional underscores, and must not conflict with predefined tags unless
    redefinition is allowed.

    Args:
        token (str): The tag token to check.
        allow_redefined (bool): Whether to allow user defined tags that are redefinitions of predefined tags.

    Returns:
        bool: True if the token is a valid user-defined tag, False otherwise.
    '''
    if not token:
        return False

    # First character must be an underscore
    if token[0] != '_':
        return False

    # Subsequent underscores are not valid
    if token[1:].count('_') > 0:
        return False

    # Redefined tags are not allowed
    if not allow_redefined and token.lstrip('_') in enums.Tag._member_map_:
        return False

    return True


def is_valid_line_value_token(token: str) -> bool: # pylint: disable=W0613
    '''
    Checks if the given token is a valid line value token.

    Args:
        token (str): The token to validate.

    Returns:
        bool: True if the token is a valid line value token, False otherwise.
    '''
    return True


def is_surname(token: str) -> bool:
    '''
    Checks if the given token represents a surname in GEDCOM format.

    A surname in GEDCOM is typically enclosed within forward slashes (e.g., /Smith/).

    Args:
        token (str): The string token to check.

    Returns:
        bool: True if the token starts and ends with '/',
        and is longer than one character; False otherwise.
    '''
    return len(token) > 1 and token[0] == '/' and token[len(token)-1] == '/'
