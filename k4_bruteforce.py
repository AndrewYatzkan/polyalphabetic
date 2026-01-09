#!/usr/bin/env python3
"""
K4 Brute Force Attack - Try everything

Last-ditch efforts to crack K4:
1. Try ALL alphabet variations
2. Try different crib positions
3. Try combining multiple constraints
4. Exhaustive key search with English scoring
"""

import itertools
from collections import Counter
import re

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# English letter frequencies for scoring
ENG_FREQ = {'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
            'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
            'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
            'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
            'Q': 0.10, 'Z': 0.07}

def score_english(text):
    """Score text based on English frequency."""
    score = 0
    for c in text:
        score += ENG_FREQ.get(c, 0)
    return score / len(text) if text else 0

def decrypt(ct, key, alpha):
    return ''.join(alpha[(alpha.index(c) - alpha.index(key[i % len(key)])) % len(alpha)]
                   for i, c in enumerate(ct))

def derive_key(ct, pt, alpha):
    return ''.join(alpha[(alpha.index(c) - alpha.index(p)) % len(alpha)]
                   for c, p in zip(ct, pt))

print("="*70)
print("K4 BRUTE FORCE ATTACK")
print("="*70)

# ATTEMPT 1: Try different alphabet orderings
print("\n[1] TRYING DIFFERENT ALPHABET ORDERINGS")
print("="*70)

# Generate some keyword-based alphabets
keywords = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK',
            'NORTHEAST', 'SANBORN', 'LANGLEY', 'SHADOW', 'SECRET']

best_score = 0
best_result = None

for keyword in keywords:
    # Create keyed alphabet
    alpha = ""
    for c in keyword.upper():
        if c not in alpha and c.isalpha():
            alpha += c
    for c in STANDARD_ALPHA:
        if c not in alpha:
            alpha += c

    # Try various period keys
    for period in range(7, 15):
        for key_word in keywords:
            key = (key_word * 3)[:period]
            pt = decrypt(K4, key, alpha)

            if 'BERLIN' in pt and 'CLOCK' in pt:
                print(f"FOUND BERLIN+CLOCK! Alpha={keyword}, key={key}")
                print(f"  {pt}")

            if 'NORTHEAST' in pt:
                print(f"FOUND NORTHEAST! Alpha={keyword}, key={key}")
                print(f"  {pt}")

            score = score_english(pt)
            if score > best_score:
                best_score = score
                best_result = (keyword, key, pt, score)

if best_result:
    print(f"\nBest English-like result:")
    print(f"  Alpha keyword: {best_result[0]}")
    print(f"  Key: {best_result[1]}")
    print(f"  Score: {best_result[3]:.2f}")
    print(f"  Text: {best_result[2][:60]}...")

# ATTEMPT 2: What if BERLIN and CLOCK aren't adjacent?
print("\n[2] TRYING NON-ADJACENT BERLIN AND CLOCK")
print("="*70)

for berlin_pos in range(len(K4) - 6):
    for clock_pos in range(len(K4) - 5):
        if abs(berlin_pos - clock_pos) < 5:  # Skip overlapping
            continue

        # Derive key constraints from both
        berlin_ct = K4[berlin_pos:berlin_pos+6]
        clock_ct = K4[clock_pos:clock_pos+5]

        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            berlin_key = derive_key(berlin_ct, "BERLIN", alpha)
            clock_key = derive_key(clock_ct, "CLOCK", alpha)

            # Check if keys could be from same periodic key
            for period in range(5, 15):
                consistent = True
                key = ['?'] * period

                # Fill from BERLIN
                for i, k in enumerate(berlin_key):
                    pos = (berlin_pos + i) % period
                    if key[pos] == '?':
                        key[pos] = k
                    elif key[pos] != k:
                        consistent = False
                        break

                if not consistent:
                    continue

                # Fill from CLOCK
                for i, k in enumerate(clock_key):
                    pos = (clock_pos + i) % period
                    if key[pos] == '?':
                        key[pos] = k
                    elif key[pos] != k:
                        consistent = False
                        break

                if consistent and '?' not in key:
                    key_str = ''.join(key)
                    pt = decrypt(K4, key_str, alpha)

                    if 'BERLIN' in pt and 'CLOCK' in pt:
                        print(f"FOUND! Berlin@{berlin_pos}, Clock@{clock_pos}")
                        print(f"  Key: {key_str}, Period: {period}")
                        print(f"  {pt}")

                        if 'NORTHEAST' in pt:
                            print("  *** ALSO HAS NORTHEAST! ***")

