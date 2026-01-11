#!/usr/bin/env python3
"""
Optimize for the exact key using the best candidates found.

Best candidates so far:
- Gap 2 with "BERL": chi² = 1.96
- Gap 2 with "ABOVE": chi² = 2.98
- Gap 2 with "BERLIN1989": chi² = 2.36
- Single letter "X" on Gap 1: chi² = 1.64
- Single letter "M" on Gap 2: chi² = 2.40
"""

from collections import Counter
import itertools

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

print("="*80)
print("KEY OPTIMIZATION: FINDING BEST DECRYPTION KEYS")
print("="*80)

# Test variations of best keys
print("\n" + "="*80)
print("TEST 1: EXTENDING PARTIAL KEYS")
print("="*80)

# "BERL" showed chi² = 1.96, try extending it
berl_keys = [
    "BER",
    "BERL",
    "BERLI",
    "BERLIN",
    "BERLINC",
    "BERLINCL",
    "BERLINCLO",
    "BERLINCLOCK",
]

print("\nGap 2 with BERL-based keys:")
print(f"  {'Key':<20} {'Chi²':<10} {'Vowels':<10} Result")
for key in berl_keys:
    decrypted = vigenere_decrypt(GAP2, key)
    chi_sq = chi_squared_english(decrypted)
    vowels = sum(1 for c in decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(decrypted)

    marker = " ⚠" if chi_sq < 5 else ""
    print(f"  {key:<20} {chi_sq:8.2f}   {vowel_ratio:5.1%}    {decrypted[:20]}{marker}")

# Test ABOVE variations
above_keys = [
    "A",
    "AB",
    "ABO",
    "ABOV",
    "ABOVE",
]

print("\nGap 2 with ABOVE-based keys:")
print(f"  {'Key':<20} {'Chi²':<10} {'Vowels':<10} Result")
for key in above_keys:
    decrypted = vigenere_decrypt(GAP2, key)
    chi_sq = chi_squared_english(decrypted)
    vowels = sum(1 for c in decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(decrypted)

    marker = " ⚠" if chi_sq < 5 else ""
    print(f"  {key:<20} {chi_sq:8.2f}   {vowel_ratio:5.1%}    {decrypted[:20]}{marker}")

# =============================================================================
# TEST 2: BRUTE FORCE SHORT KEYS (3-4 LETTERS)
# =============================================================================

print(f"\n{'='*80}")
print("TEST 2: BRUTE FORCE 3-4 LETTER KEYS")
print("="*80)

print("\nSearching for best 3-letter keys on Gap 2...")

best_keys_3 = []
for key_chars in itertools.combinations_with_replacement('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 3):
    key = ''.join(key_chars)
    decrypted = vigenere_decrypt(GAP2, key)
    chi_sq = chi_squared_english(decrypted)

    if chi_sq < 8:  # Only track good ones
        best_keys_3.append((chi_sq, key, decrypted))

# Sort and print top 20
best_keys_3.sort()
print("\nTop 20 best 3-letter keys:")
print(f"  {'Rank':<5} {'Chi²':<10} {'Key':<10} Decrypted")
for i, (chi_sq, key, decrypted) in enumerate(best_keys_3[:20]):
    print(f"  {i+1:<5} {chi_sq:8.2f}   {key:<10} {decrypted[:25]}...")

print("\nSearching for best 4-letter keys on Gap 2...")

best_keys_4 = []
for key_chars in itertools.combinations_with_replacement('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 4):
    key = ''.join(key_chars)
    decrypted = vigenere_decrypt(GAP2, key)
    chi_sq = chi_squared_english(decrypted)

    if chi_sq < 8:  # Only track good ones
        best_keys_4.append((chi_sq, key, decrypted))

# Sort and print top 20
best_keys_4.sort()
print("\nTop 20 best 4-letter keys:")
print(f"  {'Rank':<5} {'Chi²':<10} {'Key':<10} Decrypted")
for i, (chi_sq, key, decrypted) in enumerate(best_keys_4[:20]):
    print(f"  {i+1:<5} {chi_sq:8.2f}   {key:<10} {decrypted[:25]}...")

# =============================================================================
# TEST 3: TEST BEST KEYS ON ALL GAPS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 3: TEST BEST KEYS ON ALL GAPS")
print("="*80)

gaps = [
    ("Gap 1", GAP1),
    ("Gap 2", GAP2),
    ("Gap 3", GAP3),
    ("Gap 4", GAP4)
]

# Get unique top keys (remove duplicates based on chi_sq value)
top_keys_to_test = list(set([key for _, key, _ in best_keys_3[:5] + best_keys_4[:5]]))

for key in top_keys_to_test:
    print(f"\nKey: '{key}'")
    print(f"  {'Gap':<10} {'Chi²':<10} {'Vowels':<10} Decrypted")
    for gap_name, gap_text in gaps:
        decrypted = vigenere_decrypt(gap_text, key)
        chi_sq = chi_squared_english(decrypted)
        vowels = sum(1 for c in decrypted if c in 'AEIOU')
        vowel_ratio = vowels / len(decrypted) if decrypted else 0

        marker = " ⚠" if chi_sq < 8 else ""
        print(f"  {gap_name:<10} {chi_sq:8.2f}   {vowel_ratio:5.1%}    {decrypted[:25]}{marker}")

# =============================================================================
# TEST 4: ANALYZE TOP DECRYPTIONS FOR ENGLISH WORDS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 4: CHECKING FOR ENGLISH WORDS IN TOP DECRYPTIONS")
print("="*80)

common_words = [
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
    'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY',
    'LIKE', 'TIME', 'GOOD', 'MADE', 'MAKE', 'OVER', 'JUST', 'KNOW', 'TAKE',
    'SUCH', 'THAN', 'THEM', 'THEN', 'THEY', 'THIS', 'WELL', 'WHEN', 'WITH',
    'ABOUT', 'WOULD', 'COULD', 'WHICH', 'THEIR', 'WHERE', 'THESE', 'OTHER',
    'BEFORE', 'AFTER', 'FIRST', 'SECOND', 'BERLIN', 'CLOCK', 'COORDINATES'
]

print("\nGap 2 with top 3-letter key analysis:")
if best_keys_3:
    chi_sq, key, decrypted = best_keys_3[0]
    print(f"Key: {key}, Chi²: {chi_sq:.2f}")
    print(f"Decrypted: {decrypted}")

    found_words = []
    for word in common_words:
        if word in decrypted:
            found_words.append(word)

    if found_words:
        print(f"Found words: {found_words}")
    else:
        print("No common words found")

print("\n" + "="*80)
print("OPTIMIZATION COMPLETE")
print("="*80)
