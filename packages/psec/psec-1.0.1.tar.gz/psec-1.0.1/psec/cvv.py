import binascii as _binascii
import string as _string

from psec import des as _des
from psec import tools as _tools

__all__ = ["generate_cvv"]


def generate_cvv(
    cvk: bytes,
    pan: str,
    expiry: str,
    service_code: str,
) -> str:
    r"""Generate Visa/MasterCard Card Verification Value.

    Parameters
    ----------
    cvk : bytes
        16-byte binary card verification key. Has to be a valid Triple DES key.
    pan : str
        ASCII Primary Account Number.
    expiry : str
        ASCII PAN expiry date. It could be YYMM or MMYY depending on the issuer.
    service_code : str
        ASCII service code.

    Returns
    -------
    cvv : str
        Card Verification Value.

    Raises
    ------
    ValueError
        CVK must be a double length DES key
        PAN must be less than 19 digit
        PAN expiry must be 4 digits long
        Service code must be 3 digits long

    Notes
    -----
    Both MasterCard and Visa use the same card verification algorithm.
    MasterCard calls the resulting value Card Verification Code (CVC).
    Visa calls the resulting value Card Verification Value (CVV).

        - CVV encoded on a magnetic stripe is called CVV1. CVV1 is
          encoded using informtation from the track1/2 itself.
        - CVV printed on the back of a card is called CVV2. CVV2 is
          encoded using informtation from the track1/2 itself
          while using a service code different from magnetic stripe (e.g. 000).
        - CVV encoded on an EMV track2 equivalent is called Chip CVC or iCVV.
          'i' in iCVV stands for Integrated Card. iCVV is
          encoded using informtation from the EMV track1/2 itself
          while using a service code different from CVV1 and CVV2.
          Bottom line, CVV1, CVV2 and iCVV have to be different.

    Some cards employ dynamic CVV that changes with every transaction.
    Dynamic CVV is produced using a different algorithm.

    Examples
    --------
    >>> import psec
    >>> cvk = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    >>> psec.cvv.generate_cvv(cvk, "1234567890123456", "9912", "220")
    '170'
    """

    if len(cvk) != 16:
        raise ValueError("CVK must be a double length DES key")

    if len(pan) > 19 or not all(d in _string.digits for d in pan):
        raise ValueError("PAN must be less than 19 digits")

    if len(expiry) != 4 or not all(d in _string.digits for d in expiry):
        raise ValueError("PAN expiry must be 4 digits long")

    if len(service_code) != 3 or not all(d in _string.digits for d in service_code):
        raise ValueError("Service code must be 3 digits long")

    block = (pan + expiry + service_code).ljust(32, "0")
    result = _des.encrypt_tdes_ecb(cvk[:8], _binascii.a2b_hex(block[:16]))
    result = _tools.xor(result, _binascii.a2b_hex(block[16:]))
    result = _des.encrypt_tdes_ecb(cvk, result)
    return "".join(filter((lambda x: x in ("1234567890")), result.hex()))[:3]
