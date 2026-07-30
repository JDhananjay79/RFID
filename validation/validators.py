"""Validation functions for RFID UI field entries."""

TAG_ID_PLACEHOLDER = "(Alphanumeric: Max 24 Characters)"
SERIAL_PLACEHOLDER = "(Alphanumeric: Max 16 characters)"
VIN_PLACEHOLDER = "(Alphanumeric: Max 17 Characters)"
AXLE_PLACEHOLDER = "(Numeric: 0 to 65535)"
GVW_PLACEHOLDER = "(Numeric: 0 to 4294967295)"
REGISTRATION_PLACEHOLDER = "(Alphanumeric: Max 12 Characters)"


def is_tag_id_valid(value: str) -> bool:
    return len(value) <= 24 and value.isalnum()


def validate_tag_id_entry(new_value: str) -> bool:
    if new_value == "" or new_value == TAG_ID_PLACEHOLDER:
        return True
    return len(new_value) <= 24 and new_value.isalnum()


def is_serial_valid(value: str) -> bool:
    return len(value) == 16 and value.isalnum()


def validate_serial_entry(new_value: str) -> bool:
    if new_value == "" or new_value == SERIAL_PLACEHOLDER:
        return True
    return len(new_value) <= 16 and new_value.isalnum()


def is_vin_valid(value: str) -> bool:
    return len(value) == 17 and value.isalnum()


def validate_vin_entry(new_value: str) -> bool:
    if new_value == "" or new_value == VIN_PLACEHOLDER:
        return True
    return len(new_value) <= 17 and new_value.isalnum()


def is_registration_valid(value: str) -> bool:
    return len(value) == 12 and value.isalnum()


def validate_registration_entry(new_value: str) -> bool:
    if new_value == "" or new_value == REGISTRATION_PLACEHOLDER:
        return True
    return len(new_value) <= 12 and new_value.isalnum()


def is_integer_in_range(value: str, min_value: int, max_value: int) -> bool:
    if not value.isdigit():
        return False
    try:
        numeric = int(value)
        return min_value <= numeric <= max_value
    except ValueError:
        return False


def validate_numeric_range_entry(new_value: str, max_digits: str | int = 10) -> bool:
    if new_value == "" or new_value in (AXLE_PLACEHOLDER, GVW_PLACEHOLDER):
        return True
    try:
        max_d = int(max_digits)
    except (ValueError, TypeError):
        max_d = 10
    return len(new_value) <= max_d and new_value.isdigit()
