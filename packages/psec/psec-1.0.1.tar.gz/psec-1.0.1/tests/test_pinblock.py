import pytest
from psec import pinblock


# fmt: off
@pytest.mark.parametrize(
    ["pin", "pan", "error"],
    [
        ("123", "55555555555555", "PIN must be between 4 and 12 digits long"),
        ("1234567890123", "55555555555555", "PIN must be between 4 and 12 digits long"),
        ("123A", "55555555555555", "PIN must be between 4 and 12 digits long"),
        ("1234", "555555555555", "PAN must be at least 13 digits long"),
        ("1234", "5555555555555A", "PAN must be at least 13 digits long"),
    ],
)
# fmt: on
def test_encode_pinblock_iso_0_exception(pin: str, pan: str, error: str) -> None:
    with pytest.raises(
        ValueError,
        match=error,
    ):
        pinblock.encode_pinblock_iso_0(pin, pan)


@pytest.mark.parametrize(
    ["pin", "pan", "pin_block"],
    [
        ("1234", "5555555551234567", "041261AAAAEDCBA9"),
        ("123456789012", "5555555551234567", "0C1261032D8226A9"),
    ],
)
def test_encode_pinblock_iso_0(pin: str, pan: str, pin_block: str) -> None:
    assert pin_block == pinblock.encode_pinblock_iso_0(pin, pan).hex().upper()


# fmt: off
@pytest.mark.parametrize(
    ["pin", "error"],
    [
        ("123", "PIN must be between 4 and 12 digits long"),
        ("1234567890123", "PIN must be between 4 and 12 digits long"),
        ("123A", "PIN must be between 4 and 12 digits long"),
    ],
)
# fmt: on
def test_encode_pinblock_iso_2_exception(pin: str, error: str) -> None:
    with pytest.raises(
        ValueError,
        match=error,
    ):
        pinblock.encode_pinblock_iso_2(pin)


@pytest.mark.parametrize(
    ["pin", "pin_block"],
    [
        ("1234", "241234FFFFFFFFFF"),
        ("123456789", "29123456789FFFFF"),
        ("1234567890", "2A1234567890FFFF"),
        ("123456789012", "2C123456789012FF"),
    ],
)
def test_encode_pinblock_iso_2(pin: str, pin_block: str) -> None:
    assert pin_block == pinblock.encode_pinblock_iso_2(pin).hex().upper()


# fmt: off
@pytest.mark.parametrize(
    ["pin", "pan", "error"],
    [
        ("123", "55555555555555", "PIN must be between 4 and 12 digits long"),
        ("1234567890123", "55555555555555", "PIN must be between 4 and 12 digits long"),
        ("123A", "55555555555555", "PIN must be between 4 and 12 digits long"),
        ("1234", "555555555555", "PAN must be at least 13 digits long"),
        ("1234", "5555555555555A", "PAN must be at least 13 digits long"),
    ],
)
# fmt: on
def test_encode_pinblock_iso_3_exception(pin: str, pan: str, error: str) -> None:
    with pytest.raises(
        ValueError,
        match=error,
    ):
        pinblock.encode_pinblock_iso_3(pin, pan)


@pytest.mark.parametrize(
    ["pin", "pan", "pin_block"],
    [
        ("1234", "5555555551234567", "341261"),
        ("123456789012", "5555555551234567", "3C1261032D8226"),
    ],
)
def test_encode_pinblock_iso_3(pin: str, pan: str, pin_block: str) -> None:
    assert (
        pin_block
        == pinblock.encode_pinblock_iso_3(pin, pan).hex().upper()[: 2 + len(pin)]
    )


# fmt: off
@pytest.mark.parametrize(
    ["pin_block", "pan", "error"],
    [
        (bytes.fromhex("241261AAAAEDCBA9"), "5555555551234567", "PIN block is not ISO format 0: control field `2`"),
        (bytes.fromhex("041261AAAAEDCB"), "5555555551234567", "PIN block must be 8 bytes long"),
        (bytes.fromhex("0F1261AAAAEDCBA9"), "5555555551234567", "PIN length must be between 4 and 12: `15`"),
        (bytes.fromhex("021261AAAAEDCBA9"), "5555555551234567", "PIN length must be between 4 and 12: `2`"),
        (bytes.fromhex("041261AAAAEDCBAA"), "5555555551234567", "PIN block filler is incorrect: `FFFFFFFFFC`"),
        (bytes.fromhex("051261AAAAEDCBA9"), "5555555551234567", "PIN is not numeric: `1234F`"),
        (bytes.fromhex("051261AAAAEDCBA9"), "555555555123", "PAN must be at least 13 digits long"),
        (bytes.fromhex("051261AAAAEDCBA9"), "5555555551234A", "PAN must be at least 13 digits long"),
    ],
)
# fmt: on
def test_decode_pinblock_iso_0_exception(
    pin_block: bytes, pan: str, error: str
) -> None:
    with pytest.raises(
        ValueError,
        match=error,
    ):
        pinblock.decode_pinblock_iso_0(pin_block, pan)


