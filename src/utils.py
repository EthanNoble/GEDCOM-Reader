import src.enums as enums

def is_valid_level(token: str) -> bool:
    if token.isdigit():
        try:
            level: int = int(token)
            return level >= 0 and level <= 99
        except ValueError:
            return False
    else:
        return False

def is_cross_ref_id(token: str) -> bool:
    return len(token) > 2 and token[0] == '@' and token[len(token)-1] == '@'

def is_valid_cross_ref_id(token: str) -> bool:
    if len(token) <= 2:
        return False
    for c in token[1:-1]:
        if not c.isalnum() or c == '@':
            return False
    return True

def is_obsolete_tag(token: str) -> bool:
    return token in enums.ObsoleteTag._member_map_

def is_valid_tag(token: str) -> bool:
    return token in enums.Tag._member_map_

def is_user_defined_tag(token: str, allow_redefined: bool) -> bool:
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

def is_valid_line_value_token(token: str) -> bool:
    return True # TODO: Implement

def is_surname(token: str) -> bool:
    return len(token) > 1 and token[0] == '/' and token[len(token)-1] == '/'
