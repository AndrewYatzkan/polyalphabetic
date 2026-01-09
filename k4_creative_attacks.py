#!/usr/bin/env python3
"""
K4 Creative Attacks

Try unconventional approaches:
1. Interrupted key cipher (skip certain positions)
2. Letter-dependent key selection
3. Position-dependent alphabet shifts
4. Bifid/trifid hybrid approaches
5. Check if BERLINCLOCK hint might be misleading
"""

import itertools
from collections import Counter
import string

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def decrypt_char(ct, key, alpha):
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

def derive_key(ct, pt, alpha):
    return alpha[(alpha.index(ct) - alpha.index(pt)) % len(alpha)]

print("="*70)
print("K4 CREATIVE ATTACKS")
print("="*70)

# APPROACH 1: Interrupted Key
print("\n" + "="*70)
print("INTERRUPTED KEY CIPHER")
print("="*70)
print("Theory: Some positions might use a different key or be skipped")

# What if the key is applied with interruptions?
# E.g., every Nth position uses a different rule

base_keys = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'KOMITET']

for base_key in base_keys:
    for interrupt_every in [2, 3, 4, 5, 7]:
        for interrupt_shift in [1, 2, 13, -1]:
            pt = ''
            key_idx = 0
            for i, c in enumerate(K4):
                if i % interrupt_every == 0:
                    # Interrupted position - apply different shift
                    key_char = base_key[key_idx % len(base_key)]
                    key_val = (KRYPTOS_ALPHA.index(key_char) + interrupt_shift) % 26
                    pt += KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(c) - key_val) % 26]
                else:
                    # Normal position
                    key_char = base_key[key_idx % len(base_key)]
                    pt += decrypt_char(c, key_char, KRYPTOS_ALPHA)
                key_idx += 1

            if 'BERLIN' in pt or 'NORTHEAST' in pt or 'CLOCK' in pt:
                print(f"Key={base_key}, interrupt_every={interrupt_every}, shift={interrupt_shift}")
                print(f"  {pt}")

# APPROACH 2: Letter-Dependent Key
print("\n" + "="*70)
print("LETTER-DEPENDENT KEY")
print("="*70)
print("Theory: Key character depends on plaintext or ciphertext letter")

# What if key[i] depends on ct[i-1] or some previous character?
for alpha in [KRYPTOS_ALPHA]:
    for lag in [1, 2, 3]:
        for base_key in ['KRYPTOS', 'PALIMPSEST']:
            pt = []
            for i, c in enumerate(K4):
                if i < lag:
                    # Use base key for first few characters
                    key_char = base_key[i % len(base_key)]
                else:
                    # Key depends on previous ciphertext
                    prev_ct = K4[i - lag]
                    key_val = (alpha.index(base_key[i % len(base_key)]) + alpha.index(prev_ct)) % len(alpha)
                    key_char = alpha[key_val]

                pt.append(decrypt_char(c, key_char, alpha))

            plaintext = ''.join(pt)
            if 'BERLIN' in plaintext or 'NORTHEAST' in plaintext:
                print(f"Lag={lag}, base_key={base_key}: {plaintext[:50]}...")

# APPROACH 3: Polybius Square / Bifid Variant
print("\n" + "="*70)
print("POLYBIUS / BIFID VARIANT")
print("="*70)

# Create KRYPTOS Polybius square (5x5, combining I/J)
def create_polybius(keyword):
    """Create a Polybius square from keyword."""
    # KRYPTOS has 26 letters (including separate I and J? Or 25?)
    # Standard is 25 letters (I=J)
    alpha = ""
    for c in keyword:
        if c not in alpha:
            alpha += c
    for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":  # No J
        if c not in alpha:
            alpha += c
    return alpha

def polybius_coords(char, square):
    """Get row,col coordinates in Polybius square."""
    if char == 'J':
        char = 'I'
    idx = square.index(char)
    return idx // 5, idx % 5

def coords_to_char(row, col, square):
    """Convert coordinates back to character."""
    return square[row * 5 + col]

# Try Bifid cipher
square = create_polybius("KRYPTOS")
print(f"Polybius square: {square}")