@pytest.mark.parametrize(
    ["pin", "pin_block", "pan"],
    [
        ("1234", bytes.fromhex("041261AAAAEDCBA9"), "5555555551234567"),
        ("123456789", bytes.fromhex("091261032D8DCBA9"), "5555555551234567"),
        ("1234567890", bytes.fromhex("0A1261032D82CBA9"), "5555555551234567"),
        ("123456789012", bytes.fromhex("0C1261032D8226A9"), "5555555551234567"),
    ],
)
def test_decode_pinblock_iso_0(pin: str, pin_block: bytes, pan: str) -> None:
    assert pin == pinblock.decode_pinblock_iso_0(pin_block, pan)


# fmt: off
@pytest.mark.parametrize(
    ["pin_block", "error"],
    [
        (bytes.fromhex("041234FFFFFFFFFF"), "PIN block is not ISO format 2: control field `0`"),
        (bytes.fromhex("29123456789FFF"), "PIN block must be 8 bytes long"),
        (bytes.fromhex("2F123456789012FF"), "PIN length must be between 4 and 12: `15`"),
        (bytes.fromhex("22123456789012FF"), "PIN length must be between 4 and 12: `2`"),
        (bytes.fromhex("2C123456789012CF"), "PIN block filler is incorrect: `CF`"),
        (bytes.fromhex("2C12345678901FFF"), "PIN is not numeric: `12345678901F`"),
    ],
)
# fmt: on
def test_decode_pinblock_iso_2_exception(pin_block: bytes, error: str) -> None:
    with pytest.raises(
        ValueError,
        match=error,
    ):
        pinblock.decode_pinblock_iso_2(pin_block)


@pytest.mark.parametrize(
    ["pin", "pin_block"],
    [
        ("1234", bytes.fromhex("241234FFFFFFFFFF")),
        ("123456789", bytes.fromhex("29123456789FFFFF")),
        ("1234567890", bytes.fromhex("2A1234567890FFFF")),
        ("123456789012", bytes.fromhex("2C123456789012FF")),
    ],
)
def test_decode_pinblock_iso_2(pin: str, pin_block: bytes) -> None:
    assert pin == pinblock.decode_pinblock_iso_2(pin_block)


# fmt: off
@pytest.mark.parametrize(
    ["pin_block", "pan", "error"],
    [
        (bytes.fromhex("241261AAAAEDCBA9"), "5555555551234567", "PIN block is not ISO format 3: control field `2`"),
        (bytes.fromhex("341261AAAAEDCB"), "5555555551234567", "PIN block must be 8 bytes long"),
        (bytes.fromhex("3F1261AAAAEDCBA9"), "5555555551234567", "PIN length must be between 4 and 12: `15`"),
        (bytes.fromhex("321261AAAAEDCBA9"), "5555555551234567", "PIN length must be between 4 and 12: `2`"),
        (bytes.fromhex("341261AAAAEDCBA2"), "5555555551234567", "PIN block filler is incorrect: `FFFFFFFFF4`"),
        (bytes.fromhex("351261AAAAEDCBA9"), "5555555551234567", "PIN is not numeric: `1234F`"),
        (bytes.fromhex("351261AAAAEDCBA9"), "555555555123", "PAN must be at least 13 digits long"),
        (bytes.fromhex("351261AAAAEDCBA9"), "5555555551234A", "PAN must be at least 13 digits long"),
    ],
)
# fmt: on
def test_decode_pinblock_iso_3_exception(
    pin_block: bytes, pan: str, error: str
) -> None:
    with pytest.raises(
        ValueError,
        match=error,
    ):
        pinblock.decode_pinblock_iso_3(pin_block, pan)


@pytest.mark.parametrize(
    ["pin", "pin_block", "pan"],
    [
        ("1234", bytes.fromhex("341261AAAAEDCBA9"), "5555555551234567"),
        ("123456789", bytes.fromhex("391261032D8DCBA9"), "5555555551234567"),
        ("1234567890", bytes.fromhex("3A1261032D82CBA9"), "5555555551234567"),
        ("123456789012", bytes.fromhex("3C1261032D8226A9"), "5555555551234567"),
    ],
)
def test_decode_pinblock_iso_3(pin: str, pin_block: bytes, pan: str) -> None:
    assert pin == pinblock.decode_pinblock_iso_3(pin_block, pan)
