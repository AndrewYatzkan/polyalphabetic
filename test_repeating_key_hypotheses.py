#!/usr/bin/env python3
"""
Test repeating key hypotheses for K4 gibberish.

Key insight: Gap 2 has chi-squared of 9.68 (very close to English).
This suggests it might be encrypted with a short repeating key!

Test:
1. Short keys (3-9 characters) with Vigenère
2. Keys derived from: UNDER, NORTHEAST, ABOVE, BERLINCLOCK
3. Keys based on numbers: 291111989 (Berlin Wall date), 2626 (alphabet size)
4. All single-letter keys (A-Z) to find most English-like decryption
"""

from collections import Counter

K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

GAP1 = "QAPBZDBKZEL"
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenère cipher."""
    plaintext = ""
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext += decrypted
            key_idx += 1
        else:
            plaintext += char
    return plaintext

def chi_squared_english(text):
    """Calculate chi-squared against English distribution."""
    english_freq = {
        'A': 0.082, 'B': 0.015, 'C': 0.028, 'D': 0.043, 'E': 0.127,
        'F': 0.022, 'G': 0.020, 'H': 0.061, 'I': 0.070, 'J': 0.002,
        'K': 0.008, 'L': 0.040, 'M': 0.024, 'N': 0.067, 'O': 0.075,
        'P': 0.019, 'Q': 0.001, 'R': 0.060, 'S': 0.063, 'T': 0.091,
        'U': 0.028, 'V': 0.010, 'W': 0.024, 'X': 0.002, 'Y': 0.020,
        'Z': 0.001
    }

    freq = Counter(text)
    total = len(text)
    chi_sq = 0
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(char, 0) / total
        expected = english_freq[char]
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected

    return chi_sq

def find_best_single_key(ciphertext):
    """Find single-letter key that produces most English-like plaintext."""
    best_key = 'A'
    best_chi = float('inf')
    best_decrypted = ""

    for shift in range(26):
        key = chr(ord('A') + shift)
        decrypted = vigenere_decrypt(ciphertext, key)
        chi_sq = chi_squared_english(decrypted)

        if chi_sq < best_chi:
            best_chi = chi_sq
            best_key = key
            best_decrypted = decrypted

    return best_key, best_chi, best_decrypted

def find_best_key_length(ciphertext, max_length=10):
    """Find best key length using Index of Coincidence."""
    best_length = 1
    best_ic = 0
    best_chi = float('inf')
    best_key = 'A'

    for key_length in range(1, max_length + 1):
        # Try all keys of this length
        for test_key in ['A' * key_length]:
            decrypted = vigenere_decrypt(ciphertext, test_key)
            chi_sq = chi_squared_english(decrypted)

            if chi_sq < best_chi:
                best_chi = chi_sq
                best_key = test_key
                best_length = key_length

    return best_length, best_key, best_chi

# =============================================================================
# TEST SINGLE-LETTER KEYS (A-Z)
# =============================================================================

print("="*80)
print("TEST 1: SINGLE-LETTER KEYS (Caesar cipher shift)")
print("="*80)

gaps = [
    ("Gap 1", GAP1),
    ("Gap 2", GAP2),
    ("Gap 3", GAP3),
    ("Gap 4", GAP4)
]

for gap_name, gap_text in gaps:
    print(f"\n{gap_name} ({len(gap_text)} chars): {gap_text}")

    best_key, best_chi, best_decrypted = find_best_single_key(gap_text)

    print(f"  Best single-letter key: {best_key}")
    print(f"  Chi-squared: {best_chi:.2f}")
    print(f"  Decrypted: {best_decrypted}")

    # Check if English-like
    vowels = sum(1 for c in best_decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(best_decrypted) if best_decrypted else 0
    print(f"  Vowel ratio: {vowel_ratio:.1%}")

# =============================================================================
# TEST SHORT REPEATING KEYS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 2: SHORT REPEATING KEYS (2-6 characters)")
print("="*80)

short_keys = [
    "AB",
    "ABC",
    "ABCD",
    "ABCDE",
    "ABCDEF",
]

gap = GAP2
print(f"\nTesting on Gap 2: {gap}")

for key in short_keys:
    decrypted = vigenere_decrypt(gap, key)
    chi_sq = chi_squared_english(decrypted)

    vowels = sum(1 for c in decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(decrypted) if decrypted else 0

    print(f"  {key:10s} -> chi²: {chi_sq:6.2f}, vowels: {vowel_ratio:5.1%}, decrypted: {decrypted[:20]}...")

# =============================================================================
# TEST KEYS DERIVED FROM READABLE WORDS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 3: KEYS FROM READABLE WORDS (and variations)")
print("="*80)

word_keys = [
    "U",          # From UNDER
    "UN",
    "UND",
    "UNDE",
    "UNDER",
    "N",          # From NORTHEAST
    "NE",
    "NOR",
    "NORT",
    "NORTH",
    "B",          # From BERLINCLOCK
    "BE",
    "BER",
    "BERL",
    "BERLIN",
    "A",          # From ABOVE
    "AB",
    "ABO",
    "ABOV",
    "ABOVE",
    # Combinations
    "UNDERABOVE",
    "UNNE",      # Mixed
    "UNA",       # Mixed
]

for key in word_keys:
    decrypted = vigenere_decrypt(GAP2, key)
    chi_sq = chi_squared_english(decrypted)

    vowels = sum(1 for c in decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(decrypted)

    if chi_sq < 50 or vowel_ratio > 0.35:  # Highlight good results
        print(f"  {key:15s} -> chi²: {chi_sq:6.2f}, vowels: {vowel_ratio:5.1%} ⚠")
    else:
        print(f"  {key:15s} -> chi²: {chi_sq:6.2f}, vowels: {vowel_ratio:5.1%}")

# =============================================================================
# TEST BERLIN-RELATED KEYS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 4: BERLIN-RELATED KEYS")
print("="*80)

berlin_keys = [
    "BERLIN",
    "CLOCK",
    "BERLINCLOCK",
    "WELTZEITUHR",
    "WALL",
    "GATE",
    "BRANDENBURGGATE",
    "REICHSTAG",
    "ALEXANDERPLATZ",
    "1989",
    "11091989",
    "BERLIN1989",
    "WALLFALL",
    "WESTEAST",
]

for key in berlin_keys:
    if len(key) > 20:
        continue

    decrypted = vigenere_decrypt(GAP2, key)
    chi_sq = chi_squared_english(decrypted)

    vowels = sum(1 for c in decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(decrypted)

    # Extract first few decrypted words
    words = decrypted[:25]

    if chi_sq < 50 or vowel_ratio > 0.35:
        print(f"  {key:15s} -> chi²: {chi_sq:6.2f}, vowels: {vowel_ratio:5.1%} ⚠")
        print(f"    First 25: {words}")
    else:
        print(f"  {key:15s} -> chi²: {chi_sq:6.2f}, vowels: {vowel_ratio:5.1%}")

# =============================================================================
# TEST ALL GAPS WITH TOP CANDIDATES
# =============================================================================

print(f"\n{'='*80}")
print("TEST 5: TOP CANDIDATE KEYS ON ALL GAPS")
print("="*80)

top_keys = [
    "UNDER",
    "NORTHEAST",
    "BERLINCLOCK",
    "ABOVE",
    "KRYPTOS",
    "U",
    "N",
    "A",
]

for key in top_keys:
    print(f"\nKey: {key}")
    print(f"  {'Gap':<10} {'Chi²':<10} {'Vowels':<10} Decrypted")
    print(f"  {'-'*50}")

    for gap_name, gap_text in gaps:
        decrypted = vigenere_decrypt(gap_text, key)
        chi_sq = chi_squared_english(decrypted)
        vowels = sum(1 for c in decrypted if c in 'AEIOU')
        vowel_ratio = vowels / len(decrypted) if decrypted else 0

        print(f"  {gap_name:<10} {chi_sq:8.2f}   {vowel_ratio:5.1%}    {decrypted[:25]}")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print("Look for chi² < 50 and vowel ratio > 30% as indicators of possible English")
print("="*80)
