from pydantic import validate_email


def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValueError:
        return False
