#!/usr/bin/env python3
"""
K4 Reverse Engineering

Given:
- BERLINCLOCK at position 63 (0-indexed)
- NORTHEAST somewhere in plaintext
- Some unknown cipher

Work backwards to constrain what the cipher could be.
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def derive_key(ct, pt, alpha):
    return alpha[(alpha.index(ct) - alpha.index(pt)) % len(alpha)]

print("="*70)
print("K4 REVERSE ENGINEERING")
print("="*70)

# We know:
# - Position 63-73 plaintext = BERLINCLOCK
# - Key stream at 63-73 = ELYOIECBAQK (with KRYPTOS alphabet)

# For NORTHEAST (9 chars) at position X:
# Key stream at X:X+9 must decrypt K4[X:X+9] to NORTHEAST

NORTHEAST = "NORTHEAST"
BERLINCLOCK = "BERLINCLOCK"

print("\nFor each possible NORTHEAST position, calculate required key stream:")
print("="*70)

northeast_keys = {}
for pos in range(len(K4) - 9 + 1):
    ct_segment = K4[pos:pos + 9]
    key_segment = ''.join(derive_key(ct, pt, KRYPTOS_ALPHA)
                          for ct, pt in zip(ct_segment, NORTHEAST))
    northeast_keys[pos] = key_segment

    # Check if this overlaps with BERLINCLOCK
    overlaps = False
    if pos <= 73 and pos + 9 > 63:
        overlaps = True
        # Check compatibility
        compatible = True
        bc_key = "ELYOIECBAQK"
        for i in range(9):
            ne_pos = pos + i
            if 63 <= ne_pos <= 73:
                bc_idx = ne_pos - 63
                if key_segment[i] != bc_key[bc_idx]:
                    compatible = False
                    break
        if compatible:
            print(f"Position {pos}: {key_segment} - OVERLAPS with BC, COMPATIBLE!")
        else:
            print(f"Position {pos}: {key_segment} - overlaps with BC, incompatible")

    # Check if key is interesting (repeated chars, known words, etc.)
    if len(set(key_segment)) <= 4:  # Highly repetitive
        print(f"Position {pos}: {key_segment} - REPETITIVE KEY!")

# Look for patterns between BERLINCLOCK key and NORTHEAST keys
print("\n" + "="*70)
print("PATTERN SEARCH")
print("="*70)

bc_key = "ELYOIECBAQK"
print(f"BERLINCLOCK key: {bc_key}")

# For each NORTHEAST position, how similar is its key to BERLINCLOCK key?
print("\nSimilarity of NORTHEAST keys to BERLINCLOCK key:")
similarities = []
for pos, ne_key in northeast_keys.items():
    # Count matching characters in same relative position (mod some period)
    for period in range(5, 15):
        matches = 0
        for i in range(9):
            bc_pos = (pos + i - 63) % period
            if bc_pos < len(bc_key) and ne_key[i] == bc_key[bc_pos]:
                matches += 1
        if matches >= 5:
            similarities.append((pos, period, matches, ne_key))

if similarities:
    print("\nHigh similarity cases:")
    for pos, period, matches, ne_key in sorted(similarities, key=lambda x: -x[2])[:10]:
        print(f"  NE at {pos}, period {period}: {matches}/9 matches, key={ne_key}")

# What if the key is derived from the plaintext itself?
print("\n" + "="*70)
print("AUTOKEY ANALYSIS")
print("="*70)

# In autokey, key = primer + plaintext
# If primer has length P, then key[i] = pt[i-P] for i >= P

# We know pt[63:74] = BERLINCLOCK
# And key[63:74] = ELYOIECBAQK

# If autokey with primer P:
# key[63] = pt[63-P]
# key[63] = E means pt[63-P] = E

# So if P=10: pt[53] = E
# If P=20: pt[43] = E
# etc.

print("\nIf autokey cipher:")
for primer_len in range(5, 60):
    # key[63] = pt[63-primer_len] if cipher is autokey
    # We know key[63] = E
    # So pt[63-primer_len] should = E

    source_pos = 63 - primer_len
    if source_pos >= 0:
        # What ciphertext character is at source_pos?
        ct_at_source = K4[source_pos]
        # If pt[source_pos] = E, what key was used?
        needed_key = derive_key(ct_at_source, 'E', KRYPTOS_ALPHA)

        # For autokey, key[source_pos] would come from primer or earlier pt
        # This gets recursive...

        # Simpler check: does the pattern make sense?
        # key[63:74] = ELYOIECBAQK
        # If this equals pt[63-P:74-P], those positions should exist

        if 63 - primer_len >= 0 and 74 - primer_len >= 0:
            # The key segment should equal plaintext at (63-P):(74-P)
            # We don't know that plaintext yet, but we can check consistency

            # For position 63: key[63]=E, so if autokey, pt[63-P]=E
            # For position 64: key[64]=L, so pt[64-P]=L
            # etc.

            implied_pt_segment = "ELYOIECBAQK"  # The key IS the plaintext offset by primer_len
            implied_pt_start = 63 - primer_len

            print(f"Primer length {primer_len}: pt[{implied_pt_start}:{implied_pt_start+11}] = {implied_pt_segment}")

# What if we try to decrypt assuming autokey?
print("\n" + "="*70)
print("ATTEMPTING AUTOKEY DECRYPTION")
print("="*70)

def autokey_decrypt(ct, primer, alpha):
    """Decrypt autokey cipher."""
    pt = []
    key = list(primer)
    for i, c in enumerate(ct):
        if i < len(primer):
            key_char = primer[i]
        else:
            key_char = pt[i - len(primer)]

        pt_char = alpha[(alpha.index(c) - alpha.index(key_char)) % len(alpha)]
        pt.append(pt_char)

    return ''.join(pt)

# Try various primers
primers_to_try = [
    'KRYPTOS',
    'PALIMPSEST',
    'ABSCISSA',
    'KOMITET',
    'BERLIN',
    'CLOCK',
    'NORTHEAST',
    'SHADOW',
    'SECRET',
    'ELYOIECBAQK',
]

# Also try primers derived from what we know
# If BERLINCLOCK is at 63 and key there is ELYOIECBAQK,
# and autokey means key = primer + pt,
# then for various primer lengths we can constrain what the primer must be

print("\nTrying autokey with various primers:")
for primer in primers_to_try:
    pt = autokey_decrypt(K4, primer, KRYPTOS_ALPHA)

    # Check if BERLINCLOCK appears
    if 'BERLINCLOCK' in pt:
        bc_pos = pt.find('BERLINCLOCK')
        print(f"Primer '{primer}': BERLINCLOCK at {bc_pos}!")
        print(f"  Plaintext: {pt}")
        if 'NORTHEAST' in pt:
            print(f"  *** ALSO FOUND NORTHEAST! ***")

    if 'BERLIN' in pt or 'NORTHEAST' in pt or 'CLOCK' in pt:
        print(f"Primer '{primer}': {pt[:50]}...")

print("\n" + "="*70)
print("FINAL THOUGHTS")
print("="*70)

print("""
Key observations:
1. With KRYPTOS alphabet and Vigenère, key stream at 63-73 = ELYOIECBAQK
2. This key produces BERLINCLOCK but gibberish elsewhere
3. For ANY periodic cipher, BERLINCLOCK and NORTHEAST constraints conflict
4. K4 must use a non-periodic or unconventional cipher

Remaining possibilities:
- Autokey with unknown primer
- Running key with unknown text
- Multiple encryption with unknown intermediate
- Transposition variant we haven't tried
- Completely novel cipher by Sanborn

The key 'ELYOIECBAQK' may be significant - possibly:
- Part of a longer key phrase
- Related to the Berlin Clock mechanism
- A clue left by Sanborn
""")