# ATTEMPT 3: Simple offset/Caesar variants
print("\n[3] TRYING CAESAR AND OFFSET VARIANTS")
print("="*70)

for offset in range(26):
    # Simple Caesar shift
    pt = ''.join(STANDARD_ALPHA[(STANDARD_ALPHA.index(c) - offset) % 26] for c in K4)

    if 'BERLIN' in pt or 'CLOCK' in pt or 'NORTHEAST' in pt:
        print(f"Caesar offset {offset}: {pt}")

# ATTEMPT 4: Check if any rotation of K4 produces better results
print("\n[4] TRYING ROTATIONS OF CIPHERTEXT")
print("="*70)

for rotation in range(len(K4)):
    rotated = K4[rotation:] + K4[:rotation]

    # Try with known key
    for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'OIECBAQKELY']:
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            pt = decrypt(rotated, key, alpha)

            if 'BERLIN' in pt and 'CLOCK' in pt:
                print(f"Rotation {rotation}, key={key}: FOUND BERLIN+CLOCK!")
                print(f"  {pt}")

# ATTEMPT 5: What if it's atbash combined with something?
print("\n[5] TRYING ATBASH COMBINATIONS")
print("="*70)

def atbash(text, alpha=STANDARD_ALPHA):
    return ''.join(alpha[-(alpha.index(c)+1)] if c in alpha else c for c in text)

atbash_k4 = atbash(K4, STANDARD_ALPHA)
print(f"Atbash of K4: {atbash_k4}")

for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA']:
    pt = decrypt(atbash_k4, key, KRYPTOS_ALPHA)
    if 'BERLIN' in pt or 'NORTHEAST' in pt:
        print(f"Atbash then Vig with {key}: {pt}")

# ATTEMPT 6: Try reading K4 backwards
print("\n[6] TRYING REVERSED CIPHERTEXT")
print("="*70)

reversed_k4 = K4[::-1]
print(f"Reversed K4: {reversed_k4}")

for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'OIECBAQKELY']:
    for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
        pt = decrypt(reversed_k4, key, alpha)

        if 'BERLIN' in pt or 'CLOCK' in pt or 'NORTHEAST' in pt:
            print(f"Reversed + key={key}: {pt}")

# ATTEMPT 7: Exhaustive short key search
print("\n[7] EXHAUSTIVE KEY SEARCH (SHORT KEYS)")
print("="*70)

print("Searching 3-letter keys...")
best_score = 0
for key in itertools.product(KRYPTOS_ALPHA, repeat=3):
    key_str = ''.join(key)
    pt = decrypt(K4, key_str, KRYPTOS_ALPHA)

    if 'BERLIN' in pt:
        print(f"Key {key_str}: BERLIN found! {pt[:50]}...")
    if 'NORTHEAST' in pt:
        print(f"Key {key_str}: NORTHEAST found! {pt[:50]}...")

print("\nSearching 4-letter keys with high-frequency letters...")
common_letters = 'KRYPTOSAE'
for key in itertools.product(common_letters, repeat=4):
    key_str = ''.join(key)
    pt = decrypt(K4, key_str, KRYPTOS_ALPHA)

    if 'BERLIN' in pt or 'NORTHEAST' in pt:
        print(f"Key {key_str}: {pt[:50]}...")

print("\n" + "="*70)
print("BRUTE FORCE COMPLETE")
print("="*70)
