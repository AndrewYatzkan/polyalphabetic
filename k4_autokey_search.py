#!/usr/bin/env python3
"""
K4 Autokey Cipher Deep Search

Try autokey cipher with various primers using KRYPTOS alphabet.
Autokey: key = primer + plaintext (so key evolves based on decrypted text)
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

COMMON_WORDS = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS',
                'WITH', 'THAT', 'THIS', 'HAVE', 'FROM', 'THEY', 'BEEN',
                'EAST', 'WEST', 'NORTH', 'SOUTH', 'BERLIN', 'CLOCK',
                'DEGREES', 'SLOWLY', 'LAYER', 'SHADOW', 'LIGHT']

def autokey_decrypt(ct, primer, alpha):
    """Decrypt using autokey cipher."""
    pt = []
    for i, c in enumerate(ct):
        if i < len(primer):
            key_char = primer[i]
        else:
            key_char = pt[i - len(primer)]

        pt_idx = (alpha.index(c) - alpha.index(key_char)) % len(alpha)
        pt.append(alpha[pt_idx])

    return ''.join(pt)

def score_text(text):
    """Score text for English-likeness."""
    score = 0
    for word in COMMON_WORDS:
        if word in text:
            score += len(word) ** 2
    return score

print("="*70)
print("K4 AUTOKEY CIPHER DEEP SEARCH")
print("="*70)

# Try known words as primers
primers_to_try = [
    # Original Kryptos keywords
    'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'KOMITET', 'SHADOW',
    # K4 related
    'BERLINCLOCK', 'BERLIN', 'CLOCK', 'NORTHEAST', 'EAST', 'NORTH',
    # Derived keys
    'ELYOIECBAQK', 'VAATCRDUM',
    # Other possibilities
    'SANBORN', 'CIA', 'LANGLEY', 'SECRET', 'HIDDEN', 'LAYER',
    # Combinations
    'KRYPTOSABSCISSA', 'PALIMPSESTABSCISSA',
]

# Also try short primers (1-4 letters)
for length in range(1, 5):
    for combo in itertools.product(KRYPTOS_ALPHA[:10], repeat=length):
        primers_to_try.append(''.join(combo))

print(f"Testing {len(primers_to_try)} primers...")

best_results = []

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    for primer in primers_to_try:
        # Skip if primer has invalid chars
        if not all(c in alpha for c in primer):
            continue

        pt = autokey_decrypt(K4, primer, alpha)
        score = score_text(pt)

        if score > 0:
            words_found = [w for w in COMMON_WORDS if w in pt]
            best_results.append((alpha_name, primer, pt, score, words_found))

# Sort by score
best_results.sort(key=lambda x: -x[3])

print(f"\nFound {len(best_results)} results with common words")
print("\nTop 30 results:")
print("="*70)

for i, (alpha_name, primer, pt, score, words) in enumerate(best_results[:30]):
    print(f"\n{i+1}. Alpha: {alpha_name}, Primer: '{primer}', Score: {score}")
    print(f"   Plaintext: {pt[:60]}...")
    print(f"   Words: {words}")

# Now specifically look for BERLINCLOCK in autokey results
print("\n" + "="*70)
print("SEARCHING FOR BERLINCLOCK IN AUTOKEY")
print("="*70)

# Try primers of various lengths that would produce BERLINCLOCK at position 63
# In autokey, key[63] = pt[63 - primer_len] if 63 >= primer_len
# We know pt[63:74] should be BERLINCLOCK
# And key[63:74] should be... let's derive it

# For autokey with primer length P:
# - Positions 0 to P-1: key comes from primer
# - Positions P and beyond: key comes from plaintext

# If pt[63:74] = BERLINCLOCK, then for positions 74+:
# key[74] = pt[74 - P] for primer length P

# This is complex. Let's try a different approach:
# Brute force primer search looking for BERLINCLOCK in output

print("\nSearching for primers that produce BERLINCLOCK...")

for primer_len in range(1, 20):
    print(f"\nTrying primer length {primer_len}...")
    found_count = 0

    # For shorter lengths, try all combinations
    if primer_len <= 4:
        candidates = itertools.product(KRYPTOS_ALPHA, repeat=primer_len)
    else:
        # For longer lengths, try dictionary words and derived keys
        candidates = []
        for word in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'KOMITET', 'SHADOW',
                     'BERLINCLOCK', 'BERLIN', 'CLOCK', 'NORTHEAST', 'ELYOIECBAQK']:
            if len(word) == primer_len:
                candidates.append(tuple(word))

        # Also try repeating patterns
        for base in ['KRYPTOS', 'BERLIN', 'CLOCK', 'NORTHEAST']:
            extended = (base * 10)[:primer_len]
            if len(extended) == primer_len:
                candidates.append(tuple(extended))

    for primer_tuple in candidates:
        primer = ''.join(primer_tuple)

        for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA)]:
            if not all(c in alpha for c in primer):
                continue

            pt = autokey_decrypt(K4, primer, alpha)

            if 'BERLINCLOCK' in pt:
                bc_pos = pt.find('BERLINCLOCK')
                found_count += 1
                print(f"  FOUND! Primer: {primer}, BERLINCLOCK at position {bc_pos}")
                print(f"  Plaintext: {pt}")

                if 'NORTHEAST' in pt:
                    print(f"  *** ALSO FOUND NORTHEAST! ***")

    if primer_len <= 4:
        print(f"  Checked {26**primer_len} combinations, found {found_count}")

print("\n" + "="*70)
print("AUTOKEY SEARCH COMPLETE")
print("="*70)
