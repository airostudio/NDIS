"""
Validation Utilities
Validators for Australian/NDIS specific data
"""

import re
from typing import Optional
import phonenumbers


def validate_email(email: str) -> bool:
    """
    Validate email address format

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str, region: str = "AU") -> bool:
    """
    Validate Australian phone number

    Args:
        phone: Phone number to validate
        region: Country region code (default AU)

    Returns:
        True if valid phone number
    """
    try:
        parsed = phonenumbers.parse(phone, region)
        return phonenumbers.is_valid_number(parsed)
    except Exception:
        return False


def validate_abn(abn: str) -> bool:
    """
    Validate Australian Business Number (ABN)

    Args:
        abn: ABN to validate (11 digits)

    Returns:
        True if valid ABN
    """
    # Remove spaces and dashes
    abn = re.sub(r'[\s-]', '', abn)

    # Check length
    if len(abn) != 11 or not abn.isdigit():
        return False

    # ABN validation algorithm
    weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    # Subtract 1 from first digit
    digits = [int(d) for d in abn]
    digits[0] -= 1

    # Apply weights and sum
    weighted_sum = sum(d * w for d, w in zip(digits, weights))

    # Valid if divisible by 89
    return weighted_sum % 89 == 0


def validate_tfn(tfn: str) -> bool:
    """
    Validate Australian Tax File Number (TFN) format

    Args:
        tfn: TFN to validate (8 or 9 digits)

    Returns:
        True if valid TFN format
    """
    # Remove spaces and dashes
    tfn = re.sub(r'[\s-]', '', tfn)

    # Check length (8 or 9 digits)
    if not (len(tfn) in [8, 9] and tfn.isdigit()):
        return False

    # TFN checksum validation
    weights = [1, 4, 3, 7, 5, 8, 6, 9, 10]
    digits = [int(d) for d in tfn.ljust(9, '0')]

    weighted_sum = sum(d * w for d, w in zip(digits, weights))

    return weighted_sum % 11 == 0


def validate_ndis_number(ndis_number: str) -> bool:
    """
    Validate NDIS participant number format

    Args:
        ndis_number: NDIS number to validate

    Returns:
        True if valid NDIS number format
    """
    # NDIS number is typically 9 digits
    ndis_number = re.sub(r'[\s-]', '', ndis_number)

    return len(ndis_number) == 9 and ndis_number.isdigit()


def validate_medicare_number(medicare: str) -> bool:
    """
    Validate Medicare card number format

    Args:
        medicare: Medicare number to validate

    Returns:
        True if valid Medicare number format
    """
    # Medicare number is 10 digits (card number) + 1 digit (position on card)
    medicare = re.sub(r'[\s-]', '', medicare)

    if len(medicare) not in [10, 11] or not medicare.isdigit():
        return False

    # Basic checksum validation for 10-digit card number
    if len(medicare) >= 10:
        card_number = medicare[:10]
        weights = [1, 3, 7, 9, 1, 3, 7, 9]

        checksum = sum(int(d) * w for d, w in zip(card_number[:8], weights))
        check_digit = checksum % 10

        return int(card_number[8]) == check_digit

    return True


def validate_bsb(bsb: str) -> bool:
    """
    Validate Australian BSB (Bank State Branch) format

    Args:
        bsb: BSB to validate

    Returns:
        True if valid BSB format
    """
    # BSB is 6 digits, sometimes with hyphen after 3rd digit
    bsb = re.sub(r'[\s-]', '', bsb)

    return len(bsb) == 6 and bsb.isdigit()


def validate_super_fund_number(sfn: str) -> bool:
    """
    Validate Superannuation Fund Number format

    Args:
        sfn: Super fund number to validate

    Returns:
        True if valid format
    """
    # Remove spaces
    sfn = re.sub(r'\s', '', sfn)

    # Typical format is letters/numbers, varies by fund
    # Basic validation: 8-20 alphanumeric characters
    return 8 <= len(sfn) <= 20 and sfn.isalnum()


def validate_worker_screening_check(wsc: str) -> bool:
    """
    Validate NDIS Worker Screening Check number format

    Args:
        wsc: Worker screening check number

    Returns:
        True if valid format
    """
    # Format varies by state, but generally alphanumeric
    # Example NSW: WSC1234567
    wsc = re.sub(r'[\s-]', '', wsc)

    return 8 <= len(wsc) <= 15 and wsc.isalnum()
