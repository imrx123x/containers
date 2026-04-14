from app.exceptions import ValidationError


def parse_int(value, default: int, field_name: str):
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be an integer",
            code=f"{field_name}_invalid",
        )


def parse_positive_int(
    value,
    default: int,
    field_name: str,
    min_value: int = 1,
    max_value: int | None = None,
):
    number = parse_int(value, default, field_name)

    if number < min_value:
        return min_value

    if max_value is not None and number > max_value:
        return max_value

    return number