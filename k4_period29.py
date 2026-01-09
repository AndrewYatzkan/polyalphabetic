#!/usr/bin/env python3
"""
K4 Period 29 Deep Analysis

Found that period 29 is compatible with:
- NORTHEAST at positions 16-24
- BERLINCLOCK at positions 63-73

Key: ?????ELYOIECBAQKVAATCRDUM????

Let's try to fill in the missing 5 key characters.
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

def decrypt_with_key(ct, key, alpha=KRYPTOS_ALPHA):
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
        else:
            result.append(decrypt(c, k, alpha))
    return ''.join(result)

# English letter frequencies
ENG_FREQ = {'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
            'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
            'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
            'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
            'Q': 0.10, 'Z': 0.07}

COMMON_WORDS = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS',
                'ITS', 'SAY', 'SHE', 'TWO', 'WAY', 'WHO', 'DID', 'HIM',
                'GET', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TIME', 'VERY',
                'WHEN', 'COME', 'MAKE', 'THAN', 'FIRST', 'BEEN', 'CALL',
                'FIND', 'LONG', 'DOWN', 'OVER', 'SUCH', 'TAKE', 'KNOW',
                'EAST', 'WEST', 'NORTH', 'SOUTH', 'BERLIN', 'CLOCK',
                'DEGREES', 'MINUTES', 'SECONDS', 'LOCATION', 'SECRET',
                'HIDDEN', 'BURIED', 'LAYER', 'SHADOW', 'LIGHT']

def score_plaintext(pt):
    """Score plaintext for English-likeness."""
    # Remove unknowns for scoring
    known_chars = [c for c in pt if c != '?']
    if not known_chars:
        return -1000

    score = 0

    # Check for common words in the known parts
    pt_known = ''.join(known_chars)
    for word in COMMON_WORDS:
        if word in pt:
            score += len(word) * 5

    # Letter frequency
    freq = Counter(known_chars)
    n = len(known_chars)
    for letter, count in freq.items():
        observed = count / n * 100
        expected = ENG_FREQ.get(letter, 0)
        score -= abs(observed - expected) * 0.5

    # Penalize uncommon letters
    uncommon = ['Q', 'X', 'Z', 'J']
    for letter in uncommon:
        score -= freq.get(letter, 0) * 3

    return score

print("="*70)
print("K4 PERIOD 29 DEEP ANALYSIS")
print("="*70)

# Known key positions for period 29
# Position 16-24 mod 29 = 16-24 -> key positions 16-24
# Position 63-73 mod 29:
# 63 mod 29 = 5
# 64 mod 29 = 6
# etc.

period = 29
key = ['?'] * period

# Fill in from NORTHEAST at position 16
ne_key = "VAATCRDUM"
for i, k in enumerate(ne_key):
    key_pos = (16 + i) % period
    key[key_pos] = k

# Fill in from BERLINCLOCK at position 63
bc_key = "ELYOIECBAQK"
for i, k in enumerate(bc_key):
    key_pos = (63 + i) % period
    key[key_pos] = k

print(f"\nKey with known positions: {''.join(key)}")
print(f"Unknown positions: {[i for i, k in enumerate(key) if k == '?']}")

# The unknown positions are 0, 1, 2, 3, 4 and 25, 26, 27, 28
# Actually let's verify
unknown_positions = [i for i, k in enumerate(key) if k == '?']
print(f"Unknown key positions: {unknown_positions}")

# Decrypt with partial key
partial_pt = decrypt_with_key(K4, key)
print(f"\nPartial plaintext: {partial_pt}")

# Which ciphertext positions are unknown?
unknown_ct_positions = [i for i in range(len(K4)) if key[i % period] == '?']
print(f"\nUnknown ciphertext positions: {unknown_ct_positions}")

# Try to fill in the missing key characters
# We need to find 5 characters that make the plaintext English-like
print("\n" + "="*70)
print("BRUTE FORCE SEARCH FOR MISSING KEY CHARACTERS")
print("="*70)

# Unknown positions: 0, 1, 2, 3, 4
# That's 26^5 = 11,881,376 combinations - too many
# Let's be smarter

# What positions in plaintext use these key characters?
# Position 0 uses key[0], position 29 uses key[0], position 58 uses key[0], position 87 uses key[0]
# Position 1 uses key[1], position 30 uses key[1], position 59 uses key[1], position 88 uses key[1]
# etc.

for key_pos in unknown_positions:
    ct_positions = [i for i in range(len(K4)) if i % period == key_pos]
    ct_chars = [K4[i] for i in ct_positions]
    print(f"Key position {key_pos} affects ciphertext positions: {ct_positions}")
    print(f"  Ciphertext chars: {ct_chars}")

# Let's try common key letter patterns
# The known key segment is: ELYOIECBAQKVAATCRDUM
# Maybe it's a word or phrase?

print("\n" + "="*70)
print("ANALYZING KNOWN KEY SEGMENT")
print("="*70)

known_segment = ''.join(k for k in key if k != '?')
print(f"Known key characters: {known_segment}")
print(f"Length: {len(known_segment)}")

# Could this be PALIMPSEST or similar keyword?
# ELYOIECBAQKVAATCRDUM doesn't look like English

# Try to find the best single key character for each unknown position
print("\n" + "="*70)
print("FINDING BEST KEY CHARACTER FOR EACH UNKNOWN POSITION")
print("="*70)

best_chars = {}
for key_pos in unknown_positions:
    ct_positions = [i for i in range(len(K4)) if i % period == key_pos]

    best_score = -1000
    best_char = '?'

    for test_char in KRYPTOS_ALPHA:
        # What plaintext would this produce at these positions?
        test_pts = [decrypt(K4[i], test_char) for i in ct_positions]

        # Score based on common letters
        score = 0
        for pt_char in test_pts:
            score += ENG_FREQ.get(pt_char, 0)

        if score > best_score:
            best_score = score
            best_char = test_char

    best_chars[key_pos] = best_char
    print(f"Key position {key_pos}: best char = {best_char} (score: {best_score:.1f})")
    print(f"  Would produce: {[decrypt(K4[i], best_char) for i in ct_positions]}")

# Fill in best characters
for pos, char in best_chars.items():
    key[pos] = char

full_key = ''.join(key)
print(f"\nComplete key guess: {full_key}")

# Decrypt fully
full_pt = decrypt_with_key(K4, key)
print(f"\nFull plaintext: {full_pt}")

# Check for words
words_found = [w for w in COMMON_WORDS if w in full_pt]
print(f"Words found: {words_found}")

# Let's also try some specific key completions
print("\n" + "="*70)
print("TRYING SPECIFIC KEY COMPLETIONS")
print("="*70)

# The key might be a meaningful word or phrase
# Let's try adding common letter combinations at the start

# Reset to known key
key = ['?'] * period
for i, k in enumerate(ne_key):
    key[(16 + i) % period] = k
for i, k in enumerate(bc_key):
    key[(63 + i) % period] = k

# Try different prefixes for positions 0-4
prefixes_to_try = ['KRYPT', 'PALIN', 'BERLI', 'CLOCK', 'NORTH', 'SOUTH',
                   'ABCDE', 'KRPYT', 'SHADO', 'LAYER', 'INTEL', 'SECRE']

for prefix in prefixes_to_try:
    test_key = list(key)
    for i, c in enumerate(prefix[:len(unknown_positions)]):
        if i < len(unknown_positions):
            test_key[unknown_positions[i]] = c

    test_pt = decrypt_with_key(K4, test_key)

    # Score this
    words = [w for w in COMMON_WORDS if w in test_pt and w not in ['EAST', 'NORTH', 'BERLIN', 'CLOCK']]
    if words:
        print(f"Prefix '{prefix}': Found extra words: {words}")
        print(f"  Plaintext: {test_pt}")

# Try systematic search with constraints
print("\n" + "="*70)
print("SYSTEMATIC SEARCH FOR ENGLISH PLAINTEXT")
print("="*70)

# Positions 0, 29, 58, 87 use key[0]
# These map to plaintext characters that should be English

# Let's find combinations that produce common trigrams at the start
best_solutions = []

# Use top English letters for unknown positions
common_letters = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'

for k0 in common_letters[:10]:
    for k1 in common_letters[:10]:
        for k2 in common_letters[:10]:
            for k3 in common_letters[:10]:
                for k4 in common_letters[:10]:
                    test_key = list(key)
                    test_key[0] = k0
                    test_key[1] = k1
                    test_key[2] = k2
                    test_key[3] = k3
                    test_key[4] = k4

                    test_pt = decrypt_with_key(K4, test_key)

                    # Quick scoring - look for common words
                    score = 0
                    for word in ['THE', 'AND', 'WAS', 'FOR', 'ARE']:
                        if word in test_pt:
                            score += 10

                    if score > 0:
                        best_solutions.append((''.join(test_key), test_pt, score))

# Sort and show best
best_solutions.sort(key=lambda x: -x[2])
print(f"\nFound {len(best_solutions)} solutions with common words")
for key_str, pt, score in best_solutions[:10]:
    words = [w for w in COMMON_WORDS if w in pt]
    print(f"\nKey: {key_str}")
    print(f"Plaintext: {pt}")
    print(f"Words: {words}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
