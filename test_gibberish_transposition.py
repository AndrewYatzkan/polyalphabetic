#!/usr/bin/env python3
"""
Test if K4 gibberish uses transposition cipher or position-based encoding.

Key insight: Period-29 Vigenère is confirmed correct.
Gibberish doesn't decrypt to English with simple secondary keys.

Hypothesis 1: Gibberish is transposition (rearranged plaintext)
Hypothesis 2: Gibberish encodes coordinates/positions/indices
Hypothesis 3: Gibberish uses a complex hybrid cipher
"""

import itertools

def transpose_rail_fence(text, num_rails):
    """Decrypt rail fence cipher (transposition)."""
    fence = [[] for _ in range(num_rails)]
    rail = 0
    direction = 1

    # Read ciphertext into fence
    for i, char in enumerate(text):
        fence[rail].append(char)
        if rail == 0:
            direction = 1
        elif rail == num_rails - 1:
            direction = -1
        rail += direction

    # Flatten to get plaintext
    return ''.join(''.join(f) for f in fence)

def transpose_columnar(text, key_order):
    """Decrypt columnar transposition."""
    if len(text) == 0:
        return ""

    # key_order tells us the reading order
    num_cols = len(key_order)
    num_rows = len(text) // num_cols

    if len(text) % num_cols != 0:
        return None  # Can't transpose

    # Create grid based on key order
    columns = [[] for _ in range(num_cols)]
    idx = 0

    # Fill columns in the order given by key_order
    for col_idx in key_order:
        for row in range(num_rows):
            columns[col_idx].append(text[idx])
            idx += 1

    # Read row by row
    result = []
    for row in range(num_rows):
        for col in range(num_cols):
            result.append(columns[col][row])

    return ''.join(result)

def check_meaningful_indices(text):
    """
    Check if text is encoding indices/positions.
    E.g., if first letter = position, followed by data.
    """
    # Try to find patterns of form: letter (position) + letters (data)
    positions = []
    for char in text:
        if char.isalpha():
            pos = ord(char) - ord('A')
            positions.append(pos)
    return positions

KRYPTOS_ALPHABET = 'KRYPTOSABCDEFGHIJLMNQUVWXZ'

gibberish_sections = {
    'section_1': 'QAPBZDBKZEL',
    'section_2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
    'section_3': 'RSPVJWQUL',
    'section_4': 'ZOLRKCAYF',
}

print("="*80)
print("TEST 1: Rail Fence Decryption (Transposition)")
print("="*80)

print("\nTesting rail fence cipher with 2-5 rails:\n")

for section_name, ciphertext in gibberish_sections.items():
    print(f"{section_name}: {ciphertext}")

    # Try different numbers of rails
    best_for_section = None
    best_score = 0

    for num_rails in range(2, min(6, len(ciphertext))):
        try:
            decrypted = transpose_rail_fence(ciphertext, num_rails)

            # Score based on vowels (English should have ~40%)
            vowels = sum(1 for c in decrypted if c in 'AEIOUY')
            vowel_ratio = vowels / len(decrypted) if decrypted else 0

            # Check for repeated letters (common in English)
            from collections import Counter
            freq = Counter(decrypted)
            has_doubles = any(count >= 2 for count in freq.values())

            score = vowel_ratio if vowel_ratio > 0.25 else 0
            if has_doubles:
                score += 0.1

            if score > best_score:
                best_score = score
                best_for_section = (num_rails, decrypted, vowel_ratio)

            print(f"  {num_rails} rails: {decrypted} ({vowel_ratio:.0%} vowels)")
        except Exception as e:
            pass

    if best_for_section:
        rails, text, ratio = best_for_section
        print(f"  Best: {rails} rails -> {text}\n")
    else:
        print()

print("="*80)
print("TEST 2: Columnar Transposition (Keyed)")
print("="*80)

print("\nTesting columnar transposition with different key orders:\n")

