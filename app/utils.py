import re

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def normalize_email(email_value):
    if email_value is None:
        return None

    email = email_value.strip().lower()

    if not email:
        return None

    if not EMAIL_REGEX.match(email):
        return None

    return email