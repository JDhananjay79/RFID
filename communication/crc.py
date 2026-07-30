"""CRC-16/CCITT-FALSE implementation (poly=0x1021, init=0xFFFF)."""


def compute_crc16_ccitt_false(data: bytes) -> int:
    """
    Compute 16-bit CRC-16/CCITT-FALSE over `data`.
    Polynomial: 0x1021
    Initial value: 0xFFFF
    Reflect In/Out: False
    XOR Out: 0x0000
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF


def crc_to_bytes(crc: int, big_endian: bool = True) -> bytes:
    """Serialise a 16-bit CRC integer to 2 bytes."""
    return crc.to_bytes(2, "big" if big_endian else "little")