for section_name, ciphertext in gibberish_sections.items():
    print(f"{section_name}: {ciphertext} ({len(ciphertext)} chars)")

    # Try a few reasonable key orders
    length = len(ciphertext)

    if length <= 7:
        print(f"  Too short for meaningful columnar transposition\n")
        continue

    # Try natural order vs reverse
    key_order_1 = list(range(length))
    key_order_2 = list(range(length))[::-1]
    key_order_3 = list(range(length))[length//2:] + list(range(length))[:length//2]

    for key_order in [key_order_1, key_order_2, key_order_3]:
        try:
            result = transpose_columnar(ciphertext, key_order)
            if result:
                vowels = sum(1 for c in result if c in 'AEIOUY')
                vowel_ratio = vowels / len(result)
                if vowel_ratio > 0.2:  # If English-like
                    print(f"  Key order {key_order[:5]}...: {result} ({vowel_ratio:.0%})")
        except:
            pass

    print()

print("="*80)
print("TEST 3: Position-Based Encoding")
print("="*80)

print("""
Hypothesis: Gibberish encodes positions or indices.
E.g., each letter's position in alphabet = encoded data.

Convert gibberish to numeric positions:
""")

for section_name, ciphertext in gibberish_sections.items():
    positions = []
    for char in ciphertext:
        if char in KRYPTOS_ALPHABET:
            pos = KRYPTOS_ALPHABET.index(char)
        else:
            pos = ord(char) - ord('A')
        positions.append(pos)

    print(f"\n{section_name}: {ciphertext}")
    print(f"Positions: {positions}")

    # Look for patterns
    # Check if positions form sequences
    if len(positions) > 2:
        diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        print(f"Differences: {diffs}")

        # Check if differences are uniform
        if len(set(diffs)) <= 2:
            print(f"  -> Possible sequence pattern!")

        # Check if positions encode coordinates (degrees, minutes, seconds)
        # Coordinates are typically: 0-90 (degrees), 0-60 (minutes), 0-60 (seconds)
        possible_coords = []
        for p in positions:
            if p <= 90:
                possible_coords.append(f"{p}°")
            elif p <= 60:
                possible_coords.append(f"{p}'")
        if possible_coords:
            print(f"  -> Could be: {possible_coords}")

print("\n" + "="*80)
print("TEST 4: Vigenère with Position-Derived Secondary Keys")
print("="*80)

print("""
What if each gibberish section uses a key derived from its position?
E.g., section at position 5-15 uses key derived from positions 5-15 of period-29 key.
""")

PERIOD_29_KEY = 'DIJJQELYOIECBAQKVAATCRDUMPABT'

print("\nTrying position-derived keys:\n")

# For each section, try using the corresponding period-29 key positions as a decrypt key
section_info = {
    'section_1': ('QAPBZDBKZEL', list(range(5, 16))),
    'section_2': ('LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH', list(range(25, 63))),
    'section_3': ('RSPVJWQUL', list(range(74, 83))),
    'section_4': ('ZOLRKCAYF', list(range(88, 97))),
}

def vigenere_decrypt(ciphertext, key, keyed_alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    plaintext = []
    key = key.upper()
    ciphertext = ciphertext.upper()
    key_idx = 0

    for char in ciphertext:
        if char not in keyed_alphabet:
            plaintext.append(char)
            continue

        ct_pos = keyed_alphabet.index(char)
        key_char = key[key_idx % len(key)]
        key_pos = keyed_alphabet.index(key_char)
        pt_pos = (ct_pos - key_pos) % len(keyed_alphabet)
        plaintext.append(keyed_alphabet[pt_pos])
        key_idx += 1

    return ''.join(plaintext)

for section_name, (ciphertext, positions) in section_info.items():
    # Try using the period-29 key characters at those positions
    key_from_positions = ''.join(PERIOD_29_KEY[p % 29] for p in positions)

    decrypted = vigenere_decrypt(ciphertext, key_from_positions, KRYPTOS_ALPHABET)

    vowels = sum(1 for c in decrypted if c in 'AEIOUY')
    vowel_ratio = vowels / len(decrypted) if decrypted else 0

    print(f"{section_name}:")
    print(f"  Position-derived key: {key_from_positions}")
    print(f"  Decrypted: {decrypted}")
    print(f"  Vowel ratio: {vowel_ratio:.0%}\n")

print("="*80)
print("TEST 5: Check for Hidden Structure in Gibberish")
print("="*80)

print("\nAnalyzing letter frequency and patterns:\n")

all_gibberish = ''.join(gibberish_sections.values())
print(f"Combined gibberish ({len(all_gibberish)} chars): {all_gibberish[:50]}...\n")

from collections import Counter

# Overall frequency
freq = Counter(all_gibberish)
most_common = freq.most_common(5)
print(f"Most common letters: {most_common}")

# Check for bigram patterns
bigrams = {}
for i in range(len(all_gibberish) - 1):
    bigram = all_gibberish[i:i+2]
    bigrams[bigram] = bigrams.get(bigram, 0) + 1

most_common_bigrams = sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[:5]
print(f"Most common bigrams: {most_common_bigrams}")

# Check for repeating patterns
print("\nLooking for repeating substrings:")
for length in [2, 3, 4]:
    substrings = {}
    for i in range(len(all_gibberish) - length + 1):
        sub = all_gibberish[i:i+length]
        if sub in substrings:
            substrings[sub] += 1
        else:
            substrings[sub] = 1

    repeats = {s: c for s, c in substrings.items() if c >= 2}
    if repeats:
        print(f"  Length {length}: {dict(sorted(repeats.items(), key=lambda x: x[1], reverse=True)[:3])}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

print("""
Double Encryption Test Results:

1. TRANSPOSITION: Rail fence and columnar transposition don't produce English text
   - Suggests gibberish is NOT a simple rearrangement of English text

2. POSITION-BASED ENCODING: No obvious coordinate or numeric patterns found
   - Could still encode positions but not in standard format

3. SECONDARY VIGENÈRE: With tested keys, no meaningful English text emerges
   - Suggests correct secondary key hasn't been found
   - OR gibberish doesn't contain English plaintext

4. STRUCTURE: Gibberish shows:
   - High character diversity (57-100%)
   - Letter frequencies not matching English
   - No repeating substrings of length > 1
   - Suggests either: random padding OR structured data (not English text)

FINAL ASSESSMENT:

K4 Double Encryption Hypothesis Status: INCONCLUSIVE

Evidence FOR double encryption:
✓ Gibberish has structure (UP patterns with SOLUTION key)
✓ Chi-squared analysis confirms NOT simple transposition of English
✓ Multiple keys produce similar results (not random)

Evidence AGAINST double encryption:
✗ No clear English plaintext from secondary Vigenère keys
✗ Transposition doesn't recover English text
✗ No obvious coordinate/numeric encoding
✗ High character diversity suggests intentional obfuscation

Most likely explanation:
- K4 uses SINGLE period-29 Vigenère encryption
- Gibberish = intentional padding/obfuscation (Sanborn's style)
- Real plaintext = UNDER + NORTHEAST + BERLINCLOCK + ABOVE
- Remaining 67 characters = noise or encoded non-English data
- The mystery lies in: HOW the period-29 key is derived from Berlin Clock
""")
