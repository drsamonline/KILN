"""Ed25519, in the standard library only.

A licence key must verify on a machine with no packages and no network, so the
signature check cannot depend on `cryptography`. This is the reference
construction from RFC 8032, written plainly: slow, correct, and tested against
the RFC's own vector in tests/test_licence.py.

Signing happens on the owner's machine, once per licence. Verification happens
at build time, on any machine.
"""
from __future__ import annotations

import hashlib

b = 256
q = 2 ** 255 - 19
l = 2 ** 252 + 27742317777372353535851937790883648493


def H(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def _bit(h: bytes, i: int) -> int:
    return (h[i // 8] >> (i % 8)) & 1


def _inv(x: int) -> int:
    return pow(x, q - 2, q)


_d = -121665 * _inv(121666) % q
_I = pow(2, (q - 1) // 4, q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(_d * y * y + 1)
    x = pow(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * _I) % q
    if x % 2 != 0:
        x = q - x
    return x


_By = 4 * _inv(5) % q
_Bx = _xrecover(_By)
_B = (_Bx % q, _By % q, 1, (_Bx * _By) % q)


def _edwards_add(P, Q):
    x1, y1, z1, t1 = P
    x2, y2, z2, t2 = Q
    a = (y1 - x1) * (y2 - x2) % q
    b_ = (y1 + x1) * (y2 + x2) % q
    c = t1 * 2 * _d * t2 % q
    dd = z1 * 2 * z2 % q
    e = b_ - a
    f = dd - c
    g = dd + c
    h = b_ + a
    return (e * f % q, g * h % q, f * g % q, e * h % q)


def _edwards_double(P):
    x1, y1, z1, _ = P
    a = x1 * x1 % q
    b_ = y1 * y1 % q
    c = 2 * z1 * z1 % q
    e = (x1 + y1) * (x1 + y1) % q - a - b_
    g = -a + b_
    f = g - c
    h = -a - b_
    return (e * f % q, g * h % q, f * g % q, e * h % q)


def _scalarmult(P, e: int):
    if e == 0:
        return (0, 1, 1, 0)
    Q = _scalarmult(P, e // 2)
    Q = _edwards_double(Q)
    if e & 1:
        Q = _edwards_add(Q, P)
    return Q


def _encodeint(y: int) -> bytes:
    return y.to_bytes(b // 8, "little")


def _encodepoint(P) -> bytes:
    x, y, z, _ = P
    zi = _inv(z)
    x, y = x * zi % q, y * zi % q
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8)) for i in range(b // 8))


def _decodepoint(s: bytes):
    y = int.from_bytes(s, "little") & ((1 << (b - 1)) - 1)
    x = _xrecover(y)
    if x & 1 != _bit(s, b - 1):
        x = q - x
    P = (x, y, 1, x * y % q)
    if not _isedwards(P):
        raise ValueError("point is not on the curve")
    return P


def _isedwards(P) -> bool:
    x, y, z, t = P
    return (x * y) % q == (z * t) % q and \
        (y * y - x * x - z * z - _d * t * t) % q == 0


def _Hint(m: bytes) -> int:
    h = H(m)
    return sum(2 ** i * _bit(h, i) for i in range(2 * b))


def public_key(secret: bytes) -> bytes:
    """32-byte secret -> 32-byte public key."""
    if len(secret) != 32:
        raise ValueError("secret key must be 32 bytes")
    h = H(secret)
    a = 2 ** (b - 2) + sum(2 ** i * _bit(h, i) for i in range(3, b - 2))
    return _encodepoint(_scalarmult(_B, a))


def sign(message: bytes, secret: bytes, pub: bytes | None = None) -> bytes:
    pub = pub or public_key(secret)
    h = H(secret)
    a = 2 ** (b - 2) + sum(2 ** i * _bit(h, i) for i in range(3, b - 2))
    r = _Hint(bytes(h[i] for i in range(b // 8, b // 4)) + message)
    R = _scalarmult(_B, r)
    S = (r + _Hint(_encodepoint(R) + pub + message) * a) % l
    return _encodepoint(R) + _encodeint(S)


def verify(signature: bytes, message: bytes, pub: bytes) -> bool:
    if len(signature) != 64 or len(pub) != 32:
        return False
    try:
        R = _decodepoint(signature[:b // 8])
        A = _decodepoint(pub)
    except ValueError:
        return False
    S = int.from_bytes(signature[b // 8:], "little")
    if S >= l:
        return False
    h = _Hint(_encodepoint(R) + pub + message)
    # compare the canonical encoding, not the projective tuple: two equal points
    # can carry different Z values
    return _encodepoint(_scalarmult(_B, S)) == \
        _encodepoint(_edwards_add(R, _scalarmult(A, h)))
