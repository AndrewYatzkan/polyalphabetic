#!/usr/bin/env python3
"""
K4 Transposition Analysis

What if K4 involves transposition before/after substitution?
Try various transposition patterns to see if any reveals structure.
"""

import itertools
from collections import Counter
import math

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def calc_ioc(text):
    """Calculate Index of Coincidence."""
    freq = Counter(text)
    n = len(text)
    if n <= 1:
        return 0
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def decrypt_vigenere(ct, key, alpha=KRYPTOS_ALPHA):
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        result.append(alpha[(alpha.index(c) - alpha.index(k)) % len(alpha)])
    return ''.join(result)

def reverse_string(s):
    return s[::-1]

def rail_fence_decrypt(ct, rails):
    """Rail fence decryption."""
    if rails < 2:
        return ct
    n = len(ct)
    pattern = []
    for i in range(n):
        cycle = 2 * (rails - 1)
        pos = i % cycle
        rail = pos if pos < rails else cycle - pos
        pattern.append((rail, i))
    pattern.sort()

    result = [''] * n
    ct_idx = 0
    for rail, orig_idx in pattern:
        result[orig_idx] = ct[ct_idx]
        ct_idx += 1
    return ''.join(result)

def columnar_decrypt(ct, key_order):
    """Columnar transposition decryption."""
    cols = len(key_order)
    rows = math.ceil(len(ct) / cols)

    # Determine column lengths
    full_cols = len(ct) % cols or cols
    col_lens = []
    for i in range(cols):
        if i < full_cols:
            col_lens.append(rows)
        else:
            col_lens.append(rows - 1)

    # Read columns in key order
    columns = {}
    pos = 0
    for col_idx in key_order:
        col_len = col_lens[col_idx]
        columns[col_idx] = ct[pos:pos + col_len]
        pos += col_len

    # Read off row by row
    result = []
    for row in range(rows):
        for col in range(cols):
            if row < len(columns[col]):
                result.append(columns[col][row])

    return ''.join(result)

print("="*70)
print("K4 TRANSPOSITION ANALYSIS")
print("="*70)

print(f"\nOriginal K4: {K4}")
print(f"Length: {len(K4)}")
print(f"IoC: {calc_ioc(K4):.4f}")

# Factor analysis - 97 is prime!
print("\n97 is PRIME - no rectangular transposition possible!")

# Try rail fence
print("\n" + "="*70)
print("RAIL FENCE ANALYSIS")
print("="*70)

for rails in range(2, 15):
    decrypted = rail_fence_decrypt(K4, rails)
    ioc = calc_ioc(decrypted)

    # Check if BERLIN or CLOCK appears after decryption
    has_crib = 'BERLIN' in decrypted or 'CLOCK' in decrypted

    if has_crib or ioc > 0.05:
        print(f"Rails {rails}: IoC={ioc:.4f}")
        print(f"  {decrypted[:50]}...")
        if has_crib:
            print("  *** Contains BERLIN or CLOCK! ***")

# Try reverse
print("\n" + "="*70)
print("REVERSE ANALYSIS")
print("="*70)

reversed_k4 = reverse_string(K4)
print(f"Reversed: {reversed_k4}")

# Try Vigenere on reversed text
for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA']:
    pt = decrypt_vigenere(reversed_k4, key)
    if 'BERLIN' in pt or 'CLOCK' in pt:
        print(f"Reversed + Vigenere({key}): {pt}")

# Try columnar with small keys
print("\n" + "="*70)
print("COLUMNAR TRANSPOSITION ANALYSIS")
print("="*70)

# 97 is prime, so we can only do 1x97 or 97x1
# But we can try with padding
padded_k4 = K4 + "X" * 3  # 100 chars = 10x10, 5x20, etc.

print("Padded to 100 characters for columnar analysis...")

for cols in [5, 10, 20, 4, 25]:
    rows = 100 // cols
    print(f"\n{rows}x{cols} grid:")

    # Try reading in different patterns
    # Simple columnar (read columns top-to-bottom, then arrange by key)
    for key_perm in itertools.permutations(range(cols)):
        if cols > 5:
            break  # Too many permutations for larger keys

        decrypted = columnar_decrypt(padded_k4, list(key_perm))
        if 'BERLIN' in decrypted or 'CLOCK' in decrypted or 'NORTHEAST' in decrypted:
            print(f"  Key order {key_perm}: Contains crib!")
            print(f"  {decrypted}")

# What if there's a route cipher?
print("\n" + "="*70)
print("SPECIAL PATTERNS")
print("="*70)

# Try interleaving odd/even positions
odd_chars = K4[::2]
even_chars = K4[1::2]
interleaved = even_chars + odd_chars

print(f"Odd+Even interleave: {interleaved[:50]}...")

# Try splitting into halves
half1 = K4[:49]
half2 = K4[49:]
merged = ''.join(a + b for a, b in zip(half1, half2)) + half2[48:]
print(f"Half interleave: {merged[:50]}...")

# What about K3? It used transposition with keyword KRYPTOS
# Let's try that pattern on K4
print("\n" + "="*70)
print("K3-STYLE TRANSPOSITION")
print("="*70)

# K3 used transposition with KRYPTOS keyword
# KRYPTOS = 4,5,6,3,7,2,1 (alphabetic ordering)
# Wait, actually K3 used irregular transposition

# Try various columnar keys based on KRYPTOS
kryptos_order = [4, 5, 6, 3, 7, 2, 1]  # Possible ordering

print("Trying K3-style transposition patterns...")

# Skip - 97 doesn't divide evenly

print("\n" + "="*70)
print("MASKING ANALYSIS")
print("="*70)

# What if certain positions are "dummy" characters?
# Remove every Nth character and see if structure emerges

for skip in [2, 3, 4, 5, 7, 11]:
    masked = ''.join(c for i, c in enumerate(K4) if i % skip != 0)
    ioc = calc_ioc(masked)
    print(f"Skip every {skip}th: len={len(masked)}, IoC={ioc:.4f}")

    if 'BERLIN' in masked or 'CLOCK' in masked:
        print(f"  Contains crib! {masked}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