# Bifid decryption attempt
def bifid_decrypt(ciphertext, square, period=None):
    """Decrypt using Bifid cipher."""
    # Get coordinates
    coords = []
    for c in ciphertext:
        if c == 'J':
            c = 'I'
        if c in square:
            r, c_coord = polybius_coords(c, square)
            coords.append((r, c_coord))

    if not coords:
        return ""

    if period is None:
        period = len(coords)

    # Process in period-sized blocks
    plaintext = ''
    for start in range(0, len(coords), period):
        block = coords[start:start + period]

        # Split rows and columns
        rows = [r for r, c in block]
        cols = [c for r, c in block]

        # Recombine (this is the bifid transformation)
        combined = rows + cols
        for i in range(0, len(combined), 2):
            if i + 1 < len(combined):
                r, c = combined[i], combined[i + 1]
                r, c = r % 5, c % 5
                plaintext += coords_to_char(r, c, square)

    return plaintext

for period in [5, 7, 11, 97]:
    pt = bifid_decrypt(K4, square, period)
    if pt and ('BERLIN' in pt or 'NORTHEAST' in pt or 'CLOCK' in pt):
        print(f"Bifid period={period}: {pt}")
    elif pt:
        print(f"Bifid period={period}: {pt[:40]}...")

# APPROACH 4: Re-examine the BERLINCLOCK hint
print("\n" + "="*70)
print("RE-EXAMINING BERLINCLOCK HINT")
print("="*70)
print("Theory: What if positions are 0-indexed instead of 1-indexed?")

# Sanborn said characters 64-69 = NYPVTT = BERLIN
# What if he meant 0-indexed? Then it's positions 64-69 (0-indexed)
for offset in range(-3, 4):
    bc_start = 63 + offset  # Try nearby positions
    if 0 <= bc_start <= len(K4) - 11:
        segment = K4[bc_start:bc_start+11]
        print(f"Position {bc_start}: {segment}")

        # Derive key for this position
        target = "BERLINCLOCK"
        key_chars = []
        for ct, pt in zip(segment, target):
            key_chars.append(derive_key(ct, pt, KRYPTOS_ALPHA))
        print(f"  Key would be: {''.join(key_chars)}")

# APPROACH 5: What if K4 uses K1/K2/K3 plaintexts somehow?
print("\n" + "="*70)
print("USING PREVIOUS SOLUTIONS AS KEY")
print("="*70)

K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONX"

# Try K1 plaintext as running key
print("\nUsing K1 plaintext as key...")
for offset in range(-20, 20):
    pt = ''
    for i, c in enumerate(K4):
        key_idx = i + offset
        if 0 <= key_idx < len(K1_PT):
            key_char = K1_PT[key_idx]
            if key_char in KRYPTOS_ALPHA:
                pt += decrypt_char(c, key_char, KRYPTOS_ALPHA)
            else:
                pt += '?'
        else:
            pt += '?'

    if 'BERLIN' in pt or 'NORTHEAST' in pt:
        print(f"K1 offset {offset}: {pt}")

# APPROACH 6: Simple substitution check
print("\n" + "="*70)
print("SIMPLE SUBSTITUTION CHECK")
print("="*70)
print("Theory: What if part of K4 is simple substitution?")

# Frequency analysis
freq = Counter(K4)
print("\nK4 frequencies:")
for c, count in freq.most_common():
    print(f"  {c}: {count}")

# In English: E T A O I N S H R
# K4: K(8) U(6) S(6) T(6) O(5) B(5) W(5)

# Try simple substitution where K=E, etc.
simple_sub = {
    'K': 'E', 'U': 'T', 'S': 'A', 'T': 'O', 'O': 'I',
    'B': 'N', 'W': 'S', 'R': 'H', 'G': 'R', 'L': 'D'
}

sub_pt = ''
for c in K4:
    sub_pt += simple_sub.get(c, c.lower())
print(f"\nSimple frequency sub: {sub_pt}")

# APPROACH 7: Check if K4 contains an anagram
print("\n" + "="*70)
print("ANAGRAM CHECK")
print("="*70)

k4_letters = Counter(K4)
print(f"K4 letter counts: {dict(k4_letters)}")
print(f"Total letters: {sum(k4_letters.values())}")

# Could this be an anagram of something meaningful?
# 97 letters - that's a lot for an anagram

print("\n" + "="*70)
print("CREATIVE ATTACKS COMPLETE")
print("="*70)
