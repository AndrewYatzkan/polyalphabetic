#!/usr/bin/env python3
"""
K4 Deep Analysis - Explore the partially decrypted text

We found that with key OIECBAQKELY (period 11, KRYPTOS alphabet):
- BERLINCLOCK appears correctly at position 63
- But the rest isn't readable English

This suggests:
1. Additional transposition layer
2. Key needs modification
3. Different cipher entirely with specific solution for BERLINCLOCK
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The key we derived
KEY_11 = "OIECBAQKELY"

# The decrypted text with this key
DECRYPTED = "KNIMGXTOYWNFNUVCBMBWSDFFEEFVANYCTRJNHVGFJCITSEHJIKDJIKNOKVHAFMBBERLINCLOCKFVBUDGUBYJIYCNCSVFPNIAJ"

print("="*70)
print("K4 DEEP ANALYSIS")
print("="*70)

print(f"\nOriginal K4: {K4}")
print(f"Derived key: {KEY_11}")
print(f"Decrypted:   {DECRYPTED}")
print(f"\nBERLINCLOCK at pos 63-73: {DECRYPTED[63:74]}")

# Analyze the decrypted text
print("\n" + "="*70)
print("STATISTICAL ANALYSIS OF DECRYPTED TEXT")
print("="*70)

# Frequency analysis
freq = Counter(DECRYPTED)
print("\nCharacter frequencies in decrypted text:")
for char, count in freq.most_common(10):
    pct = count / len(DECRYPTED) * 100
    print(f"  {char}: {count} ({pct:.1f}%)")

# Index of coincidence
n = len(DECRYPTED)
ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
print(f"\nIndex of Coincidence: {ic:.4f}")
print(f"  (English ~0.067, random ~0.038)")

# Look for patterns
print("\n" + "="*70)
print("PATTERN SEARCH IN DECRYPTED TEXT")
print("="*70)

# Look for repeated trigrams
trigrams = {}
for i in range(len(DECRYPTED) - 2):
    tri = DECRYPTED[i:i+3]
    if tri not in trigrams:
        trigrams[tri] = []
    trigrams[tri].append(i)

repeated = {t: p for t, p in trigrams.items() if len(p) > 1}
if repeated:
    print("\nRepeated trigrams:")
    for tri, positions in sorted(repeated.items(), key=lambda x: -len(x[1])):
        print(f"  '{tri}' at positions {positions}")

# Try transposition on the decrypted text
print("\n" + "="*70)
print("TRANSPOSITION ATTEMPTS ON DECRYPTED TEXT")
print("="*70)

def columnar_read(text, cols):
    """Read text in columns."""
    rows = (len(text) + cols - 1) // cols
    padded = text + 'X' * (rows * cols - len(text))
    result = ''
    for c in range(cols):
        for r in range(rows):
            idx = r * cols + c
            if idx < len(text):
                result += padded[idx]
    return result[:len(text)]

def columnar_unread(text, cols):
    """Reverse columnar read."""
    rows = (len(text) + cols - 1) // cols
    result = [''] * len(text)
    idx = 0
    for c in range(cols):
        for r in range(rows):
            pos = r * cols + c
            if pos < len(text) and idx < len(text):
                result[pos] = text[idx]
                idx += 1
    return ''.join(result)

for cols in range(5, 15):
    trans = columnar_read(DECRYPTED, cols)
    if 'NORTHEAST' in trans or 'THEEAST' in trans or 'EASTNO' in trans:
        print(f"Columnar read cols={cols}: {trans[:50]}...")
        print(f"  Full: {trans}")

    untrans = columnar_unread(DECRYPTED, cols)
    if 'NORTHEAST' in untrans or 'THEEAST' in untrans:
        print(f"Columnar unread cols={cols}: {untrans[:50]}...")

# Try rail fence
print("\n--- Rail Fence ---")
def rail_fence_decrypt(text, rails):
    """Decrypt rail fence cipher."""
    if rails <= 1:
        return text
    cycle = 2 * (rails - 1)
    result = [''] * len(text)

    idx = 0
    for rail in range(rails):
        if rail == 0 or rail == rails - 1:
            # Top and bottom rails
            for i in range(rail, len(text), cycle):
                if idx < len(text):
                    result[i] = text[idx]
                    idx += 1
        else:
            # Middle rails
            i = rail
            down = True
            while i < len(text):
                if idx < len(text):
                    result[i] = text[idx]
                    idx += 1
                if down:
                    i += 2 * (rails - 1 - rail)
                else:
                    i += 2 * rail
                down = not down
    return ''.join(result)

for rails in range(3, 10):
    rf = rail_fence_decrypt(DECRYPTED, rails)
    if 'NORTHEAST' in rf or 'BERLIN' in rf:
        print(f"Rails={rails}: {rf[:50]}...")

# Analyze the key itself
print("\n" + "="*70)
print("KEY ANALYSIS")
print("="*70)

print(f"\nDerived key: {KEY_11}")

# Is the key an anagram of something?
key_sorted = ''.join(sorted(KEY_11))
print(f"Key sorted: {key_sorted}")

# Common words that could be anagrams
words_11 = ['BERKELEYOLI', 'LIBERTYCODE', 'CYBERTOKILE']
print("\nPossible key meanings/anagrams:")
for word in words_11:
    if sorted(word) == sorted(KEY_11):
        print(f"  {KEY_11} could be anagram of {word}")

# Try different key orderings
print("\n--- Trying key permutations ---")
# Only try some permutations since 11! is huge
import random
random.seed(42)

# Try reversals and rotations
key_variations = [
    KEY_11[::-1],  # Reversed
    KEY_11[5:] + KEY_11[:5],  # Rotated
    KEY_11[3:] + KEY_11[:3],  # Rotated
]

for var in key_variations:
    # Decrypt with this key variation
    pt = ''
    for i, c in enumerate(K4):
        ct_pos = KRYPTOS_ALPHA.index(c)
        key_pos = KRYPTOS_ALPHA.index(var[i % 11])
        pt_pos = (ct_pos - key_pos) % len(KRYPTOS_ALPHA)
        pt += KRYPTOS_ALPHA[pt_pos]

    if 'NORTHEAST' in pt or 'THE' in pt:
        print(f"Key variation {var}: {pt[:50]}...")

# Try with NORTHEAST constraint
print("\n" + "="*70)
print("SEARCHING FOR NORTHEAST")
print("="*70)

# NORTHEAST is 9 characters
# If it appears in the plaintext, we can derive key constraints

print("\nSearching all positions where NORTHEAST could appear...")
for ne_start in range(len(K4) - 9 + 1):
    target = "NORTHEAST"
    ct_segment = K4[ne_start:ne_start + 9]

    # Calculate required key chars
    key_segment = ''
    for ct_c, pt_c in zip(ct_segment, target):
        ct_pos = KRYPTOS_ALPHA.index(ct_c)
        pt_pos = KRYPTOS_ALPHA.index(pt_c)
        key_val = (ct_pos - pt_pos) % len(KRYPTOS_ALPHA)
        key_segment += KRYPTOS_ALPHA[key_val]

    # Check if this is consistent with our derived key (period 11)
    consistent = True
    for i, kc in enumerate(key_segment):
        key_pos = (ne_start + i) % 11
        if KEY_11[key_pos] != kc:
            consistent = False
            break

    if consistent:
        print(f"  Position {ne_start}: key segment = {key_segment} - CONSISTENT!")
    elif ne_start < 20 or ne_start > 70:  # Show some examples
        # Check how close it is
        matches = sum(1 for i, kc in enumerate(key_segment)
                     if KEY_11[(ne_start + i) % 11] == kc)
        if matches >= 5:
            print(f"  Position {ne_start}: key segment = {key_segment} ({matches}/9 matches)")

# Maybe NORTHEAST is split by a transposition?
print("\n" + "="*70)
print("LOOKING FOR SPLIT NORTHEAST")
print("="*70)

# Check if N,O,R,T,H,E,A,S,T appear in decrypted text in some pattern
ne_chars = list("NORTHEAST")
ne_positions = []
for char in ne_chars:
    positions = [i for i, c in enumerate(DECRYPTED) if c == char]
    ne_positions.append((char, positions[:5]))  # First 5 occurrences

print("Positions of NORTHEAST letters in decrypted text:")
for char, positions in ne_positions:
    print(f"  {char}: {positions}")

# Check for arithmetic progressions
print("\nLooking for arithmetic progressions...")
for start in range(60):
    for step in range(1, 15):
        chars = ''
        for i in range(9):
            pos = start + i * step
            if pos < len(DECRYPTED):
                chars += DECRYPTED[pos]
        if chars == "NORTHEAST":
            print(f"  Found NORTHEAST at start={start}, step={step}!")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
